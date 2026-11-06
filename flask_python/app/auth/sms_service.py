import json
import os
from flask import current_app

from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models


def _create_client():
    """
    创建阿里云短信客户端
    优先使用环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID / ALIBABA_CLOUD_ACCESS_KEY_SECRET
    其次使用配置文件中的 AccessKey
    """
    ak_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID') or current_app.config.get('ALIBABA_CLOUD_ACCESS_KEY_ID', '')
    ak_secret = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET') or current_app.config.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET', '')

    if not ak_id or not ak_secret:
        raise RuntimeError(
            "阿里云 AccessKey 未配置。请设置环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID / "
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET，或在 config.py 中配置。"
        )

    config = open_api_models.Config(
        access_key_id=ak_id,
        access_key_secret=ak_secret
    )
    config.endpoint = 'dysmsapi.aliyuncs.com'
    return Dysmsapi20170525Client(config)


def send_sms(phone_numbers: str, code: str, sign_name: str = None, template_code: str = None) -> dict:
    """
    发送短信验证码
    """
    try:
        client = _create_client()
    except RuntimeError as e:
        return {"success": False, "message": str(e)}

    sign = sign_name or current_app.config.get('SMS_SIGN_NAME', '大连义韶科技')
    tmpl = template_code or current_app.config.get('SMS_TEMPLATE_CODE', 'SMS_505900101')

    send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
        sign_name=sign,
        template_code=tmpl,
        phone_numbers=phone_numbers,
        template_param=json.dumps({"code": code}, ensure_ascii=False)
    )

    try:
        resp = client.send_sms(send_sms_request)
        body = resp.body
        if body.code == 'OK':
            return {"success": True, "message": "验证码发送成功", "biz_id": body.biz_id}
        else:
            return {"success": False, "message": f"发送失败: {body.message} (code: {body.code})"}
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'message') and e.message:
            error_msg = e.message
        return {"success": False, "message": f"短信发送异常: {error_msg}"}
