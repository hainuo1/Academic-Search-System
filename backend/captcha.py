import io
import random
import string
from PIL import Image, ImageDraw, ImageFont


def generate():
    w, h = 160, 60
    bg = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
    img = Image.new('RGB', (w, h), bg)
    draw = ImageDraw.Draw(img)

    for _ in range(5):
        x1, y1 = random.randint(0, w), random.randint(0, h)
        x2, y2 = random.randint(0, w), random.randint(0, h)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)), width=1)

    for _ in range(100):
        x, y = random.randint(0, w), random.randint(0, h)
        draw.point((x, y), fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)))

    chars = string.ascii_uppercase + string.digits
    text = ''.join(random.choice(chars) for _ in range(4))

    try:
        font = ImageFont.truetype('arial.ttf', 36)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
        except (IOError, OSError):
            font = ImageFont.load_default()

    for i, ch in enumerate(text):
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        x = 20 + i * 35 + random.randint(-5, 5)
        y = random.randint(5, 15)
        draw.text((x, y), ch, fill=color, font=font)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf, text
