from flask import Blueprint, request, jsonify, send_from_directory, Response
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from ..extensions import db
from ..models import EditorUser, DynamicPage, SiteConfig
import os
import time
import uuid
import json
from werkzeug.utils import secure_filename

editor_bp = Blueprint('editor', __name__)

# 资源存储目录
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'editor-assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
FILES_DIR = os.path.join(ASSETS_DIR, 'files')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}


def editor_required(f):
    """装饰器：验证 editor 或 admin JWT"""
    from functools import wraps
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') not in ('editor', 'admin'):
            return jsonify({"code": 403, "msg": "仅编辑器或管理员账号可访问"}), 403
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@editor_bp.route('/login', methods=['POST'])
def login():
    """编辑器登录"""
    data = request.get_json()
    account = (data.get('account') or '').strip()
    password = data.get('password') or ''

    if not account or not password:
        return jsonify({"code": 400, "msg": "请输入账号和密码"}), 400

    editor = EditorUser.query.filter_by(account=account).first()
    if not editor or not check_password_hash(editor.password, password):
        return jsonify({"code": 401, "msg": "账号或密码错误"}), 401

    access_token = create_access_token(
        identity=str(editor.id),
        additional_claims={'role': 'editor', 'account': editor.account}
    )

    return jsonify({
        "code": 200,
        "msg": "登录成功",
        "data": {
            "token": access_token,
            "account": editor.account,
            "role": editor.role
        }
    })


@editor_bp.route('/check-token', methods=['GET'])
@editor_required
def check_token():
    """验证 token 是否有效"""
    claims = get_jwt()
    return jsonify({
        "code": 200,
        "data": {
            "account": claims.get('account', ''),
            "role": claims.get('role', '')
        }
    })


# ============ 页面管理 ============

@editor_bp.route('/site/pages', methods=['GET'])
@editor_required
def get_pages():
    """获取所有可编辑页面列表（自动创建默认页面骨架，不含任何模拟数据）"""
    # 默认页面列表（只创建框架，不填充任何HTML/CSS模拟数据）
    default_pages = {
        'home': '首页',
        'about': '关于我们',
        'achievement': '成果中心',
        'demand': '需求中心',
        'expert': '专家中心',
        'partner': '合作伙伴',
        'finance': '金融服务'
    }

    # 仅创建页面骨架，html/css 均为空 — 第一次使用时通过 iframe 从 dist 捕获真实内容
    for path, name in default_pages.items():
        existing = DynamicPage.query.filter_by(page_path=path).first()
        if not existing:
            page = DynamicPage(
                page_path=path,
                page_name=name,
                html_content='',
                css_content=''
            )
            db.session.add(page)
    db.session.commit()

    # 清理旧模板数据：清除没有 gjs_data（即用户从未编辑过）的页面中的 html/css
    # 这些是之前自动填充的演示数据，用户要求全部删除，仅保留真实网页内容
    stale_pages = DynamicPage.query.filter(
        DynamicPage.gjs_data.is_(None),
        (DynamicPage.html_content != '') | (DynamicPage.css_content != '')
    ).all()
    for p in stale_pages:
        p.html_content = ''
        p.css_content = ''
    if stale_pages:
        db.session.commit()

    pages = DynamicPage.query.order_by(DynamicPage.updated_at.desc()).all()
    return jsonify({
        "code": 200,
        "data": [{
            "id": p.id,
            "page_path": p.page_path,
            "page_name": p.page_name,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            "created_at": p.created_at.isoformat() if p.created_at else None
        } for p in pages]
    })


@editor_bp.route('/site/pages', methods=['POST'])
@editor_required
def create_page():
    """创建新页面"""
    data = request.get_json()
    page_path = (data.get('page_path') or '').strip()
    page_name = (data.get('page_name') or '').strip()
    html_content = data.get('html_content', '')
    css_content = data.get('css_content', '')
    gjs_data = data.get('gjs_data', '')

    if not page_path or not page_name:
        return jsonify({"code": 400, "msg": "页面路径和名称不能为空"}), 400

    # 检查路径是否已存在
    existing = DynamicPage.query.filter_by(page_path=page_path).first()
    if existing:
        return jsonify({"code": 400, "msg": f"页面路径 '{page_path}' 已存在"}), 400

    page = DynamicPage(
        page_path=page_path,
        page_name=page_name,
        html_content=html_content,
        css_content=css_content,
        gjs_data=gjs_data
    )
    db.session.add(page)
    db.session.commit()

    return jsonify({"code": 200, "msg": "页面已创建", "data": {"id": page.id}})


