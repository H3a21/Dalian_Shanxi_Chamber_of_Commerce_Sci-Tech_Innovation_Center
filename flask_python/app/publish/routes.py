"""
成果和需求发布路由
"""
import os
import re
from flask import Blueprint, request, jsonify, g, send_from_directory
from ..publish_service import PublishService, CooperationService
from ..models import User, Message, AuditLog
from ..mongo_models import Expert, Partner, Achievement, Requirement, Session, AgentStatus, Cooperation, VisitLog
from ..extensions import db, get_mongodb
from datetime import datetime, timedelta
import functools
from ..socket_events import emit_new_message_event

publish_bp = Blueprint('publish', __name__)

# 安全文件名：去除路径遍历风险，保留 Unicode（含中文）
def safe_filename(filename):
    filename = filename.replace('\\', '/').rsplit('/', 1)[-1]
    filename = re.sub(r'[\x00-\x1f\x7f:*?"<>|]', '', filename)
    if not filename or filename == '.':
        filename = f"unnamed_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return filename

# Token验证装饰器（从chat/routes.py复制，确保独立可用）
def token_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # 放行 OPTIONS 请求
        if request.method == 'OPTIONS':
            return '', 200

        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:].strip()
        elif 'token' in request.args:
            token = request.args.get('token')

        if not token:
            return jsonify({"code": 401, "msg": "缺少访问令牌"}), 401

        if token.startswith('user_token_'):
            try:
                parts = token.split('_')
                if len(parts) >= 3:
                    user_id = int(parts[2])
                    user = User.query.get(user_id)
                    if user:
                        if user.status != 1:
                            return jsonify({"code": 401, "msg": "账号已被禁用"}), 401
                        g.user_id = user_id
                        return f(*args, **kwargs)
                    else:
                        return jsonify({"code": 401, "msg": "用户不存在"}), 401
                else:
                    return jsonify({"code": 401, "msg": "无效的token格式"}), 401
            except (ValueError, IndexError):
                return jsonify({"code": 401, "msg": "token解析失败"}), 401

        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, exceptions
            verify_jwt_in_request()
            g.user_id = int(get_jwt_identity())
            try:
                user = User.query.get(g.user_id)
                if user and user.status != 1:
                    return jsonify({"code": 401, "msg": "账号已被禁用"}), 401
            except Exception:
                pass
            return f(*args, **kwargs)
        except exceptions.JWTExtendedException:
            return jsonify({"code": 401, "msg": "JWT token无效或已过期"}), 401
    return decorated_function


# 健康检查
@publish_bp.route('/health', methods=['GET'])
def publish_health():
    return jsonify({"code": 200, "msg": "发布模块正常"})


