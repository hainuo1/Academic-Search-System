# ============================================================
# captcha.py —— 图形验证码生成工具
# ============================================================

import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageFilter


def generate_captcha_text(length=4):
    """
    生成随机验证码字符串（只包含数字和大写字母，避免混淆）
    """
    # 去掉容易混淆的字符：0, O, I, l, 1
    chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    return ''.join(random.choices(chars, k=length))


def generate_captcha_image(text, width=120, height=40):
    """
    根据验证码文本生成图片对象（PIL Image）
    """
    # 1. 创建画布（白色背景）
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 2. 尝试加载字体（如果系统没有中文字体，就用默认字体）
    try:
        # Windows 系统字体路径
        font = ImageFont.truetype('arial.ttf', 24)
    except:
        # 如果找不到，使用默认字体
        font = ImageFont.load_default()

    # 3. 在画布上绘制验证码字符（每个字符稍微偏移位置，增加识别难度）
    x_start = 10
    for i, char in enumerate(text):
        # 随机上下偏移
        y_offset = random.randint(-4, 4)
        # 随机颜色（深色，保证可读性）
        color = (random.randint(0, 80), random.randint(0, 80), random.randint(0, 80))
        draw.text((x_start + i * 25, 8 + y_offset), char, font=font, fill=color)

    # 4. 添加干扰元素（让机器更难识别）
    # 4.1 随机画几条干扰线
    for _ in range(3):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=(180, 180, 180), width=1)

    # 4.2 随机画一些噪点
    for _ in range(80):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=(100, 100, 100))

    # 5. 应用模糊滤镜（让字符边缘不那么锐利，增加机器识别难度）
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))

    return image


def generate_captcha_response():
    """
    生成验证码图片和对应的文本，返回 (图片字节流, 验证码文本)
    供 Flask 路由调用
    """
    text = generate_captcha_text(4)
    image = generate_captcha_image(text)

    # 把图片保存到内存字节流中（不保存到硬盘）
    buf = BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)  # 把指针移到开头，方便读取

    return buf, text