@editor_bp.route('/site/pages/<int:page_id>', methods=['GET'])
@editor_required
def get_page(page_id):
    """获取单个页面完整数据（含 GrapesJS 数据）"""
    page = DynamicPage.query.get(page_id)
    if not page:
        return jsonify({"code": 404, "msg": "页面不存在"}), 404

    return jsonify({
        "code": 200,
        "data": {
            "id": page.id,
            "page_path": page.page_path,
            "page_name": page.page_name,
            "html_content": page.html_content or '',
            "css_content": page.css_content or '',
            "gjs_data": page.gjs_data or '',
            "updated_at": page.updated_at.isoformat() if page.updated_at else None,
            "created_at": page.created_at.isoformat() if page.created_at else None
        }
    })


@editor_bp.route('/site/pages/<int:page_id>', methods=['PUT'])
@editor_required
def update_page(page_id):
    """更新页面内容"""
    page = DynamicPage.query.get(page_id)
    if not page:
        return jsonify({"code": 404, "msg": "页面不存在"}), 404

    data = request.get_json()
    if 'page_name' in data:
        page.page_name = (data['page_name'] or '').strip()
    if 'page_path' in data:
        new_path = (data['page_path'] or '').strip()
        dup = DynamicPage.query.filter(DynamicPage.page_path == new_path, DynamicPage.id != page_id).first()
        if dup:
            return jsonify({"code": 400, "msg": f"页面路径 '{new_path}' 已被使用"}), 400
        page.page_path = new_path
    if 'html_content' in data:
        page.html_content = data['html_content']
    if 'css_content' in data:
        page.css_content = data['css_content']
    if 'gjs_data' in data:
        page.gjs_data = data['gjs_data']

    db.session.commit()
    return jsonify({"code": 200, "msg": "页面已更新"})


@editor_bp.route('/site/pages/<int:page_id>', methods=['DELETE'])
@editor_required
def delete_page(page_id):
    """删除页面"""
    page = DynamicPage.query.get(page_id)
    if not page:
        return jsonify({"code": 404, "msg": "页面不存在"}), 404

    db.session.delete(page)
    db.session.commit()
    return jsonify({"code": 200, "msg": "页面已删除"})



@editor_bp.route('/site/pages/<path:page_path>/view', methods=['GET'])
def view_page(page_path):
    """公开接口：访问已发布的页面"""
    page = DynamicPage.query.filter_by(page_path=page_path).first()
    if not page or not page.html_content:
        return jsonify({"code": 404, "msg": "页面不存在或未发布"}), 404

    css = page.css_content or ''
    html = page.html_content or ''

    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page.page_name}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; line-height:1.5715; }}
		a {{ text-decoration: none; color: inherit; }}
		a:hover {{ text-decoration: underline; }}
/* ===== GrapesJS 滚动动画系统 ===== */
/* 在编辑器中给元素添加 CSS 类名即可触发动画（通过 GrapesJS 右侧样式面板 → 类名） */
/* 可选延迟：animate-delay-1 到 animate-delay-5 */

.animate-fade-in, .animate-fade-left, .animate-fade-right, .animate-scale-in {{
  opacity: 0;
  visibility: visible;
  transition: opacity 0.8s ease, transform 0.8s ease !important;
}}
.animate-fade-in  {{ transform: translateY(40px); }}
.animate-fade-left  {{ transform: translateX(-50px); }}
.animate-fade-right {{ transform: translateX(50px); }}
.animate-scale-in  {{ transform: scale(0.9); }}

.animate-fade-in.visible, .animate-fade-left.visible,
.animate-fade-right.visible, .animate-scale-in.visible {{
  opacity: 1;
  transform: translate(0) scale(1);
}}

/* 延迟变体 */
.animate-delay-1.visible {{ transition-delay: 0.15s !important; }}
.animate-delay-2.visible {{ transition-delay: 0.30s !important; }}
.animate-delay-3.visible {{ transition-delay: 0.45s !important; }}
.animate-delay-4.visible {{ transition-delay: 0.60s !important; }}
.animate-delay-5.visible {{ transition-delay: 0.75s !important; }}

