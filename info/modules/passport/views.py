import random
import re

from flask import request, abort, current_app, make_response, jsonify

from info import redis_store, constants
from info.modules.passport import passport_blu

from info.utils.captcha.captcha import captcha


from info.utils.response_code import RET


from info.libs.yuntongxun.sms import CCP


# 短信验证码   post请求
@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():
    """
    生产并发送短信验证码
    1.获取参数：手机号，图片验证码id，图片验证码内容
    2.判断是否有值，校验手机号
    3.从redis中取出图片验证码内容，与用户传过来的图片验证码内容进行校验
    4.生成短信验证码
    5.发送短信验证码
    6.将短信验证码内容存到redis中，记录验证码
    7.返回响应
    :return:
    """

    # 1.获取参数：手机号，图片验证码id，图片验证码内容
    params_dict = request.json
    mobile = params_dict["mobile"]
    image_code = params_dict["image_code"]
    image_code_id = params_dict["image_code_id"]

    # 2.判断是否有值，校验手机号
    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 校验手机号
    if not re.match(r"^1[345678]\d{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号不正确")

    # 3.从redis中取出图片验证码内容，与用户传过来的图片验证码内容进行校验
    try:
        real_image_code = redis_store.get("imageCodeId" + image_code_id)
        # 如果取出图片验证码内容, 删除redis中的缓存
        if real_image_code:
            real_image_code = real_image_code.decode()
            redis_store.delete("imageCodeId" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")
    # 校验
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码错误")

    # 生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # 5.发送短信验证码
    result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES//60], 2)
    if result != 0:
        return jsonify(errno=RET.THIRDERR, errmsg="验证码发送失败")

    # 6.将短信验证码内容存到redis中
    redis_store.set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    # 记录验证码
    current_app.logger.info("SMS_%s,---短信验证码%s" % (mobile, sms_code))

    # 7.返回响应
    return jsonify(errno=RET.OK, errmsg="验证码已发送，请注意查收")



# 图片验证码
@passport_blu.route("/image_code")
def get_image_code():
    """
    生产图片验证码
    1.取出参数
    2.看参数是否有值
    3.生成图片验证码
    4.存储验证码内容到redis中
    5.返回验证码图片
    :return:
    """

    # 1.取出参数
    image_code_id = request.args.get("imageCodeId", None)

    # 2.看参数是否有值
    if not image_code_id:
        return abort(403)

    # 3.生成图片验证码  # 名字，内容，图片
    name, text, image = captcha.generate_captcha()
    # 打印出图片验证码内容
    current_app.logger.info("图片验证码:%s" % text)
    # 4.存储验证码内容到redis中
    try:
        redis_store.set("imageCodeId" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 5.返回验证码图片
    response = make_response(image)
    # 设置数据的类型，以便浏览器更加智能识别其是什么类型
    response.headers["Content-Type"] = "image/jpg"
    return response