# 提交成果
@publish_bp.route('/achievement', methods=['POST', 'OPTIONS'])
@token_required
def create_achievement():
    """创建成果记录"""
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    # 调试：打印接收到的数据
    print(f"[DEBUG] create_achievement route: 接收到的数据 = {data}")
    print(f"[DEBUG] create_achievement route: transformTypes = {data.get('transformTypes')}, type = {type(data.get('transformTypes'))}")

    # 调用服务层创建成果
    achievement = PublishService.create_achievement(user_id, data)
    if not achievement:
        return jsonify({"code": 500, "msg": "成果保存失败"}), 500

    # 通知提交者 + 通知管理员
    try:
        submitter_msg = Message(
            send_user_id=0,
            receive_user_id=user_id,
            msg_type='result',
            biz_type='achievement',
            biz_id=achievement.achievement_code,
            title='成果提交确认',
            content=f'您刚才提交的「{achievement.achievement_name}」正在审核中，我们将于1~3个工作日内审核完毕',
            is_read=0,
            create_time=datetime.now()
        )
        db.session.add(submitter_msg)
        admin_users = User.query.filter_by(role='admin').all()
        for admin in admin_users:
            db.session.add(Message(
                send_user_id=0,
                receive_user_id=admin.id,
                msg_type='result',
                biz_type='achievement',
                biz_id=achievement.achievement_code,
                title='新的成果审核待处理',
                content=f'有新的成果「{achievement.achievement_name}」审核待您处理',
                is_read=0,
                create_time=datetime.now()
            ))
        db.session.commit()

        # 实时推送通知
        try:
            emit_new_message_event(user_id, {
                'id': submitter_msg.id,
                'title': submitter_msg.title,
                'content': submitter_msg.content,
                'msg_type': submitter_msg.msg_type,
                'create_time': submitter_msg.create_time.strftime('%Y-%m-%d %H:%M:%S') if submitter_msg.create_time else ''
            })
            for admin in admin_users:
                emit_new_message_event(admin.id, {
                    'id': 0,  # 前端不需要准确的id来更新列表，会重新fetch
                    'title': '新的成果审核待处理',
                    'content': f'有新的成果「{achievement.achievement_name}」审核待您处理',
                    'msg_type': 'result',
                    'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        except Exception as e:
            print(f"[WARN] 推送成果提交通知失败: {e}")
    except Exception as e:
        print(f"[WARN] 创建成果提交通知消息失败: {e}")
        db.session.rollback()

    return jsonify({
        "code": 200,
        "msg": "成果提交成功",
        "data": {
            "id": str(achievement._id),
            "achievement_code": achievement.achievement_code,
            "achievement_name": achievement.achievement_name,
            "status": achievement.status,
            "created_at": achievement.created_at.isoformat() if achievement.created_at else None
        }
    })


# 更新已驳回的成果并重新提交
@publish_bp.route('/achievement/<achievement_id>', methods=['PUT'])
@token_required
def update_achievement(achievement_id):
    """更新已驳回的成果内容并重新提交审核"""
    user_id = g.user_id
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    # 验证成果属于当前用户
    achievement = PublishService.get_achievement_by_id(achievement_id)
    if not achievement:
        return jsonify({"code": 404, "msg": "成果不存在"}), 404
    if str(achievement.user_id) != str(user_id):
        return jsonify({"code": 403, "msg": "无权修改此成果"}), 403
    if achievement.status != 'rejected':
        return jsonify({"code": 400, "msg": "仅驳回状态的成果可以修改"}), 400

    updated = PublishService.update_achievement(achievement_id, data)
    if not updated:
        return jsonify({"code": 500, "msg": "更新失败"}), 500

    return jsonify({
        "code": 200,
        "msg": "成果已更新并重新提交审核",
        "data": {
            "id": str(updated._id),
            "achievement_code": updated.achievement_code,
            "achievement_name": updated.achievement_name,
            "status": updated.status
        }
    })


# 提交需求
@publish_bp.route('/requirement', methods=['POST', 'OPTIONS'])
@token_required
def create_requirement():
    """创建需求记录"""
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    # 调用服务层创建需求
    requirement = PublishService.create_requirement(user_id, data)
    if not requirement:
        return jsonify({"code": 500, "msg": "需求保存失败"}), 500

    # 通知提交者 + 通知管理员
    try:
        submitter_msg = Message(
            send_user_id=0,
            receive_user_id=user_id,
            msg_type='result',
            biz_type='demand',
            biz_id=requirement.demand_code,
            title='需求提交确认',
            content=f'您刚才提交的「{requirement.demand_name}」正在审核中，我们将于1~3个工作日内审核完毕',
            is_read=0,
            create_time=datetime.now()
        )
        db.session.add(submitter_msg)
        admin_users = User.query.filter_by(role='admin').all()
        for admin in admin_users:
            db.session.add(Message(
                send_user_id=0,
                receive_user_id=admin.id,
                msg_type='result',
                biz_type='demand',
                biz_id=requirement.demand_code,
                title='新的需求审核待处理',
                content=f'有新的需求「{requirement.demand_name}」审核待您处理',
                is_read=0,
                create_time=datetime.now()
            ))
        db.session.commit()

        # 实时推送通知
        try:
            emit_new_message_event(user_id, {
                'id': submitter_msg.id,
                'title': submitter_msg.title,
                'content': submitter_msg.content,
                'msg_type': submitter_msg.msg_type,
                'create_time': submitter_msg.create_time.strftime('%Y-%m-%d %H:%M:%S') if submitter_msg.create_time else ''
            })
            for admin in admin_users:
                emit_new_message_event(admin.id, {
                    'id': 0,
                    'title': '新的需求审核待处理',
                    'content': f'有新的需求「{requirement.demand_name}」审核待您处理',
                    'msg_type': 'result',
                    'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        except Exception as e:
            print(f"[WARN] 推送需求提交通知失败: {e}")
    except Exception as e:
        print(f"[WARN] 创建需求提交通知消息失败: {e}")
        db.session.rollback()

    return jsonify({
        "code": 200,
        "msg": "需求提交成功",
        "data": {
            "id": str(requirement._id),
            "demand_code": requirement.demand_code,
            "demand_name": requirement.demand_name,
            "status": requirement.status,
            "created_at": requirement.created_at.isoformat() if requirement.created_at else None
        }
    })


# 更新已驳回的需求并重新提交
@publish_bp.route('/requirement/<requirement_id>', methods=['PUT'])
@token_required
def update_requirement(requirement_id):
    """更新已驳回的需求内容并重新提交审核"""
    user_id = g.user_id
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    # 验证需求属于当前用户
    requirement = PublishService.get_requirement_by_id(requirement_id)
    if not requirement:
        return jsonify({"code": 404, "msg": "需求不存在"}), 404
    if str(requirement.user_id) != str(user_id):
        return jsonify({"code": 403, "msg": "无权修改此需求"}), 403
    if requirement.status != 'rejected':
        return jsonify({"code": 400, "msg": "仅驳回状态的需求可以修改"}), 400

    updated = PublishService.update_requirement(requirement_id, data)
    if not updated:
        return jsonify({"code": 500, "msg": "更新失败"}), 500

    return jsonify({
        "code": 200,
        "msg": "需求已更新并重新提交审核",
        "data": {
            "id": str(updated._id),
            "demand_code": updated.demand_code,
            "demand_name": updated.demand_name,
            "status": updated.status
        }
    })


# 获取用户成果列表
@publish_bp.route('/achievements', methods=['GET'])
@token_required
def get_achievements():
    """获取用户提交的成果列表"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 5, type=int)
    offset = (page - 1) * page_size
    status_filter = request.args.get('status', '').strip()

    if status_filter:
        achievements = PublishService.get_user_achievements(user_id, page_size, offset, status=status_filter)
        all_achievements = PublishService.get_user_achievements(user_id, limit=0, status=status_filter)
    else:
        achievements = PublishService.get_user_achievements(user_id, page_size, offset, exclude_rejected=True)
        all_achievements = PublishService.get_user_achievements(user_id, limit=0, exclude_rejected=True)
    total = len(all_achievements)

    result = []
    for achievement in achievements:
        result.append({
            "id": str(achievement._id),
            "achievement_code": achievement.achievement_code,
            "achievement_name": achievement.achievement_name,
            "owner": achievement.owner,
            "tech_fields": achievement.tech_fields,
            "tech_maturity": achievement.tech_maturity,
            "status": achievement.status,
            "reject_reason": getattr(achievement, 'reject_reason', ''),
            "is_display": getattr(achievement, 'is_display', False),
            "created_at": achievement.created_at.isoformat() if achievement.created_at else None,
            "updated_at": achievement.updated_at.isoformat() if achievement.updated_at else None
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


# 获取用户需求列表
@publish_bp.route('/requirements', methods=['GET'])
@token_required
def get_requirements():
    """获取用户提交的需求列表"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 5, type=int)
    offset = (page - 1) * page_size
    status_filter = request.args.get('status', '').strip()

    if status_filter:
        requirements = PublishService.get_user_requirements(user_id, page_size, offset, status=status_filter)
        all_requirements = PublishService.get_user_requirements(user_id, limit=0, status=status_filter)
    else:
        requirements = PublishService.get_user_requirements(user_id, page_size, offset, exclude_rejected=True)
        all_requirements = PublishService.get_user_requirements(user_id, limit=0, exclude_rejected=True)
    total = len(all_requirements)

    result = []
    for requirement in requirements:
        result.append({
            "id": str(requirement._id),
            "demand_code": requirement.demand_code,
            "demand_name": requirement.demand_name,
            "company_name": requirement.company_name,
            "tech_fields": requirement.tech_fields,
            "tech_fields_other": requirement.tech_fields_other or "",
            "demand_types": requirement.demand_types or [],
            "demand_types_other": requirement.demand_types_other or "",
            "region": requirement.region or {},
            "description": {
                "overview": requirement.description.get("overview", ""),
                "target_problems": requirement.description.get("target_problems", ""),
                "budget": requirement.description.get("budget", 0)
            },
            "status": requirement.status,
            "reject_reason": getattr(requirement, 'reject_reason', ''),
            "created_at": requirement.created_at.isoformat() if requirement.created_at else None,
            "updated_at": requirement.updated_at.isoformat() if requirement.updated_at else None
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


# 获取用户被驳回的成果列表
@publish_bp.route('/rejected_achievements', methods=['GET'])
@token_required
def get_rejected_achievements():
    """获取当前用户被驳回的成果列表"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 5, type=int)
    offset = (page - 1) * page_size

    achievements = PublishService.get_user_rejected_achievements(user_id, page_size, offset)

    all_rejected = PublishService.get_user_rejected_achievements(user_id, limit=0)
    total = len(all_rejected)

    result = []
    for achievement in achievements:
        result.append({
            "id": str(achievement._id),
            "achievement_code": achievement.achievement_code,
            "achievement_name": achievement.achievement_name,
            "owner": achievement.owner,
            "tech_fields": achievement.tech_fields,
            "tech_fields_other": getattr(achievement, "tech_fields_other", "") or "",
            "tech_maturity": achievement.tech_maturity,
            "status": achievement.status,
            "reject_reason": getattr(achievement, 'reject_reason', ''),
            "is_display": getattr(achievement, 'is_display', False),
            "created_at": achievement.created_at.isoformat() if achievement.created_at else None,
            "updated_at": achievement.updated_at.isoformat() if achievement.updated_at else None
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


# 获取用户被驳回的需求列表
@publish_bp.route('/rejected_requirements', methods=['GET'])
@token_required
def get_rejected_requirements():
    """获取当前用户被驳回的需求列表"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 5, type=int)
    offset = (page - 1) * page_size

    requirements = PublishService.get_user_rejected_requirements(user_id, page_size, offset)

    all_rejected = PublishService.get_user_rejected_requirements(user_id, limit=0)
    total = len(all_rejected)

    result = []
    for requirement in requirements:
        result.append({
            "id": str(requirement._id),
            "demand_code": requirement.demand_code,
            "demand_name": requirement.demand_name,
            "company_name": requirement.company_name,
            "tech_fields": requirement.tech_fields,
            "tech_fields_other": requirement.tech_fields_other,
            "status": requirement.status,
            "reject_reason": getattr(requirement, 'reject_reason', ''),
            "created_at": requirement.created_at.isoformat() if requirement.created_at else None,
            "updated_at": requirement.updated_at.isoformat() if requirement.updated_at else None
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


# 获取待审核成果列表（管理员专用）
@publish_bp.route('/pending_achievements', methods=['GET'])
@token_required
def get_pending_achievements():
    """获取待审核的成果列表，仅管理员可访问"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    # 检查用户角色是否为管理员
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可访问"}), 403

    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 5, type=int)  # 默认每页5条

    # 计算偏移量
    offset = (page - 1) * page_size

    # 获取待审核成果
    achievements = PublishService.get_pending_achievements(limit=page_size, offset=offset)

    result = []
    for achievement in achievements:
        result.append({
            "id": str(achievement._id),
            "achievement_code": achievement.achievement_code,
            "achievement_name": achievement.achievement_name,
            "owner": achievement.owner,
            "tech_fields": achievement.tech_fields,
            "tech_fields_other": achievement.tech_fields_other or '',
            "tech_maturity": achievement.tech_maturity,
            "transfer_methods": achievement.transfer_methods,
            "transfer_methods_other": achievement.transfer_methods_other or '',
            "status": achievement.status,
            "created_at": achievement.created_at.isoformat() if achievement.created_at else None,
            "updated_at": achievement.updated_at.isoformat() if achievement.updated_at else None
        })

    # 获取待审核成果总数（用于分页）
    all_pending = PublishService.get_pending_achievements(limit=0)  # limit=0表示获取所有
    total = len(all_pending)

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


# 获取单个成果详情
@publish_bp.route('/achievement/<achievement_id>', methods=['GET'])
@token_required
def get_achievement_detail(achievement_id):
    """获取单个成果详情"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    # 调用服务层获取成果详情
    achievement = PublishService.get_achievement_by_id(achievement_id)
    if not achievement:
        return jsonify({"code": 404, "msg": "成果不存在"}), 404

    # 构建响应数据，映射字段名以匹配前端期望
    # 注意：这里需要根据前端字段名调整
    # 处理地区字符串
    province = achievement.region.get('province', '')
    city = achievement.region.get('city', '')
    region_str = province
    if city and city != province:  # 避免重复（如"北京市北京市"）
        region_str = f"{province}{city}"

    # 处理期望完成日期
    expected_date = achievement.transfer_preference.get('expected_complete_date', {})
    year = expected_date.get('year', 0)
    month = expected_date.get('month', 0)
    expected_completion_date = ''
    if year > 0 and month > 0:
        expected_completion_date = f"{year}年{month}月前"
    else:
        expected_completion_date = '____年____月前'

    # collaborationPreferences使用transfer_methods，因为前端期望数组
    collaboration_preferences = achievement.transfer_methods or []

    data = {
        "id": str(achievement._id),
        "title": achievement.achievement_name,
        "achievementNumber": achievement.achievement_code,
        "holder": achievement.owner,
        "region": region_str,
        "technologyFields": achievement.tech_fields or [],
        "otherTechnologyField": achievement.tech_fields_other or '',
        "maturity": achievement.tech_maturity or '',
        "transferMethods": achievement.transfer_methods or [],
        "otherTransferMethod": achievement.transfer_methods_other or '',
        "summary": achievement.description.get('summary', ''),
        "innovationLevel": achievement.description.get('innovation_level', ''),
        "advantages": achievement.description.get('advantages', ''),
        "coreTechnicalIndicators": achievement.description.get('core_indicators', ''),
        "intellectualProperties": achievement.description.get('intellectual_property', ''),
        "collaborationPreferences": collaboration_preferences,
        "techTransferFee": achievement.transfer_preference.get('tech_transfer', {}).get('expected_fee', 0),
        "licenseType": achievement.transfer_preference.get('tech_license', {}).get('type', ''),
        "techValuation": achievement.transfer_preference.get('tech_investment', {}).get('valuation', 0),
        "equityPercentage": achievement.transfer_preference.get('tech_investment', {}).get('share_ratio', 0),
        "otherCollaborationPreference": achievement.transfer_preference.get('other', ''),
        "expectedCompletionDate": expected_completion_date,
        "status": achievement.status,
        "reject_reason": getattr(achievement, 'reject_reason', ''),
        "is_display": getattr(achievement, 'is_display', False),
        "created_at": achievement.created_at.isoformat() if achievement.created_at else None,
        "updated_at": achievement.updated_at.isoformat() if achievement.updated_at else None,
        # 原始字段，方便前端直接使用
        "user_id": achievement.user_id,
        "achievement_name": achievement.achievement_name,
        "owner": achievement.owner,
        "achievement_code": achievement.achievement_code,
        "tech_fields": achievement.tech_fields or [],
        "tech_fields_other": achievement.tech_fields_other or '',
        "tech_maturity": achievement.tech_maturity or '',
        "transfer_methods": achievement.transfer_methods or [],
        "transfer_methods_other": achievement.transfer_methods_other or '',
        "description": {
            "summary": achievement.description.get('summary', ''),
            "innovation_level": achievement.description.get('innovation_level', ''),
            "advantages": achievement.description.get('advantages', ''),
            "core_indicators": achievement.description.get('core_indicators', ''),
            "intellectual_property": achievement.description.get('intellectual_property', '')
        },
        "transfer_preference": {
            "tech_transfer": achievement.transfer_preference.get('tech_transfer', {}),
            "tech_license": achievement.transfer_preference.get('tech_license', {}),
            "tech_investment": achievement.transfer_preference.get('tech_investment', {}),
            "cooperation_dev": achievement.transfer_preference.get('cooperation_dev', False),
            "other": achievement.transfer_preference.get('other', ''),
            "preferred_method": achievement.transfer_preference.get('preferred_method', ''),
            "expected_complete_date": achievement.transfer_preference.get('expected_complete_date', {})
        },
        "region": achievement.region or {},
        "expected_completion_date": expected_completion_date
    }

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": data
    })


# 审核成果（通过/拒绝）
@publish_bp.route('/achievement/<achievement_id>/review', methods=['POST'])
@token_required
def review_achievement(achievement_id):
    """审核成果，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    # 检查用户角色是否为管理员
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    status = data.get('status')
    if status not in ['approved', 'rejected']:
        return jsonify({"code": 400, "msg": "无效的状态，必须是'approved'或'rejected'"}), 400

    reason = data.get('reason', '')  # 拒绝理由，通过时可空

    # 调用服务层更新状态
    achievement = PublishService.update_achievement_status(achievement_id, status, user_id)
    if not achievement:
        return jsonify({"code": 404, "msg": "成果不存在或更新失败"}), 404

    # 保存驳回原因到成果文档
    if status == 'rejected' and reason:
        achievement.reject_reason = reason
        achievement.save()

    biz_code = achievement.achievement_code  # 如 CG2025001

    # 写入审核记录表 audit_logs
    try:
        audit_log = AuditLog(
            biz_type='achievement',
            biz_id=biz_code,
            admin_id=user_id,
            result=1 if status == 'approved' else 0,
            reason=reason if status == 'rejected' else None,
            create_time=datetime.now()
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"[WARN] 写入审核记录失败: {e}")
        db.session.rollback()

    # 自动生成审核结果通知
    try:
        if status == 'approved':
            msg_content = f"您提交的成果「{achievement.achievement_name}」已经通过审核"
        else:
            reason_text = f"，原因：{reason}" if reason else ""
            msg_content = f"您提交的成果「{achievement.achievement_name}」已被驳回{reason_text}。请前往「个人中心->我的待办」页面，根据原因进行修改后继续提交进行审核"
        msg = Message(
            send_user_id=0,
            receive_user_id=achievement.user_id,
            msg_type='result',
            biz_type='achievement',
            biz_id=biz_code,
            title='成果审核结果通知',
            content=msg_content,
            is_read=0,
            create_time=datetime.now()
        )
        db.session.add(msg)
        db.session.commit()

        # 实时推送审核结果通知
        try:
            emit_new_message_event(achievement.user_id, {
                'id': msg.id,
                'title': msg.title,
                'content': msg.content,
                'msg_type': msg.msg_type,
                'create_time': msg.create_time.strftime('%Y-%m-%d %H:%M:%S') if msg.create_time else ''
            })
        except Exception as e:
            print(f"[WARN] 推送成果审核结果通知失败: {e}")
    except Exception as e:
        print(f"[WARN] 创建审核消息失败: {e}")

    return jsonify({
        "code": 200,
        "msg": f"成果审核{'通过' if status == 'approved' else '拒绝'}成功",
        "data": {
            "id": str(achievement._id),
            "achievement_code": achievement.achievement_code,
            "achievement_name": achievement.achievement_name,
            "status": achievement.status,
            "reviewer_id": achievement.reviewer_id,
            "reviewed_at": achievement.reviewed_at.isoformat() if achievement.reviewed_at else None
        }
    })


# 获取待审核需求列表（管理员专用）
@publish_bp.route('/pending_requirements', methods=['GET'])
@token_required
def get_pending_requirements():
    """获取待审核的需求列表，仅管理员可访问"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    # 检查用户角色是否为管理员
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可访问"}), 403

    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 5, type=int)  # 默认每页5条

    # 计算偏移量
    offset = (page - 1) * page_size

    # 获取待审核需求
    requirements = PublishService.get_pending_requirements(limit=page_size, offset=offset)

    result = []
    for requirement in requirements:
        result.append({
            "id": str(requirement._id),
            "demand_code": requirement.demand_code,
            "demand_name": requirement.demand_name,
            "company_name": requirement.company_name,
            "region": requirement.region,
            "tech_fields": requirement.tech_fields,
            "tech_fields_other": requirement.tech_fields_other or '',
            "demand_types": requirement.demand_types,
            "demand_types_other": requirement.demand_types_other or '',
            "description": {
                "overview": requirement.description.get('overview', ''),
                "target_problems": requirement.description.get('target_problems', ''),
                "budget": requirement.description.get('budget', 0)
            },
            "status": requirement.status,
            "created_at": requirement.created_at.isoformat() if requirement.created_at else None,
            "updated_at": requirement.updated_at.isoformat() if requirement.updated_at else None
        })

    # 获取待审核需求总数（用于分页）
    all_pending = PublishService.get_pending_requirements(limit=0)  # limit=0表示获取所有
    total = len(all_pending)

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


# 获取单个需求详情
@publish_bp.route('/requirement/<requirement_id>', methods=['GET'])
@token_required
def get_requirement_detail(requirement_id):
    """获取单个需求详情"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    # 调用服务层获取需求详情
    requirement = PublishService.get_requirement_by_id(requirement_id)
    if not requirement:
        return jsonify({"code": 404, "msg": "需求不存在"}), 404

    # 构建响应数据
    data = {
        "id": str(requirement._id),
        "user_id": requirement.user_id,
        "demand_name": requirement.demand_name,
        "demand_code": requirement.demand_code,
        "company_name": requirement.company_name,
        "region": requirement.region or {},
        "tech_fields": requirement.tech_fields or [],
        "tech_fields_other": requirement.tech_fields_other or '',
        "demand_types": requirement.demand_types or [],
        "demand_types_other": requirement.demand_types_other or '',
        "description": {
            "overview": requirement.description.get('overview', ''),
            "target_problems": requirement.description.get('target_problems', ''),
            "budget": requirement.description.get('budget', 0)
        },
        "status": requirement.status,
        "reject_reason": getattr(requirement, 'reject_reason', ''),
        "reviewer_id": requirement.reviewer_id,
        "reviewed_at": requirement.reviewed_at.isoformat() if requirement.reviewed_at else None,
        "created_at": requirement.created_at.isoformat() if requirement.created_at else None,
        "updated_at": requirement.updated_at.isoformat() if requirement.updated_at else None,
        "match_status": getattr(requirement, 'match_status', '待对接'),
        "is_display": getattr(requirement, 'is_display', False)
    }

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": data
    })


# 审核需求（通过/拒绝）
@publish_bp.route('/requirement/<requirement_id>/review', methods=['POST'])
@token_required
def review_requirement(requirement_id):
    """审核需求，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    # 检查用户角色是否为管理员
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    status = data.get('status')
    if status not in ['approved', 'rejected']:
        return jsonify({"code": 400, "msg": "无效的状态，必须是'approved'或'rejected'"}), 400

    reason = data.get('reason', '')  # 拒绝理由，通过时可空

    # 调用服务层更新状态
    requirement = PublishService.update_requirement_status(requirement_id, status, user_id)
    if not requirement:
        return jsonify({"code": 404, "msg": "需求不存在或更新失败"}), 404

    # 保存驳回原因到需求文档
    if status == 'rejected' and reason:
        requirement.reject_reason = reason
        requirement.save()

    biz_code = requirement.demand_code  # 如 XQ2025001

    # 写入审核记录表 audit_logs
    try:
        audit_log = AuditLog(
            biz_type='demand',
            biz_id=biz_code,
            admin_id=user_id,
            result=1 if status == 'approved' else 0,
            reason=reason if status == 'rejected' else None,
            create_time=datetime.now()
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"[WARN] 写入审核记录失败: {e}")
        db.session.rollback()

    # 自动生成审核结果通知
    try:
        if status == 'approved':
            msg_content = f"您提交的需求「{requirement.demand_name}」已经通过审核"
        else:
            reason_text = f"，原因：{reason}" if reason else ""
            msg_content = f"您提交的需求「{requirement.demand_name}」已被驳回{reason_text}。请前往「个人中心->我的待办」页面，根据原因进行修改后继续提交进行审核"
        msg = Message(
            send_user_id=0,
            receive_user_id=requirement.user_id,
            msg_type='result',
            biz_type='demand',
            biz_id=biz_code,
            title='需求审核结果通知',
            content=msg_content,
            is_read=0,
            create_time=datetime.now()
        )
        db.session.add(msg)
        db.session.commit()

        # 实时推送审核结果通知
        try:
            emit_new_message_event(requirement.user_id, {
                'id': msg.id,
                'title': msg.title,
                'content': msg.content,
                'msg_type': msg.msg_type,
                'create_time': msg.create_time.strftime('%Y-%m-%d %H:%M:%S') if msg.create_time else ''
            })
        except Exception as e:
            print(f"[WARN] 推送需求审核结果通知失败: {e}")
    except Exception as e:
        print(f"[WARN] 创建审核消息失败: {e}")

    return jsonify({
        "code": 200,
        "msg": f"需求审核{'通过' if status == 'approved' else '拒绝'}成功",
        "data": {
            "id": str(requirement._id),
            "demand_code": requirement.demand_code,
            "demand_name": requirement.demand_name,
            "status": requirement.status,
            "reviewer_id": requirement.reviewer_id,
            "reviewed_at": requirement.reviewed_at.isoformat() if requirement.reviewed_at else None
        }
    })
# 切换成果主页展示状态（仅管理员）
@publish_bp.route('/achievement/<achievement_id>/display', methods=['POST'])
@token_required
def toggle_achievement_display(achievement_id):
    """切换成果是否在主页展示"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    # 权限校验：仅管理员可操作
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data or 'is_display' not in data:
        return jsonify({"code": 400, "msg": "缺少 is_display 参数"}), 400

    # 提取布尔值
    is_display = data.get('is_display')
    if not isinstance(is_display, bool):
        # 兼容一下前端可能传来的字符串 'true' / 'false'
        is_display = str(is_display).lower() == 'true'

    # 限制最多展示3个
    if is_display:
        displayed = Achievement.find(is_display=True)
        # 排除自身
        displayed = [d for d in displayed if str(d._id) != achievement_id]
        if len(displayed) >= 3:
            return jsonify({"code": 400, "msg": "成果最多只能展示3个，请先取消其他成果的展示"}), 400

    # 调用 Service 更新
    achievement = PublishService.toggle_achievement_display(achievement_id, is_display)
    if not achievement:
        return jsonify({"code": 404, "msg": "成果不存在或更新失败"}), 404

    return jsonify({
        "code": 200,
        "msg": f"成果展示状态已更新为：{'展示' if is_display else '隐藏'}",
        "data": {
            "id": str(achievement._id),
            "achievement_code": achievement.achievement_code,
            "is_display": achievement.is_display
        }
    })


# 切换需求主页展示状态（仅管理员）
@publish_bp.route('/requirement/<requirement_id>/display', methods=['POST'])
@token_required
def toggle_requirement_display(requirement_id):
    """切换需求是否在主页展示"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    # 权限校验：仅管理员可操作
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data or 'is_display' not in data:
        return jsonify({"code": 400, "msg": "缺少 is_display 参数"}), 400

    is_display = data.get('is_display')
    if not isinstance(is_display, bool):
        is_display = str(is_display).lower() == 'true'

    # 限制最多展示3个
    if is_display:
        displayed = Requirement.find(is_display=True)
        # 排除自身
        displayed = [d for d in displayed if str(d._id) != requirement_id]
        if len(displayed) >= 3:
            return jsonify({"code": 400, "msg": "需求最多只能展示3个，请先取消其他需求的展示"}), 400

    # 调用 Service 更新
    requirement = PublishService.toggle_requirement_display(requirement_id, is_display)
    if not requirement:
        return jsonify({"code": 404, "msg": "需求不存在或更新失败"}), 404

    return jsonify({
        "code": 200,
        "msg": f"需求展示状态已更新为：{'展示' if is_display else '隐藏'}",
        "data": {
            "id": str(requirement._id),
            "demand_code": requirement.demand_code,
            "is_display": requirement.is_display
        }
    })


# ==========================================
# 专家管理 API（仅管理员）
# ==========================================

@publish_bp.route('/experts', methods=['GET'])
@token_required
def get_experts():
    """获取专家列表（分页），所有登录用户可访问"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str)
    domain = request.args.get('domain', '', type=str)
    offset = (page - 1) * page_size

    experts = PublishService.get_experts(limit=page_size, offset=offset)

    # 研究方向过滤
    if domain.strip() and domain != '全部':
        kw = domain.lower()
        experts = [e for e in experts if
                   e.professional_fields and
                   any(kw in (f or '').lower() for f in e.professional_fields)]

    # 关键词搜索过滤
    if keyword.strip():
        kw = keyword.lower()
        experts = [e for e in experts if
                   kw in (e.name or '').lower() or
                   kw in (e.work_unit or '').lower() or
                   kw in (e.position_title or '').lower() or
                   any(kw in (f or '').lower() for f in (e.professional_fields or []))]

    all_experts = PublishService.get_experts(limit=0)
    total = len(all_experts)

    result = []
    for expert in experts:
        result.append({
            "id": str(expert._id),
            "name": expert.name,
            "gender": expert.gender,
            "highest_education": expert.highest_education,
            "school_major": expert.school_major,
            "work_unit": expert.work_unit,
            "position_title": expert.position_title,
            "professional_fields": expert.professional_fields,
            "contact": expert.contact,
            "honors": expert.honors,
            "technical_title": expert.technical_title,
            "personal_profile": expert.personal_profile,
            "professional_certification": expert.professional_certification,
            "foreign_language": expert.foreign_language,
            "work_years": expert.work_years,
            "successful_cases": expert.successful_cases,
            "patents": expert.patents,
            "publications": expert.publications,
            "research_projects": expert.research_projects,
            "awards": expert.awards,
            "attachments": expert.attachments,
            "created_at": expert.created_at.isoformat() if expert.created_at else None,
            "updated_at": expert.updated_at.isoformat() if expert.updated_at else None,
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


@publish_bp.route('/experts', methods=['POST'])
@token_required
def create_expert():
    """创建专家，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    if not data.get('name'):
        return jsonify({"code": 400, "msg": "专家姓名不能为空"}), 400

    # 检查身份证号是否已存在
    id_card = data.get('id_card', '')
    if id_card:
        existing = Expert.find_one(id_card=id_card)
        if existing:
            return jsonify({"code": 400, "msg": "身份证号已存在"}), 400

    expert = PublishService.create_expert(data)
    if not expert:
        return jsonify({"code": 500, "msg": "专家保存失败"}), 500

    return jsonify({
        "code": 200,
        "msg": "专家创建成功",
        "data": {"id": str(expert._id), "name": expert.name}
    })


@publish_bp.route('/experts/<expert_id>', methods=['GET'])
@token_required
def get_expert_detail(expert_id):
    """获取单个专家详情，所有登录用户可访问"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    expert = PublishService.get_expert_by_id(expert_id)
    if not expert:
        return jsonify({"code": 404, "msg": "专家不存在"}), 404

    data = {
        "id": str(expert._id),
        "name": expert.name,
        "gender": expert.gender,
        "id_card": expert.id_card,
        "highest_education": expert.highest_education,
        "school_major": expert.school_major,
        "work_unit": expert.work_unit,
        "position_title": expert.position_title,
        "contact": expert.contact,
        "address": expert.address,
        "honors": expert.honors,
        "professional_fields": expert.professional_fields,
        "professional_fields_other": expert.professional_fields_other,
        "technical_title": expert.technical_title,
        "professional_certification": expert.professional_certification,
        "foreign_language": expert.foreign_language,
        "work_years": expert.work_years,
        "successful_cases": expert.successful_cases,
        "patents": expert.patents,
        "publications": expert.publications,
        "research_projects": expert.research_projects,
        "awards": expert.awards,
        "personal_profile": expert.personal_profile,
        "attachments": expert.attachments,
        "created_at": expert.created_at.isoformat() if expert.created_at else None,
        "updated_at": expert.updated_at.isoformat() if expert.updated_at else None
    }

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": data
    })


@publish_bp.route('/experts/<expert_id>', methods=['PUT'])
@token_required
def update_expert(expert_id):
    """更新专家信息，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    # 检查身份证号是否已被其他专家使用
    id_card = data.get('id_card', '')
    if id_card:
        existing = Expert.find_one(id_card=id_card)
        if existing and str(existing._id) != expert_id:
            return jsonify({"code": 400, "msg": "身份证号已存在"}), 400

    expert = PublishService.update_expert(expert_id, data)
    if not expert:
        return jsonify({"code": 404, "msg": "专家不存在或更新失败"}), 404

    return jsonify({
        "code": 200,
        "msg": "专家更新成功",
        "data": {"id": str(expert._id), "name": expert.name}
    })


@publish_bp.route('/experts/<expert_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_expert(expert_id):
    """删除专家，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    success = PublishService.delete_expert(expert_id)
    if not success:
        return jsonify({"code": 404, "msg": "专家不存在或删除失败"}), 404

    return jsonify({
        "code": 200,
        "msg": "专家删除成功"
    })


# ==========================================
# 专家附件上传 API
# ==========================================

EXPERTS_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'experts_images')

# 附件类型（固定6项）
ATTACHMENT_TYPES = [
    '身份证件复印件', '近期生活照或职业照一张', '学历学位证书',
    '职称证明', '代表性成果证明', '其他证明材料'
]

# 提供专家附件的静态文件访问
@publish_bp.route('/experts/attachments/<path:filename>', methods=['GET'])
def serve_expert_attachment(filename):
    """提供专家附件文件的静态访问"""
    return send_from_directory(EXPERTS_IMAGES_DIR, filename)


@publish_bp.route('/experts/<expert_id>/upload', methods=['POST'])
@token_required
def upload_expert_attachment(expert_id):
    """上传专家附件文件"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    expert = PublishService.get_expert_by_id(expert_id)
    if not expert:
        return jsonify({"code": 404, "msg": "专家不存在"}), 404

    attachment_type = request.form.get('attachment_type', '')
    if attachment_type not in ATTACHMENT_TYPES:
        return jsonify({"code": 400, "msg": f"无效的附件类型: {attachment_type}"}), 400

    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "没有上传文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "msg": "文件名为空"}), 400

    # 创建文件夹: experts_images/{expert_name}/{attachment_type}/
    expert_name = expert.name or '未知专家'
    folder_path = os.path.join(EXPERTS_IMAGES_DIR, expert_name, attachment_type)
    os.makedirs(folder_path, exist_ok=True)

    # 保存文件（添加时间戳前缀防止重名）
    original_name = safe_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = f"{timestamp}_{original_name}"
    file_path = os.path.join(folder_path, file_name)
    file.save(file_path)

    # 构建访问URL
    relative_path = f"{expert_name}/{attachment_type}/{file_name}"
    file_url = f"/api/publish/experts/attachments/{relative_path}"

    # 更新专家文档中的附件记录
    PublishService.add_expert_attachment(expert_id, attachment_type, {
        'file_name': file_name,
        'file_path': relative_path,
        'file_url': file_url
    })

    return jsonify({
        "code": 200,
        "msg": "上传成功",
        "data": {
            "file_name": file_name,
            "file_url": file_url,
            "attachment_type": attachment_type
        }
    })


@publish_bp.route('/experts/<expert_id>/attachments', methods=['DELETE'])
@token_required
def delete_expert_attachment(expert_id):
    """删除专家附件文件"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    expert = PublishService.get_expert_by_id(expert_id)
    if not expert:
        return jsonify({"code": 404, "msg": "专家不存在"}), 404

    attachment_type = request.args.get('attachment_type', '')
    file_name = request.args.get('file_name', '')

    if not attachment_type or not file_name:
        return jsonify({"code": 400, "msg": "缺少参数"}), 400

    # 从专家文档的附件记录中找到匹配项的 file_path，用于删除物理文件
    # 必须使用 file_path 而非 expert.name 拼接，因为专家姓名可能已修改
    file_path_to_delete = None
    if hasattr(expert, 'attachments') and expert.attachments:
        files = expert.attachments.get(attachment_type, [])
        for f in files:
            if f.get('file_name') == file_name:
                file_path_to_delete = f.get('file_path')
                break

    if file_path_to_delete:
        full_path = os.path.join(EXPERTS_IMAGES_DIR, file_path_to_delete)
        if os.path.exists(full_path):
            os.remove(full_path)
    else:
        # 兼容旧路径：用当前专家名拼接（附件记录可能没有 file_path）
        expert_name = expert.name or '未知专家'
        legacy_path = os.path.join(EXPERTS_IMAGES_DIR, expert_name, attachment_type, file_name)
        if os.path.exists(legacy_path):
            os.remove(legacy_path)

    # 更新专家文档
    PublishService.remove_expert_attachment(expert_id, attachment_type, file_name)

    return jsonify({"code": 200, "msg": "删除成功"})


# ==========================================
# 主页公开接口（无需登录 token_required）
# ==========================================

# 获取主页公开展示的成果
@publish_bp.route('/public/achievements', methods=['GET'])
def get_public_achievements():
    """获取主页展示的成果（卡片展示版）"""
    # 默认拉取6条，适合前端卡片排版
    limit = request.args.get('limit', 6, type=int)
    achievements = PublishService.get_public_achievements(limit=limit)

    result = []
    for achievement in achievements:
        # 只返回主页卡片需要的核心字段，避免数据冗余和敏感信息泄露
        region = achievement.region or {}
        if isinstance(region, dict):
            province = region.get('province', '') or ''
            city = region.get('city', '') or ''
            region_str = (province + ' ' + city).strip()
        else:
            region_str = str(region)

        transfer_methods = achievement.transfer_methods or []
        if isinstance(transfer_methods, (list, tuple)):
            transfer_str = ', '.join(str(t) for t in transfer_methods[:2])
        else:
            transfer_str = str(transfer_methods)

        result.append({
            "id": str(achievement._id),
            "achievement_code": achievement.achievement_code,
            "achievement_name": achievement.achievement_name,
            "owner": achievement.owner,
            "tech_fields": achievement.tech_fields,
            "tech_fields_other": achievement.tech_fields_other or '',
            "tech_maturity": achievement.tech_maturity,
            "region": region_str,
            "transfer_methods": transfer_str,
            "transfer_methods_other": achievement.transfer_methods_other or '',
            "summary": achievement.description.get('summary', '') if hasattr(achievement, 'description') and isinstance(achievement.description, dict) else '',
            "created_at": achievement.created_at.isoformat() if hasattr(achievement, 'created_at') and achievement.created_at else None
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result
    })


# 获取主页公开展示的需求
@publish_bp.route('/public/requirements', methods=['GET'])
def get_public_requirements():
    """获取主页展示的需求（卡片展示版）"""
    limit = request.args.get('limit', 6, type=int)
    requirements = PublishService.get_public_requirements(limit=limit)

    result = []
    for req in requirements:
        region = req.region or {}
        if isinstance(region, dict):
            province = region.get('province', '') or ''
            city = region.get('city', '') or ''
            region_str = (province + ' ' + city).strip()
        else:
            region_str = str(region)

        result.append({
            "id": str(req._id),
            "demand_code": req.demand_code,
            "demand_name": req.demand_name,
            "company_name": req.company_name,
            "tech_fields": req.tech_fields,
            "tech_fields_other": req.tech_fields_other or '',
            "demand_types": req.demand_types,
            "demand_types_other": req.demand_types_other or '',
            "region": region_str,
            "budget": req.description.get('budget', 0) if hasattr(req, 'description') and isinstance(req.description, dict) else 0,
            "created_at": req.created_at.isoformat() if hasattr(req, 'created_at') and req.created_at else None
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result
    })


# 获取成果中心所有已审核的成果
@publish_bp.route('/public/achievements/center', methods=['GET'])
def get_center_achievements():
    """获取成果中心展示的所有已审核成果"""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    achievements = PublishService.get_all_approved_achievements(limit=limit, offset=offset)

    result = []
    for achievement in achievements:
        # 构建地区字符串（安全处理：可能是dict、string或None）
        region = achievement.region or {}
        if isinstance(region, dict):
            province = region.get('province', '') or ''
            city = region.get('city', '') or ''
            region_str = (province + ' ' + city).strip()
        else:
            region_str = str(region)

        result.append({
            "id": str(achievement._id),
            "achievement_code": achievement.achievement_code,
            "achievement_name": achievement.achievement_name,
            "owner": achievement.owner,
            "region": region_str,
            "tech_fields": achievement.tech_fields,
            "tech_fields_other": achievement.tech_fields_other or '',
            "tech_maturity": achievement.tech_maturity,
            "transfer_methods": achievement.transfer_methods,
            "transfer_methods_other": achievement.transfer_methods_other or '',
            "transfer_preference": achievement.transfer_preference if hasattr(achievement, 'transfer_preference') and isinstance(achievement.transfer_preference, dict) else {},
            "summary": achievement.description.get('summary', '') if hasattr(achievement, 'description') and isinstance(achievement.description, dict) else '',
            "advantages": achievement.description.get('advantages', '') if hasattr(achievement, 'description') and isinstance(achievement.description, dict) else '',
            "innovation_level": achievement.description.get('innovation_level', '') if hasattr(achievement, 'description') and isinstance(achievement.description, dict) else '',
            "core_indicators": achievement.description.get('core_indicators', '') if hasattr(achievement, 'description') and isinstance(achievement.description, dict) else '',
            "intellectual_property": achievement.description.get('intellectual_property', '') if hasattr(achievement, 'description') and isinstance(achievement.description, dict) else '',
            "created_at": achievement.created_at.isoformat() if hasattr(achievement, 'created_at') and achievement.created_at else None
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": len(result),
        "limit": limit,
        "offset": offset
    })


# 获取需求中心所有已审核的需求
@publish_bp.route('/public/requirements/center', methods=['GET'])
def get_center_requirements():
    """获取需求中心展示的所有已审核需求"""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    requirements = PublishService.get_all_approved_requirements(limit=limit, offset=offset)

    result = []
    for req in requirements:
        # 构建地区字符串（安全处理：可能是dict、string或None）
        region = req.region or {}
        if isinstance(region, dict):
            province = region.get('province', '') or ''
            city = region.get('city', '') or ''
            region_str = (province + ' ' + city).strip()
        else:
            region_str = str(region)

        result.append({
            "id": str(req._id),
            "demand_code": req.demand_code,
            "demand_name": req.demand_name,
            "company_name": req.company_name,
            "region": region_str,
            "tech_fields": req.tech_fields,
            "tech_fields_other": req.tech_fields_other or '',
            "demand_types": req.demand_types,
            "demand_types_other": req.demand_types_other or '',
            "overview": req.description.get('overview', '') if hasattr(req, 'description') and isinstance(req.description, dict) else '',
            "target_problems": req.description.get('target_problems', '') if hasattr(req, 'description') and isinstance(req.description, dict) else '',
            "budget": req.description.get('budget', 0) if hasattr(req, 'description') and isinstance(req.description, dict) else 0,
            "created_at": req.created_at.isoformat() if hasattr(req, 'created_at') and req.created_at else None,
            "match_status": getattr(req, 'match_status', '待对接')
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": len(result),
        "limit": limit,
        "offset": offset
    })


# ==========================================
# 合作伙伴管理 API（仅管理员）
# ==========================================

PARTNERS_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'partners_images')


@publish_bp.route('/partners/attachments/<path:filename>', methods=['GET'])
def serve_partner_image(filename):
    """提供合作伙伴图片的静态访问"""
    return send_from_directory(PARTNERS_IMAGES_DIR, filename)


@publish_bp.route('/partners', methods=['GET'])
@token_required
def get_partners():
    """获取合作伙伴列表（分页），管理员可查看全部信息"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str)
    type_filter = request.args.get('type', '', type=str)
    offset = (page - 1) * page_size

    partners = PublishService.get_partners(limit=page_size, offset=offset, type_filter=type_filter if type_filter else None)

    if keyword.strip():
        kw = keyword.lower()
        partners = [p for p in partners if
                    kw in (p.name or '').lower() or
                    kw in (p.address or '').lower() or
                    kw in (p.industry or '').lower() or
                    kw in (p.contact or '').lower()]

    all_partners = PublishService.get_partners(limit=0, type_filter=type_filter if type_filter else None)
    total = len(all_partners)

    result = []
    for p in partners:
        result.append({
            "id": str(p._id),
            "name": p.name,
            "type": p.type,
            "address": p.address,
            "industry": p.industry,
            "intro": p.intro,
            "services": p.services,
            "contact": p.contact if user.role == 'admin' else '',
            "images": p.images,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


@publish_bp.route('/partners', methods=['POST'])
@token_required
def create_partner():
    """创建合作伙伴，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    if not data.get('name'):
        return jsonify({"code": 400, "msg": "平台名称不能为空"}), 400

    partner = PublishService.create_partner(data)
    if not partner:
        return jsonify({"code": 500, "msg": "合作伙伴保存失败"}), 500

    return jsonify({
        "code": 200,
        "msg": "合作伙伴创建成功",
        "data": {"id": str(partner._id), "name": partner.name}
    })


@publish_bp.route('/partners/<partner_id>', methods=['GET'])
@token_required
def get_partner_detail(partner_id):
    """获取单个合作伙伴详情"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    partner = PublishService.get_partner_by_id(partner_id)
    if not partner:
        return jsonify({"code": 404, "msg": "合作伙伴不存在"}), 404

    data = {
        "id": str(partner._id),
        "name": partner.name,
        "type": partner.type,
        "address": partner.address,
        "industry": partner.industry,
        "intro": partner.intro,
        "services": partner.services,
        "contact": partner.contact,
        "images": partner.images,
        "created_at": partner.created_at.isoformat() if partner.created_at else None,
        "updated_at": partner.updated_at.isoformat() if partner.updated_at else None
    }

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": data
    })


@publish_bp.route('/partners/<partner_id>', methods=['PUT'])
@token_required
def update_partner(partner_id):
    """更新合作伙伴信息，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    partner = PublishService.update_partner(partner_id, data)
    if not partner:
        return jsonify({"code": 404, "msg": "合作伙伴不存在或更新失败"}), 404

    return jsonify({
        "code": 200,
        "msg": "合作伙伴更新成功",
        "data": {"id": str(partner._id), "name": partner.name}
    })


@publish_bp.route('/partners/<partner_id>', methods=['DELETE'])
@token_required
def delete_partner(partner_id):
    """删除合作伙伴，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    success = PublishService.delete_partner(partner_id)
    if not success:
        return jsonify({"code": 404, "msg": "合作伙伴不存在或删除失败"}), 404

    return jsonify({
        "code": 200,
        "msg": "合作伙伴删除成功"
    })


@publish_bp.route('/partners/<partner_id>/upload', methods=['POST'])
@token_required
def upload_partner_image(partner_id):
    """上传合作伙伴图片"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    partner = PublishService.get_partner_by_id(partner_id)
    if not partner:
        return jsonify({"code": 404, "msg": "合作伙伴不存在"}), 404

    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "没有上传文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "msg": "文件名为空"}), 400

    # 创建文件夹: partners_images/{partner_name}/
    partner_name = partner.name or '未知合作方'
    folder_path = os.path.join(PARTNERS_IMAGES_DIR, partner_name)
    os.makedirs(folder_path, exist_ok=True)

    # 保存文件（添加时间戳前缀防止重名）
    original_name = safe_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = f"{timestamp}_{original_name}"
    file_path = os.path.join(folder_path, file_name)
    file.save(file_path)

    # 构建访问URL
    relative_path = f"{partner_name}/{file_name}"
    file_url = f"/api/publish/partners/attachments/{relative_path}"

    # 更新合作伙伴文档中的图片记录
    PublishService.add_partner_image(partner_id, {
        'file_name': file_name,
        'file_path': relative_path,
        'file_url': file_url
    })

    return jsonify({
        "code": 200,
        "msg": "上传成功",
        "data": {
            "file_name": file_name,
            "file_url": file_url
        }
    })


@publish_bp.route('/partners/<partner_id>/images', methods=['DELETE'])
@token_required
def delete_partner_image(partner_id):
    """删除合作伙伴图片"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    partner = PublishService.get_partner_by_id(partner_id)
    if not partner:
        return jsonify({"code": 404, "msg": "合作伙伴不存在"}), 404

    file_name = request.args.get('file_name', '')
    if not file_name:
        return jsonify({"code": 400, "msg": "缺少 file_name 参数"}), 400

    # 查找物理文件路径并删除
    file_path_to_delete = None
    if hasattr(partner, 'images') and partner.images:
        for f in partner.images:
            if f.get('file_name') == file_name:
                file_path_to_delete = f.get('file_path')
                break

    if file_path_to_delete:
        full_path = os.path.join(PARTNERS_IMAGES_DIR, file_path_to_delete)
        if os.path.exists(full_path):
            os.remove(full_path)

    # 更新合作伙伴文档
    PublishService.remove_partner_image(partner_id, file_name)

    return jsonify({"code": 200, "msg": "删除成功"})


# ==========================================
# 合作伙伴公开接口（无需登录）
# ==========================================

@publish_bp.route('/public/partners', methods=['GET'])
def get_public_partners():
    """获取主页展示的合作伙伴列表（公开接口，不含联系方式）"""
    limit = request.args.get('limit', 50, type=int)
    type_filter = request.args.get('type', '', type=str)

    partners = PublishService.get_partners(limit=limit, offset=0, type_filter=type_filter if type_filter else None)

    result = []
    for p in partners:
        result.append({
            "id": str(p._id),
            "name": p.name,
            "type": p.type,
            "address": p.address,
            "industry": p.industry,
            "intro": p.intro,
            "services": p.services,
            "images": p.images,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result
    })


# ==========================================
# 金融服务机构管理 API（仅管理员）
# ==========================================

FINANCIAL_SERVICES_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'financial_services_images')


@publish_bp.route('/financial-services/attachments/<path:filename>', methods=['GET'])
def serve_financial_service_image(filename):
    """提供金融服务机构图片的静态访问"""
    return send_from_directory(FINANCIAL_SERVICES_IMAGES_DIR, filename)


@publish_bp.route('/financial-services', methods=['GET'])
@token_required
def get_financial_services():
    """获取金融服务机构列表（分页），管理员可查看全部信息"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str)
    offset = (page - 1) * page_size

    fss = PublishService.get_financial_services(limit=page_size, offset=offset)

    if keyword.strip():
        kw = keyword.lower()
        fss = [f for f in fss if
               kw in (f.name or '').lower() or
               kw in (f.intro or '').lower() or
               kw in (f.services or '').lower() or
               kw in (f.contact or '').lower()]

    all_fss = PublishService.get_financial_services(limit=0)
    total = len(all_fss)

    result = []
    for f in fss:
        result.append({
            "id": str(f._id),
            "name": f.name,
            "intro": f.intro,
            "services": f.services,
            "contact": f.contact if user.role == 'admin' else '',
            "images": f.images,
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "updated_at": f.updated_at.isoformat() if f.updated_at else None,
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


@publish_bp.route('/financial-services', methods=['POST'])
@token_required
def create_financial_service():
    """创建金融服务机构，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    if not data.get('name'):
        return jsonify({"code": 400, "msg": "机构名称不能为空"}), 400

    fs = PublishService.create_financial_service(data)
    if not fs:
        return jsonify({"code": 500, "msg": "金融服务机构保存失败"}), 500

    return jsonify({
        "code": 200,
        "msg": "金融服务机构创建成功",
        "data": {"id": str(fs._id), "name": fs.name}
    })


@publish_bp.route('/financial-services/<fs_id>', methods=['GET'])
@token_required
def get_financial_service_detail(fs_id):
    """获取单个金融服务机构详情"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    fs = PublishService.get_financial_service_by_id(fs_id)
    if not fs:
        return jsonify({"code": 404, "msg": "金融服务机构不存在"}), 404

    data = {
        "id": str(fs._id),
        "name": fs.name,
        "intro": fs.intro,
        "services": fs.services,
        "contact": fs.contact,
        "images": fs.images,
        "created_at": fs.created_at.isoformat() if fs.created_at else None,
        "updated_at": fs.updated_at.isoformat() if fs.updated_at else None
    }

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": data
    })


@publish_bp.route('/financial-services/<fs_id>', methods=['PUT'])
@token_required
def update_financial_service(fs_id):
    """更新金融服务机构信息，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    fs = PublishService.update_financial_service(fs_id, data)
    if not fs:
        return jsonify({"code": 404, "msg": "金融服务机构不存在或更新失败"}), 404

    return jsonify({
        "code": 200,
        "msg": "金融服务机构更新成功",
        "data": {"id": str(fs._id), "name": fs.name}
    })


@publish_bp.route('/financial-services/<fs_id>', methods=['DELETE'])
@token_required
def delete_financial_service(fs_id):
    """删除金融服务机构，仅管理员可操作"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    success = PublishService.delete_financial_service(fs_id)
    if not success:
        return jsonify({"code": 404, "msg": "金融服务机构不存在或删除失败"}), 404

    return jsonify({
        "code": 200,
        "msg": "金融服务机构删除成功"
    })


@publish_bp.route('/financial-services/<fs_id>/upload', methods=['POST'])
@token_required
def upload_financial_service_image(fs_id):
    """上传金融服务机构图片"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    fs = PublishService.get_financial_service_by_id(fs_id)
    if not fs:
        return jsonify({"code": 404, "msg": "金融服务机构不存在"}), 404

    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "没有上传文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "msg": "文件名为空"}), 400

    # 创建文件夹: financial_services_images/{机构名称}/
    fs_name = fs.name or '未知机构'
    folder_path = os.path.join(FINANCIAL_SERVICES_IMAGES_DIR, fs_name)
    os.makedirs(folder_path, exist_ok=True)

    # 保存文件（添加时间戳前缀防止重名）
    original_name = safe_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = f"{timestamp}_{original_name}"
    file_path = os.path.join(folder_path, file_name)
    file.save(file_path)

    # 构建访问URL
    relative_path = f"{fs_name}/{file_name}"
    file_url = f"/api/publish/financial-services/attachments/{relative_path}"

    # 更新文档中的图片记录
    PublishService.add_financial_service_image(fs_id, {
        'file_name': file_name,
        'file_path': relative_path,
        'file_url': file_url
    })

    return jsonify({
        "code": 200,
        "msg": "上传成功",
        "data": {
            "file_name": file_name,
            "file_url": file_url
        }
    })


@publish_bp.route('/financial-services/<fs_id>/images', methods=['DELETE'])
@token_required
def delete_financial_service_image(fs_id):
    """删除金融服务机构图片"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    fs = PublishService.get_financial_service_by_id(fs_id)
    if not fs:
        return jsonify({"code": 404, "msg": "金融服务机构不存在"}), 404

    file_name = request.args.get('file_name', '')
    if not file_name:
        return jsonify({"code": 400, "msg": "缺少 file_name 参数"}), 400

    # 查找物理文件路径并删除
    file_path_to_delete = None
    if hasattr(fs, 'images') and fs.images:
        for f in fs.images:
            if f.get('file_name') == file_name:
                file_path_to_delete = f.get('file_path')
                break

    if file_path_to_delete:
        full_path = os.path.join(FINANCIAL_SERVICES_IMAGES_DIR, file_path_to_delete)
        if os.path.exists(full_path):
            os.remove(full_path)

    # 更新文档
    PublishService.remove_financial_service_image(fs_id, file_name)

    return jsonify({"code": 200, "msg": "删除成功"})


# ==========================================
# 金融服务机构公开接口（无需登录）
# ==========================================

@publish_bp.route('/public/financial-services', methods=['GET'])
def get_public_financial_services():
    """获取主页展示的金融服务机构列表（公开接口，不含联系方式）"""
    limit = request.args.get('limit', 50, type=int)

    fss = PublishService.get_financial_services(limit=limit, offset=0)

    result = []
    for f in fss:
        result.append({
            "id": str(f._id),
            "name": f.name,
            "intro": f.intro,
            "services": f.services,
            "images": f.images,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result
    })


@publish_bp.route('/public/experts', methods=['GET'])
def get_public_experts():
    """获取专家列表（公开接口，无需登录）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str)
    domain = request.args.get('domain', '', type=str)
    offset = (page - 1) * page_size

    experts = PublishService.get_experts(limit=page_size, offset=offset)

    # 研究方向过滤
    if domain.strip() and domain != '全部':
        kw = domain.lower()
        experts = [e for e in experts if
                   e.professional_fields and
                   any(kw in (f or '').lower() for f in e.professional_fields)]

    # 关键词搜索过滤
    if keyword.strip():
        kw = keyword.lower()
        experts = [e for e in experts if
                   kw in (e.name or '').lower() or
                   kw in (e.work_unit or '').lower() or
                   kw in (e.position_title or '').lower() or
                   any(kw in (f or '').lower() for f in (e.professional_fields or []))]

    all_experts = PublishService.get_experts(limit=0)
    total = len(all_experts)

    result = []
    for expert in experts:
        result.append({
            "id": str(expert._id),
            "name": expert.name,
            "gender": expert.gender,
            "highest_education": expert.highest_education,
            "school_major": expert.school_major,
            "work_unit": expert.work_unit,
            "position_title": expert.position_title,
            "professional_fields": expert.professional_fields,
            "honors": expert.honors,
            "technical_title": expert.technical_title,
            "personal_profile": expert.personal_profile,
            "professional_certification": expert.professional_certification,
            "foreign_language": expert.foreign_language,
            "work_years": expert.work_years,
            "successful_cases": expert.successful_cases,
            "patents": expert.patents,
            "publications": expert.publications,
            "research_projects": expert.research_projects,
            "awards": expert.awards,
            "attachments": expert.attachments,
            "created_at": expert.created_at.isoformat() if expert.created_at else None,
            "updated_at": expert.updated_at.isoformat() if expert.updated_at else None,
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total
    })


@publish_bp.route('/public/experts/<expert_id>', methods=['GET'])
def get_public_expert_detail(expert_id):
    """获取单个专家详情（公开接口，无需登录，不含敏感信息）"""
    expert = PublishService.get_expert_by_id(expert_id)
    if not expert:
        return jsonify({"code": 404, "msg": "专家不存在"}), 404

    data = {
        "id": str(expert._id),
        "name": expert.name,
        "gender": expert.gender,
        "highest_education": expert.highest_education,
        "school_major": expert.school_major,
        "work_unit": expert.work_unit,
        "position_title": expert.position_title,
        "professional_fields": expert.professional_fields,
        "professional_fields_other": expert.professional_fields_other,
        "honors": expert.honors,
        "technical_title": expert.technical_title,
        "professional_certification": expert.professional_certification,
        "foreign_language": expert.foreign_language,
        "work_years": expert.work_years,
        "successful_cases": expert.successful_cases,
        "patents": expert.patents,
        "publications": expert.publications,
        "research_projects": expert.research_projects,
        "awards": expert.awards,
        "personal_profile": expert.personal_profile,
        "attachments": expert.attachments,
        "created_at": expert.created_at.isoformat() if expert.created_at else None,
        "updated_at": expert.updated_at.isoformat() if expert.updated_at else None,
    }

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": data
    })


# ==========================================
# 合作申请 API
# ==========================================

@publish_bp.route('/cooperation/apply', methods=['POST', 'OPTIONS'])
def create_cooperation():
    """普通用户提交合作申请（公开接口，无需登录）"""
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    if not data.get('contact_name'):
        return jsonify({"code": 400, "msg": "联系人姓名不能为空"}), 400
    if not data.get('contact_phone'):
        return jsonify({"code": 400, "msg": "联系人电话不能为空"}), 400

    cooperation = CooperationService.create_cooperation(data)
    if not cooperation:
        return jsonify({"code": 500, "msg": "申请提交失败"}), 500

    # ====== 给所有管理员发送通知 ======
    try:
        contact_name = data.get('contact_name', '未知')
        company = data.get('company', '未知')
        admin_users = User.query.filter_by(role='admin').all()
        for admin in admin_users:
            db.session.add(Message(
                send_user_id=0,
                receive_user_id=admin.id,
                msg_type='result',
                biz_type='cooperation',
                biz_id=str(cooperation._id),
                title='新的合作申请待处理',
                content=f'联系人 {contact_name}（{company}）提交了合作申请，请及时处理',
                is_read=0,
                create_time=datetime.now()
            ))
        db.session.commit()

        # 实时推送通知
        for admin in admin_users:
            try:
                emit_new_message_event(admin.id, {
                    'id': 0,
                    'title': '新的合作申请待处理',
                    'content': f'联系人 {contact_name}（{company}）提交了合作申请，请及时处理',
                    'msg_type': 'result',
                    'biz_type': 'cooperation',
                    'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception:
                pass
    except Exception as e:
        db.session.rollback()
        print(f"[合作申请] 发送管理员通知失败: {e}")

    return jsonify({
        "code": 200,
        "msg": "申请提交成功",
        "data": {"id": str(cooperation._id)}
    })


@publish_bp.route('/admin/cooperation/list', methods=['GET'])
@token_required
def get_cooperation_list():
    """管理员获取合作申请列表"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可访问"}), 403

    keyword = request.args.get('keyword', '', type=str)
    cooperations = CooperationService.get_cooperations(limit=0)
    total = len(cooperations)

    if keyword.strip():
        kw = keyword.lower()
        cooperations = [c for c in cooperations if
                        kw in (c.contact_name or '').lower() or
                        kw in (c.company or '').lower()]

    # 获取关联的合作伙伴信息
    result = []
    for c in cooperations:
        partner_info = None
        if c.partner_id:
            try:
                partner = Partner.get(c.partner_id)
                if partner:
                    partner_info = {
                        "id": str(partner._id),
                        "name": partner.name,
                        "type": partner.type,
                        "industry": partner.industry,
                        "address": partner.address,
                        "intro": partner.intro,
                        "services": partner.services,
                        "images": partner.images
                    }
            except Exception as e:
                print(f"[WARN] 获取合作伙伴信息失败: {e}")

        result.append({
            "id": str(c._id),
            "partner_id": c.partner_id,
            "contact_name": c.contact_name,
            "contact_phone": c.contact_phone,
            "contact_email": c.contact_email,
            "company": c.company,
            "address": c.address,
            "intention": c.intention,
            "partner_info": partner_info,
            "created_at": c.created_at.isoformat() if c.created_at else None
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total
    })


@publish_bp.route('/admin/cooperation/detail/<cooperation_id>', methods=['GET'])
@token_required
def get_cooperation_detail(cooperation_id):
    """管理员获取合作申请详情"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可访问"}), 403

    c = CooperationService.get_cooperation_by_id(cooperation_id)
    if not c:
        return jsonify({"code": 404, "msg": "合作申请不存在"}), 404

    partner_info = None
    if c.partner_id:
        try:
            partner = Partner.get(c.partner_id)
            if partner:
                partner_info = {
                    "id": str(partner._id),
                    "name": partner.name,
                    "type": partner.type,
                    "industry": partner.industry,
                    "address": partner.address,
                    "intro": partner.intro,
                    "services": partner.services,
                    "images": partner.images
                }
        except Exception as e:
            print(f"[WARN] 获取合作伙伴信息失败: {e}")

    data = {
        "id": str(c._id),
        "partner_id": c.partner_id,
        "contact_name": c.contact_name,
        "contact_phone": c.contact_phone,
        "contact_email": c.contact_email,
        "company": c.company,
        "address": c.address,
        "intention": c.intention,
        "partner_info": partner_info,
        "created_at": c.created_at.isoformat() if c.created_at else None
    }

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": data
    })