/* 页面加载时顶部元素直接显示（避免首屏空白闪烁） */
@media (prefers-reduced-motion: reduce) {{
  .animate-fade-in, .animate-fade-left, .animate-fade-right, .animate-scale-in {{
    opacity: 1; transform: none; transition: none !important;
  }}
}}
{css}
</style>
</head>
<body>
{html}
<script>
(function() {{
  // === 自适应高度 ===
  function reportHeight() {{
    var h = Math.max(
      document.documentElement.scrollHeight,
      document.body.scrollHeight,
      document.documentElement.offsetHeight,
      document.body.offsetHeight
    );
    window.parent.postMessage({{ type: 'page-height', height: h }}, '*');
  }}

  // === 动态注入动画类名（与编辑器内容解耦，编辑不会破坏动画） ===
  function injectAnimationClasses() {{
    var skipTags = {{ script:1, style:1, link:1, meta:1, noscript:1, title:1, base:1 }};
    var children = document.body.children;
    var count = 0;
    for (var i = 0; i < children.length; i++) {{
      var el = children[i];
      if (skipTags[el.tagName.toLowerCase()]) continue;
      // 已有动画类名则跳过（避免重复注入）
      if (el.classList.contains('animate-fade-in') ||
          el.classList.contains('animate-fade-left') ||
          el.classList.contains('animate-fade-right') ||
          el.classList.contains('animate-scale-in')) continue;
      el.classList.add('animate-fade-in');
      if (count < 5) {{
        el.classList.add('animate-delay-' + (count + 1));
      }}
      count++;
    }}
  }}

  function getAnimated() {{
    return document.querySelectorAll(
      '.animate-fade-in, .animate-fade-left, .animate-fade-right, .animate-scale-in'
    );
  }}

  // === 滚动动画（基于父窗口视口检测） ===
  function checkVisibility() {{
    var frameEl = window.frameElement;
    var frameTop = 0;
    if (frameEl) {{
      frameTop = frameEl.getBoundingClientRect().top;
    }} else {{
      // 回退：通过 window.parent 计算 iframe 位置
      try {{
        var iframes = window.parent.document.querySelectorAll('iframe');
        for (var i = 0; i < iframes.length; i++) {{
          if (iframes[i].contentWindow === window) {{
            frameTop = iframes[i].getBoundingClientRect().top;
            break;
          }}
        }}
      }} catch(e) {{}}
    }}
    var parentHeight = window.parent.innerHeight;
    var count = 0;
    getAnimated().forEach(function(el) {{
      if (el.classList.contains('visible')) return;
      var elTop = el.getBoundingClientRect().top + frameTop;
      if (elTop < parentHeight - 60) {{
        el.classList.add('visible');
        count++;
      }}
    }});
    return count;
  }}

	  // === 修复内部链接：设置 target="_parent" 防止在 iframe 内跳转 ===
	  function fixInternalLinks() {{
	    var links = document.querySelectorAll('a[href^="/"]');
	    for (var i = 0; i < links.length; i++) {{
	      if (!links[i].getAttribute('target')) {{
	        links[i].setAttribute('target', '_parent');
	      }}
	    }}
	  }}

	  // === 页面加载完成后延迟执行（确保布局稳定） ===
	  window.addEventListener('load', function() {{
	    fixInternalLinks();
	    injectAnimationClasses();
	    reportHeight();
	    checkVisibility();
	    setTimeout(function() {{ reportHeight(); checkVisibility(); }}, 200);
	    setTimeout(function() {{ reportHeight(); checkVisibility(); }}, 600);
	    setTimeout(function() {{ reportHeight(); checkVisibility(); }}, 1200);
	  }});

  // 监听父窗口的滚动和尺寸变化
  window.parent.addEventListener('scroll', checkVisibility, {{ passive: true }});
  window.parent.addEventListener('resize', function() {{
    reportHeight();
    checkVisibility();
  }});

  // DOM 变化时更新
  if (window.MutationObserver) {{
    new MutationObserver(function() {{
      reportHeight();
      checkVisibility();
    }}).observe(document.body, {{ childList: true, subtree: true, attributes: true }});
  }}

  // 图片加载后更新
  document.addEventListener('load', function(e) {{
    if (e.target.tagName === 'IMG') {{ reportHeight(); checkVisibility(); }}
  }}, true);
}})();
</script>
</body>
</html>'''
    return full_html, 200, {'Content-Type': 'text/html; charset=utf-8'}


@editor_bp.route('/import/default', methods=['GET'])
def import_default_template():
    """获取当前网站构建后的 index.html 作为编辑起始模板"""
    # 尝试多个可能的 dist 路径
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', 'dist', 'index.html'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dist', 'index.html'),
    ]
    for p in possible_paths:
        abs_path = os.path.abspath(p)
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({"code": 200, "data": {"html": content}})
    return jsonify({"code": 404, "msg": "未找到构建文件，请先执行 npm run build"})


# ============ 资源管理 ============

@editor_bp.route('/upload', methods=['POST'])
@editor_required
def upload_file():
    """上传图片/文件到资源目录"""
    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "未选择文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "msg": "文件名为空"}), 400

    if not allowed_file(file.filename):
        return jsonify({"code": 400, "msg": "不支持的文件类型"}), 400

    # 判断文件类型
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext in {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'ico'}:
        sub_dir = 'images'
    else:
        sub_dir = 'files'

    target_dir = os.path.join(ASSETS_DIR, sub_dir)
    os.makedirs(target_dir, exist_ok=True)

    # 生成唯一文件名
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_name = f"{name}_{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
    file_path = os.path.join(target_dir, unique_name)
    file.save(file_path)

    file_url = f"/static/editor-assets/{sub_dir}/{unique_name}"

    return jsonify({
        "code": 200,
        "msg": "上传成功",
        "data": {
            "url": file_url,
            "filename": unique_name,
            "original_name": file.filename,
            "size": os.path.getsize(file_path),
            "type": sub_dir
        }
    })


@editor_bp.route('/assets', methods=['GET'])
@editor_required
def list_assets():
    """列出所有已上传的资源文件"""
    assets = []

    for sub_dir in ['images', 'files']:
        target_dir = os.path.join(ASSETS_DIR, sub_dir)
        if not os.path.exists(target_dir):
            continue
        for fname in os.listdir(target_dir):
            fpath = os.path.join(target_dir, fname)
            if os.path.isfile(fpath):
                assets.append({
                    "url": f"/static/editor-assets/{sub_dir}/{fname}",
                    "filename": fname,
                    "size": os.path.getsize(fpath),
                    "type": sub_dir,
                    "updated_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(fpath)))
                })

    # 按修改时间倒序
    assets.sort(key=lambda a: a['updated_at'], reverse=True)

    return jsonify({"code": 200, "data": assets})


@editor_bp.route('/assets/<path:filename>', methods=['DELETE'])
@editor_required
def delete_asset(filename):
    """删除资源文件"""
    for sub_dir in ['images', 'files']:
        fpath = os.path.join(ASSETS_DIR, sub_dir, filename)
        if os.path.exists(fpath):
            os.remove(fpath)
            return jsonify({"code": 200, "msg": "已删除"})

    return jsonify({"code": 404, "msg": "文件不存在"}), 404


# ============ 站点全局配置 API ============

@editor_bp.route('/config/all', methods=['GET'])
def get_all_configs():
    """获取所有站点配置（公开，供前端展示使用）"""
    configs = SiteConfig.query.all()
    config_dict = {c.config_key: c.config_value for c in configs}

    # 解析 JSON 字段
    for key in ['nav_menu', 'carousel_images', 'about_content']:
        if key in config_dict and config_dict[key]:
            try:
                config_dict[key] = json.loads(config_dict[key])
            except (json.JSONDecodeError, TypeError):
                if key == 'nav_menu':
                    config_dict[key] = []
                elif key == 'carousel_images':
                    config_dict[key] = []
                elif key == 'about_content':
                    config_dict[key] = {}
    return jsonify({'code': 200, 'data': config_dict})


@editor_bp.route('/config/update', methods=['POST'])
@jwt_required()
def update_configs():
    """更新站点配置（管理员权限）"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"code": 403, "msg": "仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    for key, value in data.items():
        # JSON 字段序列化存储
        if isinstance(value, (list, dict)):
            str_value = json.dumps(value, ensure_ascii=False)
        else:
            str_value = str(value) if value is not None else ''

        config = SiteConfig.query.filter_by(config_key=key).first()
        if config:
            config.config_value = str_value
        else:
            new_cfg = SiteConfig(config_key=key, config_value=str_value)
            db.session.add(new_cfg)

    db.session.commit()
    return jsonify({'code': 200, 'message': '配置更新成功'})


# ============ 站点配置图片上传 API ============

# 上传目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(APP_DIR)
UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'uploads', 'site_config')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@editor_bp.route('/upload/image', methods=['POST'])
@jwt_required()
def upload_site_image():
    """上传站点配置图片（Logo、轮播图等）"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"code": 403, "msg": "仅管理员可操作"}), 403

    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未找到文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '文件为空'})

    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'ico'}:
        return jsonify({'code': 400, 'message': '仅支持图片格式'})

    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    image_url = f"/api/editor/uploads/site_config/{filename}"
    return jsonify({
        'code': 200,
        'data': {'url': image_url},
        'message': '上传成功'
    })


@editor_bp.route('/uploads/<path:filename>', methods=['GET'])
def get_uploaded_file(filename):
    """提供上传的图片文件访问"""
    uploads_dir = os.path.join(ROOT_DIR, 'uploads')
    return send_from_directory(uploads_dir, filename)
