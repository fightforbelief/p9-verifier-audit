"""Render Fig 1 from returned JSON. Run from the extracted S1 File directory."""
from io import BytesIO
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import PercentFormatter
from PIL import Image

SUBJECTS = {
    "gsm8k": "GSM8K", "math500": "MATH-500", "minerva_math": "Minerva Math",
    "gaokao2023en": "Gaokao", "olympiadbench": "OlympiadBench",
    "college_math": "College Math", "mmlu_stem": "MMLU STEM", "lightman": "Lightman (MATH)",
}


def main():
    font_manager.findfont("Arial", fallback_to_default=False)
    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    rows = []
    for name, label in SUBJECTS.items():
        report = json.loads(Path(f"reports/{name}.json").read_text())
        answer = report["results"]["8"]["answer"]
        widths = [answer["policies"][k]["width10"] for k in ("difference", "pooled")]
        widths.append(answer["random_width10"])
        rows.append((label, *[w / answer["initial_width"] for w in widths]))

    with Path("Fig1_values.csv").open("w", newline="") as dest:
        writer = csv.writer(dest)
        writer.writerow(("collection", "mass_difference", "pooled_winner_mass", "uniform_expected"))
        writer.writerows(rows)

    fig, ax = plt.subplots(figsize=(6.8, 3.45))
    for column, (label, symbol, color) in enumerate([
        ("Mass difference", "o", "#14615d"), ("Pooled winner mass", "s", "#996029"),
        ("Uniform (expected)", "x", "#575e73"),
    ], start=1):
        ax.scatter([r[column] for r in rows], range(len(rows)), label=label,
                   marker=symbol, color=color, s=35, zorder=3)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(-0.025, 1.015)
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    ax.set_xlabel("Fraction of initial uncertainty width remaining")
    ax.grid(axis="x", linewidth=0.5, alpha=0.4)
    ax.spines[["right", "top", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.015), ncol=3,
              frameon=False, fontsize=9, handletextpad=0.3, columnspacing=1.1)
    fig.tight_layout()
    with BytesIO() as buffer:
        fig.savefig(buffer, format="png", dpi=300, facecolor="white")
        buffer.seek(0)
        with Image.open(buffer) as image:
            image.convert("RGB").save("Fig1.tif", compression="tiff_lzw", dpi=(300, 300))
    plt.close(fig)


if __name__ == "__main__":
    main()