@publish_bp.route('/admin/cooperation/<cooperation_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_cooperation(cooperation_id):
    """管理员删除合作申请"""
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    success = CooperationService.delete_cooperation(cooperation_id)
    if not success:
        return jsonify({"code": 404, "msg": "合作申请不存在或删除失败"}), 404

    return jsonify({
        "code": 200,
        "msg": "删除成功"
    })


# ==========================================
# 网站访问追踪 API
# ==========================================

@publish_bp.route('/visit/track', methods=['POST', 'OPTIONS'])
def track_visit():
    """记录网站页面访问"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json() or {}
        ip = request.remote_addr or ''
        mongo_db = get_mongodb()

        # 每个 IP 每天只记录一条，避免重复数据
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        existing = mongo_db.visit_logs.find_one({
            'ip': ip,
            'created_at': {'$gte': today_start}
        })
        if existing:
            return '', 200

        mongo_db.visit_logs.insert_one({
            'path': data.get('path', '/'),
            'title': data.get('title', ''),
            'ip': ip,
            'user_agent': request.headers.get('User-Agent', ''),
            'created_at': datetime.now()
        })
    except Exception as e:
        # 静默失败，不影响用户体验
        print(f"[WARN] 访问记录失败: {e}")

    return jsonify({"code": 200, "msg": "ok"})


# ==========================================
# 访客日志管理 API（管理员 CRUD）
# ==========================================

@publish_bp.route('/admin/visit-logs', methods=['GET'])
@token_required
def list_visit_logs():
    """获取访客日志列表（分页 + 筛选）"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        ip_filter = request.args.get('ip', '').strip()
        path_filter = request.args.get('path', '').strip()
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        mongo_db = get_mongodb()
        match_cond = {}

        if ip_filter:
            match_cond['ip'] = {'$regex': ip_filter, '$options': 'i'}
        if path_filter:
            match_cond['path'] = {'$regex': path_filter, '$options': 'i'}
        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range['$gte'] = datetime.strptime(date_from, '%Y-%m-%d')
            if date_to:
                date_range['$lte'] = datetime.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            match_cond['created_at'] = date_range

        total = mongo_db.visit_logs.count_documents(match_cond)
        cursor = mongo_db.visit_logs.find(match_cond, {
            'path': 1, 'title': 1, 'ip': 1, 'user_agent': 1, 'created_at': 1
        }).sort('created_at', -1).skip((page - 1) * page_size).limit(page_size)

        logs = []
        for doc in cursor:
            logs.append({
                '_id': str(doc['_id']),
                'path': doc.get('path', ''),
                'title': doc.get('title', ''),
                'ip': doc.get('ip', ''),
                'user_agent': doc.get('user_agent', ''),
                'created_at': doc.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if doc.get('created_at') else ''
            })

        return jsonify({"code": 200, "msg": "ok", "data": logs, "total": total, "page": page, "page_size": page_size})
    except Exception as e:
        print(f"[ERROR] 获取访客日志失败: {e}")
        return jsonify({"code": 500, "msg": "获取失败"}), 500


@publish_bp.route('/admin/visit-logs/<log_id>', methods=['DELETE'])
@token_required
def delete_visit_log(log_id):
    """删除单条访客日志"""
    try:
        from bson.objectid import ObjectId
        mongo_db = get_mongodb()
        result = mongo_db.visit_logs.delete_one({'_id': ObjectId(log_id)})
        if result.deleted_count:
            return jsonify({"code": 200, "msg": "删除成功"})
        return jsonify({"code": 404, "msg": "记录不存在"}), 404
    except Exception as e:
        print(f"[ERROR] 删除访客日志失败: {e}")
        return jsonify({"code": 500, "msg": "删除失败"}), 500


@publish_bp.route('/admin/visit-logs/clear', methods=['DELETE'])
@token_required
def clear_visit_logs():
    """清空所有访客日志"""
    try:
        mongo_db = get_mongodb()
        result = mongo_db.visit_logs.delete_many({})
        return jsonify({"code": 200, "msg": f"已清空 {result.deleted_count} 条记录"})
    except Exception as e:
        print(f"[ERROR] 清空访客日志失败: {e}")
        return jsonify({"code": 500, "msg": "清空失败"}), 500


# ==========================================
# 仪表板统计数据 API
# ==========================================

@publish_bp.route('/admin/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats():
    """获取仪表板统计数据（管理员专用）"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可访问"}), 403

    # 普通用户总数（MySQL - users 表 role='common'）
    common_users = User.query.filter_by(role='common').count()

    # 成果总数（MongoDB）
    achievements_count = Achievement._collection.count_documents({})

    # 需求总数（MongoDB）
    requirements_count = Requirement._collection.count_documents({})

    # 专家总数（MongoDB）
    experts_count = Expert._collection.count_documents({})

    # 伙伴总数（MongoDB）
    partners_count = Partner._collection.count_documents({})

    # ====== 1. 待办审批概览 ======
    pending_achievements = Achievement._collection.count_documents({'status': 'pending'})
    pending_requirements = Requirement._collection.count_documents({'status': 'pending'})
    cooperation_count = Cooperation._collection.count_documents({})

    # ====== 2. 内容分布情况 ======
    # 成果技术领域分布
    tech_field_pipeline = [
        {'$unwind': '$tech_fields'},
        {'$group': {'_id': '$tech_fields', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    try:
        tech_field_data = list(Achievement._collection.aggregate(tech_field_pipeline))
    except Exception:
        tech_field_data = []
    tech_fields = [{'name': item['_id'], 'count': item['count']} for item in tech_field_data]

    # 成果按状态分布
    try:
        achievement_status_data = list(Achievement._collection.aggregate([
            {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
        ]))
    except Exception:
        achievement_status_data = []
    achievement_status = [{'name': item['_id'], 'count': item['count']} for item in achievement_status_data]

    # 需求按状态分布
    try:
        requirement_status_data = list(Requirement._collection.aggregate([
            {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
        ]))
    except Exception:
        requirement_status_data = []
    requirement_status = [{'name': item['_id'], 'count': item['count']} for item in requirement_status_data]

    # ====== 3. 客服运营状态 ======
    active_sessions = Session._collection.count_documents({'status': 'active'})
    waiting_sessions = Session._collection.count_documents({'status': 'pending'})
    # 按 agent_id 去重统计在线客服数，防止并发重复记录的干扰
    distinct_online_agents = AgentStatus._collection.distinct('agent_id', {'online_status': {'$in': ['online', 'busy']}})
    online_agents = len(distinct_online_agents)

    # ====== 4. 近7天趋势数据 ======
    today = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    seven_days_ago = (today - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    next_day = today + timedelta(days=1)

    # 生成7天日期列表
    date_list = [(seven_days_ago + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

    # 获取已有数据
    try:
        achievement_trend_raw = list(Achievement._collection.aggregate([
            {'$match': {
                'created_at': {'$gte': seven_days_ago, '$lt': next_day, '$type': 'date'}
            }},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at'}},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]))
    except Exception:
        achievement_trend_raw = []
    achievement_trend_map = {item['_id']: item['count'] for item in achievement_trend_raw}

    try:
        requirement_trend_raw = list(Requirement._collection.aggregate([
            {'$match': {
                'created_at': {'$gte': seven_days_ago, '$lt': next_day, '$type': 'date'}
            }},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at'}},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]))
    except Exception:
        requirement_trend_raw = []
    requirement_trend_map = {item['_id']: item['count'] for item in requirement_trend_raw}

    # 用户注册趋势（MySQL）
    try:
        user_trend_raw = db.session.query(
            db.func.date(User.created_at).label('date'),
            db.func.count(User.id).label('count')
        ).filter(
            User.created_at >= seven_days_ago,
            User.created_at < next_day
        ).group_by(
            db.func.date(User.created_at)
        ).order_by('date').all()
    except Exception:
        user_trend_raw = []
    user_trend_map = {row.date.strftime('%Y-%m-%d') if hasattr(row.date, 'strftime') else str(row.date): row.count for row in user_trend_raw}

    # 用日期数组填充，缺失补0
    achievement_trend = [achievement_trend_map.get(d, 0) for d in date_list]
    requirement_trend = [requirement_trend_map.get(d, 0) for d in date_list]
    user_trend = [user_trend_map.get(d, 0) for d in date_list]

    # ====== 5. 网站访问趋势（独立访客 UV，按 IP 去重） ======
    try:
        mongo_db = get_mongodb()
        visit_trend_raw = list(mongo_db.visit_logs.aggregate([
            {'$match': {
                'created_at': {'$gte': seven_days_ago, '$lt': next_day}
            }},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at'}},
                'ips': {'$addToSet': '$ip'}
            }},
            {'$project': {
                '_id': 1,
                'count': {'$size': '$ips'}
            }},
            {'$sort': {'_id': 1}}
        ]))
    except Exception:
        visit_trend_raw = []
    visit_trend_map = {item['_id']: item['count'] for item in visit_trend_raw}
    visit_trend = [visit_trend_map.get(d, 0) for d in date_list]

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": {
            # 原有数据
            "common_users": common_users,
            "achievements": achievements_count,
            "requirements": requirements_count,
            "experts": experts_count,
            "partners": partners_count,

            # 1. 待办审批
            "pending_review": {
                "pending_achievements": pending_achievements,
                "pending_requirements": pending_requirements,
                "cooperation_applications": cooperation_count
            },

            # 2. 内容分布
            "content_distribution": {
                "tech_fields": tech_fields,
                "achievement_status": achievement_status,
                "requirement_status": requirement_status
            },

            # 3. 客服运营
            "customer_service": {
                "active_sessions": active_sessions,
                "waiting_sessions": waiting_sessions,
                "online_agents": online_agents
            },

            # 4. 近7天趋势
            "trends": {
                "dates": date_list,
                "achievements": achievement_trend,
                "requirements": requirement_trend,
                "users": user_trend,
                "visits": visit_trend
            }
        }
    })


# ==========================================
# 管理员成果/需求管理 API
# ==========================================

@publish_bp.route('/admin/achievements', methods=['GET'])
@token_required
def admin_get_achievements():
    """管理员获取所有成果列表（含分页、关键词搜索、状态筛选）"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可访问"}), 403

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    offset = (page - 1) * page_size

    achievements = PublishService.get_all_achievements(limit=page_size, offset=offset)

    # 关键词搜索
    if keyword.strip():
        kw = keyword.lower()
        achievements = [a for a in achievements if
                        kw in (a.achievement_name or '').lower() or
                        kw in (a.achievement_code or '').lower() or
                        kw in (a.owner or '').lower()]

    # 状态筛选
    if status_filter and status_filter in ('pending', 'approved', 'rejected'):
        achievements = [a for a in achievements if a.status == status_filter]

    all_items = PublishService.get_all_achievements(limit=0)
    total = len(all_items)

    result = []
    for a in achievements:
        result.append({
            "id": str(a._id),
            "user_id": a.user_id,
            "achievement_code": a.achievement_code,
            "achievement_name": a.achievement_name,
            "owner": a.owner,
            "tech_fields": a.tech_fields or [],
            "tech_fields_other": a.tech_fields_other or '',
            "tech_maturity": a.tech_maturity or '',
            "transfer_methods": a.transfer_methods or [],
            "transfer_methods_other": a.transfer_methods_other or '',
            "status": a.status,
            "is_display": getattr(a, 'is_display', False),
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None,
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


@publish_bp.route('/admin/requirements', methods=['GET'])
@token_required
def admin_get_requirements():
    """管理员获取所有需求列表（含分页、关键词搜索、状态筛选）"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可访问"}), 403

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    offset = (page - 1) * page_size

    requirements = PublishService.get_all_requirements(limit=page_size, offset=offset)

    # 关键词搜索
    if keyword.strip():
        kw = keyword.lower()
        requirements = [r for r in requirements if
                        kw in (r.demand_name or '').lower() or
                        kw in (r.demand_code or '').lower() or
                        kw in (r.company_name or '').lower()]

    # 状态筛选
    if status_filter and status_filter in ('pending', 'approved', 'rejected'):
        requirements = [r for r in requirements if r.status == status_filter]

    all_items = PublishService.get_all_requirements(limit=0)
    total = len(all_items)

    result = []
    for r in requirements:
        result.append({
            "id": str(r._id),
            "user_id": r.user_id,
            "demand_code": r.demand_code,
            "demand_name": r.demand_name,
            "company_name": r.company_name,
            "tech_fields": r.tech_fields or [],
            "tech_fields_other": r.tech_fields_other or '',
            "demand_types": r.demand_types or [],
            "demand_types_other": r.demand_types_other or '',
            "budget": r.description.get('budget', 0) if hasattr(r, 'description') and isinstance(r.description, dict) else 0,
            "status": r.status,
            "is_display": getattr(r, 'is_display', False),
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            "match_status": getattr(r, 'match_status', '待对接'),
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


@publish_bp.route('/achievement/<achievement_id>', methods=['DELETE'])
@token_required
def admin_delete_achievement(achievement_id):
    """管理员删除成果"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    success = PublishService.delete_achievement(achievement_id)
    if not success:
        return jsonify({"code": 404, "msg": "成果不存在或删除失败"}), 404

    return jsonify({"code": 200, "msg": "成果删除成功"})


@publish_bp.route('/requirement/<requirement_id>', methods=['DELETE'])
@token_required
def admin_delete_requirement(requirement_id):
    """管理员删除需求"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    success = PublishService.delete_requirement(requirement_id)
    if not success:
        return jsonify({"code": 404, "msg": "需求不存在或删除失败"}), 404

    return jsonify({"code": 200, "msg": "需求删除成功"})


@publish_bp.route('/admin/achievement/<achievement_id>', methods=['PUT'])
@token_required
def admin_update_achievement(achievement_id):
    """管理员更新成果信息"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    updated = PublishService.admin_update_achievement(achievement_id, data)
    if not updated:
        return jsonify({"code": 404, "msg": "成果不存在或更新失败"}), 404

    return jsonify({"code": 200, "msg": "成果更新成功"})


@publish_bp.route('/admin/requirement/<requirement_id>', methods=['PUT'])
@token_required
def admin_update_requirement(requirement_id):
    """管理员更新需求信息"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.role != 'admin':
        return jsonify({"code": 403, "msg": "权限不足，仅管理员可操作"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    updated = PublishService.admin_update_requirement(requirement_id, data)
    if not updated:
        return jsonify({"code": 404, "msg": "需求不存在或更新失败"}), 404

    return jsonify({"code": 200, "msg": "需求更新成功"})
