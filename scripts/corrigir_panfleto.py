"""Correções no panfleto: aviso removido por completo e preços redesenhados."""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FLYER = ROOT / "img" / "lista-pecas.png"
PECAS_JSON = ROOT / "data" / "pecas.json"

AVISO_BOX = (518, 288, 1015, 408)
FIRST_ROW_Y = 490
ROW_STEP = 35
PRICE_X1, PRICE_X2 = 800, 1008
PRICE_Y_HALF = 20
TOTAL_BOX = (655, 1285, 975, 1345)
YELLOW = (255, 193, 7)
BLACK = (0, 0, 0)


def load_font(size: int):
    for path in (
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def sample_bg(img: Image.Image, x: int, y: int) -> tuple:
    pixels = [img.getpixel((x + dx, y + dy)) for dx in range(-2, 3) for dy in range(-2, 3)]
    return tuple(sum(c[i] for c in pixels) // len(pixels) for i in range(3))


def format_preco(value: int) -> str:
    return f"R$ {value:,}".replace(",", ".")


def repaint_prices(img: Image.Image, pecas: list, total: int):
    draw = ImageDraw.Draw(img)
    font_row = load_font(17)
    font_total = load_font(28)

    draw.rectangle(AVISO_BOX, fill=BLACK)

    # Limpa toda a coluna de preços da tabela
    last_y = FIRST_ROW_Y + (len(pecas) - 1) * ROW_STEP
    draw.rectangle(
        (PRICE_X1, FIRST_ROW_Y - PRICE_Y_HALF - 2, PRICE_X2, last_y + PRICE_Y_HALF + 2),
        fill=BLACK,
    )

    for i, peca in enumerate(pecas):
        y = FIRST_ROW_Y + i * ROW_STEP
        txt = format_preco(peca["preco"])
        bbox = draw.textbbox((0, 0), txt, font=font_row)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((PRICE_X2 - tw - 4, y - th // 2 - 2), txt, fill=YELLOW, font=font_row)

    total_txt = format_preco(total)
    draw.rectangle(TOTAL_BOX, fill=BLACK)
    bbox = draw.textbbox((0, 0), total_txt, font=font_total)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    ty = TOTAL_BOX[1] + (TOTAL_BOX[3] - TOTAL_BOX[1] - th) // 2
    draw.text((TOTAL_BOX[2] - tw - 6, ty), total_txt, fill=YELLOW, font=font_total)


def main():
    with open(PECAS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    img = Image.open(FLYER).convert("RGB")
    repaint_prices(img, data["pecas"], data["valorTotalEstimado"])
    img.save(FLYER, "PNG", optimize=True)

    orig = ROOT / "Lista de peças-PassatVariant.png"
    if orig.exists():
        img.save(orig, "PNG", optimize=True)

    print("Panfleto corrigido.")


if __name__ == "__main__":
    main()
