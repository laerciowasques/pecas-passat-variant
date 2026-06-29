"""Baixa e gera imagens fidedignas para o catálogo de peças Passat B7 Variant."""
import io
import time
import urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "img" / "pecas"
SOURCES = ROOT / "img" / "_sources"
BASE.mkdir(parents=True, exist_ok=True)
SOURCES.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (PassatPartsCatalog/1.0)"}


def download(url: str, dest: Path) -> Image.Image:
    time.sleep(1.2)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return Image.open(io.BytesIO(data)).convert("RGB")


def load_local(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def save_crop(img: Image.Image, box, dest: Path, size=400):
    cropped = img.crop(box)
    w, h = cropped.size
    side = max(min(w, h), 1)
    left = max((w - side) // 2, 0)
    top = max((h - side) // 2, 0)
    cropped = cropped.crop((left, top, left + side, top + side))
    cropped = cropped.resize((size, size), Image.Resampling.LANCZOS)
    cropped.save(dest, "JPEG", quality=90)


def save_image(img: Image.Image, dest: Path, size=400):
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    img.save(dest, "JPEG", quality=90)


# Fotos reais do veículo do usuário
frente = load_local(ROOT / "img" / "passat-frente.jpeg")
lateral = load_local(ROOT / "img" / "passat-lateral.jpeg")
traseira = load_local(ROOT / "img" / "passat-traseira.jpeg")

fw, fh = frente.size
lw, lh = lateral.size
rw, rh = traseira.size

# Recortes das fotos reais do Passat Variant do usuário
LOCAL_CROPS = {
    "13-farol": (frente, (int(fw * 0.52), int(fh * 0.38), int(fw * 0.92), int(fh * 0.62))),
    "05-portas": (lateral, (int(lw * 0.22), int(lh * 0.18), int(lw * 0.58), int(lh * 0.72))),
    "06-rodas": (lateral, (int(lw * 0.52), int(lh * 0.58), int(lw * 0.88), int(lh * 0.92))),
    "09-rack-teto": (lateral, (int(lw * 0.18), int(lh * 0.02), int(lw * 0.82), int(lh * 0.16))),
    "10-antena": (lateral, (int(lw * 0.38), int(lh * 0.02), int(lw * 0.62), int(lh * 0.10))),
    "19-retrovisor": (lateral, (int(lw * 0.06), int(lh * 0.12), int(lw * 0.24), int(lh * 0.28))),
    "15-porta-malas": (traseira, (int(rw * 0.12), int(rh * 0.12), int(rw * 0.88), int(rh * 0.72))),
    "04-bancos": (lateral, (int(lw * 0.28), int(lh * 0.28), int(lw * 0.72), int(lh * 0.52))),
}

print("Recortando fotos reais do Passat...")
for name, (img, box) in LOCAL_CROPS.items():
    save_crop(img, box, BASE / f"{name}.jpg")
    print(f"  OK {name}")

# Referências OEM / Passat B7 da internet (URLs verificadas)
OEM_URLS = {
    "01-painel": "https://goliathauto.com/cdn/shop/files/GVO3B_1303_Instrument_Cluster_34adf5ad-cc89-4d78-bf3c-b95758162a4f.png?v=1733001592&width=800",
    "07-multimidia": "https://upload.wikimedia.org/wikipedia/commons/2/2e/SiriusXM_Display_on_Volkswagen%27s_RNS-510_Receiver.png",
    "08-porta-luvas": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Glove-box.jpg",
    "02-botoes": "https://upload.wikimedia.org/wikipedia/commons/f/f5/VW_Passat_Variant_B7_2.0_TDI_BMT_DSG_Highline_Deep_Black_Interieur.JPG",
    "03-ar-condicionado": "https://upload.wikimedia.org/wikipedia/commons/5/5c/VW_Passat_B7_2.0_TDI_DSG_Highline_Kaschmirbraun_Interieur.JPG",
    "11-comando-ar": "https://upload.wikimedia.org/wikipedia/commons/f/f5/VW_Passat_Variant_B7_2.0_TDI_BMT_DSG_Highline_Deep_Black_Interieur.JPG",
    "12-manopla": "https://upload.wikimedia.org/wikipedia/commons/5/5c/VW_Passat_B7_2.0_TDI_DSG_Highline_Kaschmirbraun_Interieur.JPG",
    "14-volante": "https://upload.wikimedia.org/wikipedia/commons/5/5c/VW_Passat_B7_2.0_TDI_DSG_Highline_Kaschmirbraun_Interieur.JPG",
    "16-tampao": "https://upload.wikimedia.org/wikipedia/commons/d/dc/VW_Passat_Variant_B7_2.0_TDI_BMT_DSG_Highline_Deep_Black_Heck.JPG",
    "17-tanque": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vialle_round_lpg.jpg",
    "18-carpete": "https://upload.wikimedia.org/wikipedia/commons/5/5c/VW_Passat_B7_2.0_TDI_DSG_Highline_Kaschmirbraun_Interieur.JPG",
    "20-abs": "https://upload.wikimedia.org/wikipedia/commons/0/0c/ABS_hydraulic_unit.jpg",
}

INTERIOR_CROPS = {
    "02-botoes": (0.38, 0.42, 0.62, 0.58),
    "03-ar-condicionado": (0.28, 0.15, 0.72, 0.38),
    "11-comando-ar": (0.38, 0.32, 0.62, 0.48),
    "12-manopla": (0.43, 0.52, 0.57, 0.68),
    "14-volante": (0.02, 0.22, 0.38, 0.62),
    "18-carpete": (0.08, 0.68, 0.92, 0.96),
    "16-tampao": (0.18, 0.42, 0.82, 0.72),
}

downloaded = {}

print("Baixando referências da web...")
for key, url in OEM_URLS.items():
    try:
        downloaded[key] = download(url, SOURCES / f"{key}_src.jpg")
        print(f"  download OK: {key}")
    except Exception as exc:
        print(f"  download FAIL {key}: {exc}")

# Painel OEM Passat B7
if "01-painel" in downloaded:
    save_image(downloaded["01-painel"], BASE / "01-painel.jpg")

# Multimídia RNS-510 VW
if "07-multimidia" in downloaded:
    save_image(downloaded["07-multimidia"], BASE / "07-multimidia.jpg")

# Porta-luvas
if "08-porta-luvas" in downloaded:
    save_image(downloaded["08-porta-luvas"], BASE / "08-porta-luvas.jpg")

# Tanque combustível
if "17-tanque" in downloaded:
    save_image(downloaded["17-tanque"], BASE / "17-tanque.jpg")

# ABS
if "20-abs" in downloaded:
    save_image(downloaded["20-abs"], BASE / "20-abs.jpg")

# Recortes do interior Passat B7 Variant (Wikimedia)
for name, ratios in INTERIOR_CROPS.items():
    src_key = name if name in downloaded else None
    if not src_key:
        continue
    img = downloaded[src_key]
    w, h = img.size
    box = (int(w * ratios[0]), int(h * ratios[1]), int(w * ratios[2]), int(h * ratios[3]))
    save_crop(img, box, BASE / f"{name}.jpg")
    print(f"  interior crop OK: {name}")

print("Imagens geradas em", BASE)
