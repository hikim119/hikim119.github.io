"""로고 원본(_build/logo-source.png, 투명 배경)에서 사이트용 로고·탭 아이콘·공유 이미지를 만든다.

    python sameuntech/_build/make_icons.py

만드는 것
  img/logo.png       흰 바탕용 원래 색 로고 (푸터·모바일 메뉴)
  img/logo-dark.png  어두운 바탕용: SE 마크는 색 그대로, 글자만 흰색 (머리말)
  favicon.png        브라우저 탭 아이콘 (SE 마크)
  apple-touch-icon.png  아이폰 홈 화면 아이콘 (흰 바탕 + SE 마크)
  og.jpg             카카오톡·문자 공유 미리보기 (메인 사진 + 로고)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
FONT = "C:/Windows/Fonts/NotoSansKR-{}.ttf"

src = Image.open(HERE / "logo-source.png").convert("RGBA")
arr = np.asarray(src)
vis = arr[..., 3] > 40
ys, xs = np.where(vis)
logo = src.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

# 마크와 글자 사이의 빈 세로줄 찾기
cols = (np.asarray(logo)[..., 3] > 40).sum(axis=0)
split, run = None, 0
for x, c in enumerate(cols):
    run = run + 1 if c == 0 else 0
    if run > 15:
        split = x - run + 1
        break
if split is None:
    raise SystemExit("마크와 글자 사이 빈 칸을 못 찾음")
mark = logo.crop((0, 0, split, logo.height))
mark = mark.crop(mark.getbbox())


def fit_h(img, h):
    return img.resize((round(img.width * h / img.height), h), Image.LANCZOS)


# 로고 2종 (표시 높이 46px 기준 3배)
H = 140
fit_h(logo, H).save(OUT / "img" / "logo.png", optimize=True)
dark = np.asarray(logo).copy()
dark[:, split:, :3] = 255
fit_h(Image.fromarray(dark), H).save(OUT / "img" / "logo-dark.png", optimize=True)


def square(img, size, pad, bg=None):
    s = size * 4
    canvas = Image.new("RGBA", (s, s), bg or (0, 0, 0, 0))
    inner = s - 2 * int(s * pad)
    m = img.copy()
    m.thumbnail((inner, inner), Image.LANCZOS)
    canvas.paste(m, ((s - m.width) // 2, (s - m.height) // 2), m)
    return canvas.resize((size, size), Image.LANCZOS)


def rounded_white(size, radius=0.22):
    s = size * 4
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * radius), fill=255)
    tile = Image.new("RGBA", (s, s), (255, 255, 255, 0))
    tile.paste(Image.new("RGBA", (s, s), (255, 255, 255, 255)), (0, 0), m)
    return tile


fav = rounded_white(64)
fm = mark.copy()
fm.thumbnail((int(64 * 4 * 0.94), int(64 * 4 * 0.94)), Image.LANCZOS)
fav.paste(fm, ((fav.width - fm.width) // 2, (fav.height - fm.height) // 2), fm)
fav.resize((64, 64), Image.LANCZOS).save(OUT / "favicon.png", optimize=True)
square(mark, 180, 0.12, bg=(255, 255, 255, 255)).convert("RGB").save(OUT / "apple-touch-icon.png", optimize=True)

# 공유 미리보기 1200x630: 메인 사진 오른쪽 + 왼쪽 남색 그라데이션 + 로고
W, Hh = 1200, 630
bg = Image.open(OUT / "img" / "hero.jpg").convert("RGB")
r = Hh / bg.height
bg = bg.resize((round(bg.width * r), Hh), Image.LANCZOS)
bg = bg.crop((bg.width - W, 0, bg.width, Hh)).convert("RGBA")
ov = Image.new("RGBA", (W, Hh))
d = ImageDraw.Draw(ov)
for x in range(W):
    t = x / W
    d.line([(x, 0), (x, Hh)], fill=(8, 17, 42, max(0, int(235 * (1 - t / 0.75)))))
og = Image.alpha_composite(bg, ov)
lg = fit_h(Image.fromarray(dark), 170)
og.paste(lg, (70, 150), lg)
d = ImageDraw.Draw(og)
d.text((84, 372), "SMT · 수삽 · PCB 조립", font=ImageFont.truetype(FONT.format("Bold"), 44), fill="white")
d.text((84, 440), "샘플부터 양산까지 · 02-2083-2070", font=ImageFont.truetype(FONT.format("Medium"), 28), fill=(255, 255, 255, 215))
og.convert("RGB").save(OUT / "og.jpg", "JPEG", quality=85, optimize=True, progressive=True)

for p in ["img/logo.png", "img/logo-dark.png", "favicon.png", "apple-touch-icon.png", "og.jpg"]:
    print(p, (OUT / p).stat().st_size // 1024, "KB")
