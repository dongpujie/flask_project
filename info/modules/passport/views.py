from flask import request, abort, current_app, make_response

from info import redis_store, constants
from info.modules.passport import passport_blu

from info.utils.captcha.captcha import captcha


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

