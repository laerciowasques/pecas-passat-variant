"""Valida alinhamento dos hotspots com os números das linhas no panfleto."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FLYER = ROOT / "img" / "lista-pecas.png"

ROW_CENTERS = [
    515, 573, 602, 659, 692, 754, 783, 825, 868, 909, 952, 1000, 1033, 1086, 1110, 1155, 1200, 1225,
    1255, 1285,
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
        limit = 10 if i in {1, 2, 19, 20} else 18

        if max(scores) < 5:
            failures.append(f"linha {i:02d}: sem número detectado (centro={center})")
        elif abs(offset) > limit:
            failures.append(f"linha {i:02d}: desvio {offset:+d}px (centro={center}, melhor={best_y})")

        if i > 1:
            prev_bottom = ROW_CENTERS[i - 2] + ROW_HALF_H
            overlap = prev_bottom - top
            if overlap > 13:
                failures.append(
                    f"linha {i-1:02d}/{i:02d}: sobreposição de {overlap}px (tops {top}, prev_bottom {prev_bottom})"
                )

    print("Linhas críticas:")
    for i in [1, 2, 19, 20]:
        center = ROW_CENTERS[i - 1]
        print(f"  {i:02d}: y {center - ROW_HALF_H}-{center + ROW_HALF_H} (centro {center})")

    if failures:
        print("FALHA na verificação:")
        for item in failures:
            print(f"  - {item}")
        raise SystemExit(1)

    print("OK: 20 linhas alinhadas sem sobreposição crítica.")
    print(f"    faixa coberta: y {ROW_CENTERS[0] - ROW_HALF_H}–{ROW_CENTERS[-1] + ROW_HALF_H}")


if __name__ == "__main__":
    main()
