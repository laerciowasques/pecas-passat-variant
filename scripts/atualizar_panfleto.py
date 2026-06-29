"""Remove aviso 'pessoa física' e aplica 25% de desconto nos preços do panfleto."""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FLYER = ROOT / "img" / "lista-pecas.png"
PECAS_JSON = ROOT / "data" / "pecas.json"

FLYER_W, FLYER_H = 1024, 1536
AVISO_BOX = (548, 324, 1006, 392)
FIRST_ROW_Y = 490
ROW_STEP = 35
PRICE_X1, PRICE_X2 = 812, 1004
PRICE_Y_HALF = 16
TOTAL_BOX = (668, 1293, 962, 1338)

YELLOW = (255, 193, 7)
BLACK = (0, 0, 0)


def load_font(size: int, bold: bool = True):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/Arial Bold.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def format_preco(value: int) -> str:
    return f"R$ {value:,}".replace(",", ".")


def sample_bg(img: Image.Image, x: int, y: int) -> tuple:
    pixels = [img.getpixel((x + dx, y + dy)) for dx in range(-3, 4) for dy in range(-3, 4)]
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    return (r, g, b)


def main():
    with open(PECAS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    total = 0
    for peca in data["pecas"]:
        base = peca.get("precoOriginal", peca["preco"])
        novo = round(base * 0.75)
        peca["precoOriginal"] = base
        peca["preco"] = novo
        total += novo
    data["valorTotalEstimado"] = total
    data["descontoPercentual"] = 25

    with open(PECAS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    img = Image.open(FLYER).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Remove aviso — preenche com fundo preto da região
    bg = sample_bg(img, 700, 410)
    draw.rectangle(AVISO_BOX, fill=bg)

    font_row = load_font(17)
    font_total = load_font(28)

    for i, peca in enumerate(data["pecas"]):
        y = FIRST_ROW_Y + i * ROW_STEP
        preco_txt = format_preco(peca["preco"])
        row_bg = sample_bg(img, PRICE_X1 + 20, y)
        draw.rectangle(
            (PRICE_X1, y - PRICE_Y_HALF, PRICE_X2, y + PRICE_Y_HALF),
            fill=row_bg,
        )
        bbox = draw.textbbox((0, 0), preco_txt, font=font_row)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = PRICE_X2 - tw - 6
        ty = y - th // 2 - 2
        draw.text((tx, ty), preco_txt, fill=YELLOW, font=font_row)

    # Total estimado
    total_txt = format_preco(total)
    tbg = sample_bg(img, 800, 1315)
    draw.rectangle(TOTAL_BOX, fill=tbg)
    bbox = draw.textbbox((0, 0), total_txt, font=font_total)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = TOTAL_BOX[2] - tw - 8
    ty = TOTAL_BOX[1] + (TOTAL_BOX[3] - TOTAL_BOX[1] - th) // 2
    draw.text((tx, ty), total_txt, fill=YELLOW, font=font_total)

    img.save(FLYER, "PNG", optimize=True)

    orig = ROOT / "Lista de peças-PassatVariant.png"
    if orig.exists():
        img.save(orig, "PNG", optimize=True)

    print(f"Panfleto atualizado. Total com desconto: {total_txt}")


if __name__ == "__main__":
    main()
