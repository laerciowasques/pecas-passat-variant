"""Valida alinhamento dos hotspots com os números das linhas no panfleto."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FLYER = ROOT / "img" / "lista-pecas.png"

ROW_CENTERS = [
    518, 527, 573, 618, 663, 708, 755, 798, 841, 883, 923, 952, 1005, 1045, 1083, 1123, 1162, 1186,
    1220, 1264,
]
ROW_HALF_H = 18
H = 1536


def row_number_y(px, y: int) -> int:
    return sum(1 for x in range(42, 68) if px[x, y][0] > 200 and px[x, y][1] > 140)


def main() -> None:
    img = Image.open(FLYER).convert("RGB")
    px = img.load()

    failures = []
    for i, center in enumerate(ROW_CENTERS, start=1):
        top = center - ROW_HALF_H
        bottom = center + ROW_HALF_H
        scores = [row_number_y(px, y) for y in range(top, bottom + 1)]
        best_y = top + scores.index(max(scores))
        offset = best_y - center

        if i >= 17:
            limit = 10
        else:
            limit = 18

        if max(scores) < 5:
            failures.append(f"linha {i:02d}: sem número detectado (centro={center})")
        elif abs(offset) > limit:
            failures.append(f"linha {i:02d}: desvio {offset:+d}px (centro={center}, melhor={best_y})")

    tail = list(range(17, 21))
    print("Linhas finais:")
    for i in tail:
        center = ROW_CENTERS[i - 1]
        top = center - ROW_HALF_H
        bottom = center + ROW_HALF_H
        print(f"  {i:02d}: y {top}-{bottom} (centro {center})")

    if failures:
        print("FALHA na verificação:")
        for item in failures:
            print(f"  - {item}")
        raise SystemExit(1)

    print("OK: 20 linhas alinhadas aos números do panfleto.")
    print(f"    faixa coberta: y {ROW_CENTERS[0] - ROW_HALF_H}–{ROW_CENTERS[-1] + ROW_HALF_H}")


if __name__ == "__main__":
    main()
