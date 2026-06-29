"""Extrai os ícones de cada peça do catálogo Passat Variant (flyer original)."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FLYER = ROOT / "img" / "lista-pecas.png"
OUT = ROOT / "img" / "pecas"
OUT.mkdir(parents=True, exist_ok=True)

NAMES = [
    "01-painel",
    "02-botoes",
    "03-ar-condicionado",
    "04-bancos",
    "05-portas",
    "06-rodas",
    "07-multimidia",
    "08-porta-luvas",
    "09-rack-teto",
    "10-antena",
    "11-comando-ar",
    "12-manopla",
    "13-farol",
    "14-volante",
    "15-porta-malas",
    "16-tampao",
    "17-tanque",
    "18-carpete",
    "19-retrovisor",
    "20-abs",
]

img = Image.open(FLYER).convert("RGB")

# Coordenadas calibradas (1024×1536) — seção LISTA DE PREÇOS
FIRST_ROW_Y = 490
ROW_STEP = 35
ICON_X1 = 95
ICON_X2 = 230
ICON_HALF_H = 11
PAD = 4
TARGET_W = 380
TARGET_H = 80


def save_icon(crop: Image.Image, dest: Path):
    """Centraliza o ícone no canvas preto (como no panfleto)."""
    pixels = crop.load()
    cw, ch = crop.size
    threshold = 28
    bbox = None

    for y in range(ch):
        for x in range(cw):
            r, g, b = pixels[x, y]
            if r > threshold or g > threshold or b > threshold:
                if bbox is None:
                    bbox = [x, y, x, y]
                else:
                    bbox[0] = min(bbox[0], x)
                    bbox[1] = min(bbox[1], y)
                    bbox[2] = max(bbox[2], x)
                    bbox[3] = max(bbox[3], y)

    if bbox:
        crop = crop.crop(tuple(bbox))

    cw, ch = crop.size
    canvas = Image.new("RGB", (TARGET_W, TARGET_H), (0, 0, 0))
    scale = min((TARGET_W - PAD * 2) / cw, (TARGET_H - PAD * 2) / ch)
    nw = max(1, int(cw * scale))
    nh = max(1, int(ch * scale))
    resized = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    ox = (TARGET_W - nw) // 2
    oy = (TARGET_H - nh) // 2
    canvas.paste(resized, (ox, oy))
    canvas.save(dest, "JPEG", quality=94)


for i, name in enumerate(NAMES):
    y_center = FIRST_ROW_Y + i * ROW_STEP
    y1 = int(y_center - ICON_HALF_H)
    y2 = int(y_center + ICON_HALF_H)
    crop = img.crop((ICON_X1, y1, ICON_X2, y2))
    dest = OUT / f"{name}.jpg"
    save_icon(crop, dest)
    print(f"OK {name} -> {dest.name}")

print("Concluído:", len(NAMES), "ícones extraídos do catálogo.")
