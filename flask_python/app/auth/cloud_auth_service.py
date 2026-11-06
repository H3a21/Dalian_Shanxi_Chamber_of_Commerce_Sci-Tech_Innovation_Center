import os
from flask import current_app
from alibabacloud_cloudauth20190307.client import Client as Cloudauth20190307Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cloudauth20190307 import models as cloudauth_20190307_models
from alibabacloud_tea_util import models as util_models


def _create_client():
    """创建阿里云实人认证客户端"""
    ak_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID') or current_app.config.get('ALIBABA_CLOUD_ACCESS_KEY_ID', '')
    ak_secret = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET') or current_app.config.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET', '')

    if not ak_id or not ak_secret:
        raise RuntimeError(
            '阿里云 AccessKey 未配置。请设置环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID / '
            'ALIBABA_CLOUD_ACCESS_KEY_SECRET，或在 config.py 中配置。'
        )

    config = open_api_models.Config(
        access_key_id=ak_id,
        access_key_secret=ak_secret
    )
    config.endpoint = 'cloudauth.cn-beijing.aliyuncs.com'
    return Cloudauth20190307Client(config)


def verify_identity(real_name: str, id_card: str, mobile: str) -> dict:
    """
    通过阿里云 Mobile3MetaSimpleVerify 认证手机号、姓名和身份证号是否一致

    Returns:
        {"success": True/False, "message": "...", "biz_code": "1"}
        biz_code: 1=一致, 2=不一致, 3=查无记录, 其他=异常
    """
    try:
        client = _create_client()
    except RuntimeError as e:
        return {"success": False, "message": str(e), "biz_code": None}

    request = cloudauth_20190307_models.Mobile3MetaSimpleVerifyRequest(
        param_type='normal',
        identify_num=id_card.strip(),
        user_name=real_name.strip(),
        mobile=mobile.strip()
    )
    runtime = util_models.RuntimeOptions()

    try:
        resp = client.mobile_3meta_simple_verify_with_options(request, runtime)
        body = resp.body

        if body.code == '200':
            result = body.result_object
            biz_code = result.biz_code if hasattr(result, 'biz_code') else None

            if biz_code == '1':
                return {"success": True, "message": "身份认证通过", "biz_code": "1"}
            elif biz_code == '2':
                return {"success": False, "message": "手机号、姓名与身份证号不匹配，请核对后重试", "biz_code": "2"}
            elif biz_code == '3':
                return {"success": False, "message": "无法查询到该身份信息", "biz_code": "3"}
            else:
                msg = result.message if hasattr(result, 'message') else '认证失败'
                return {"success": False, "message": f"认证失败: {msg}", "biz_code": biz_code}
        else:
            return {"success": False, "message": f"认证服务异常: {body.code}", "biz_code": None}

    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'message') and e.message:
            error_msg = e.message
        return {"success": False, "message": f"认证请求异常: {error_msg}", "biz_code": None}
