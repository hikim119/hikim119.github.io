"""브라우저 탭 아이콘(파비콘) 만들기: 남색 둥근 사각형에 흰 「삼」.

    python sameuntech/_build/make_icons.py

로고가 생기면 이 그림 대신 로고로 favicon.png / apple-touch-icon.png 를 바꾼다.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent
FONT = "C:/Windows/Fonts/NotoSansKR-Black.ttf"


def icon(size, radius_ratio=0.22, text_ratio=0.66):
    s = size * 4  # 크게 그린 뒤 줄여서 가장자리를 매끄럽게
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    # 위→아래 남색 그라데이션
    grad = Image.new("RGBA", (s, s))
    gd = ImageDraw.Draw(grad)
    top, bot = (31, 63, 140), (11, 23, 54)
    for y in range(s):
        t = y / (s - 1)
        gd.line([(0, y), (s, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bot)) + (255,))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * radius_ratio), fill=255)
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, int(s * text_ratio))
    box = d.textbbox((0, 0), "삼", font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((s - w) / 2 - box[0], (s - h) / 2 - box[1]), "삼", font=font, fill="white")
    return img.resize((size, size), Image.LANCZOS)


icon(64).save(OUT / "favicon.png", optimize=True)
icon(180, radius_ratio=0.0).convert("RGB").save(OUT / "apple-touch-icon.png", optimize=True)  # iOS 가 직접 둥글게 깎는다
print("ok", (OUT / "favicon.png").stat().st_size, (OUT / "apple-touch-icon.png").stat().st_size)
