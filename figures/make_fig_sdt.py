"""Figure 2: change in discrimination (d') and bias (c) on unknown items, defended minus base, corrected scorer,
main subset, all replies (amendment 7, descriptive). Reads analysis_sdt*.csv from ~/tool-trust-research.
Run with the research repo's venv: python figures/make_fig_sdt.py  ->  figures/fig_sdt.pdf"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

R = Path.home() / "tool-trust-research" / "outputs"
ARMS = [  # (label, run, file, arm, colour, marker, hollow); hollow = weights merged before quantization
    ("Qwen D1", "defense_qwen4b_v2", "analysis_sdt_64", "D164", "#2a78d6", "o", False),
    ("Qwen D1, merged", "defense_qwen4b_v2", "analysis_sdt_64_merged", "D1m64", "#2a78d6", "o", True),
    ("Qwen D2", "defense_qwen4b_v2", "analysis_sdt_64", "D264", "#eb6834", "s", False),
    ("Qwen D2, merged", "defense_qwen4b_v2", "analysis_sdt_64_merged", "D2m64", "#eb6834", "s", True),
    ("Llama Meta-SecAlign", "defense_llama8b_v2", "analysis_sdt_64", "D64", "#1baf7a", "^", False),
    ("Llama Meta-SecAlign, merged", "defense_llama8b_v2", "analysis_sdt_64_merged", "M64", "#1baf7a", "^", True),
    ("Llama SecPO (merged)", "defense_llama8b_v2", "analysis_sdt_64_secpo", "P64", "#eda100", "D", True)]
SEATS = ["user", "tool", "system", "doc", "input"]
LABEL = {"doc": "document"}
PANELS = [("dd", "Discrimination, change in d′"), ("dc", "Bias, change in c (negative = more liberal)")]
INK, MUTED, GRID = "#101418", "#5b646d", "#e1e0d9"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": INK})
fig, axes = plt.subplots(1, 2, figsize=(7.0, 4.6), sharey=True)
offs = [-0.36, -0.24, -0.12, 0.0, 0.12, 0.24, 0.36]
for ax, (m, title) in zip(axes, PANELS):
    for i, s in enumerate(SEATS):
        if s in ("tool", "input"):
            ax.axhspan(i - 0.45, i + 0.45, color=GRID, alpha=0.55, lw=0, zorder=0)
    for (name, run, f, arm, col, mk, hollow), dy in zip(ARMS, offs):
        t = pd.read_csv(R / run / f"{f}.csv")
        t = t[(t.subset == "main") & (t.set == "all") & (t.arm == arm)].set_index("seat")
        for i, s in enumerate(SEATS):
            r = t.loc[s]
            ax.plot([r[m + "_lo"], r[m + "_hi"]], [i + dy] * 2, color=col, lw=1.3, solid_capstyle="round", zorder=2)
            ax.plot(r[m], i + dy, mk, color=col, ms=4.6 if hollow else 5.6, mfc="white" if hollow else col, mec=col if hollow else "white",
                    mew=1.1 if hollow else 0.8, zorder=3, label=name if i == 0 else None)
    ax.axvline(0, color=MUTED, lw=1, zorder=1)
    ax.grid(axis="x", color=GRID, lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title(title, fontsize=9, color=INK, loc="left")
    ax.set_xlabel("Defended minus base")
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
axes[0].set_yticks(range(len(SEATS)), [LABEL.get(s, s) for s in SEATS])
axes[0].invert_yaxis()
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.0), fontsize=7.5, handletextpad=0.3, columnspacing=1.4)
fig.tight_layout(rect=(0, 0, 1, 0.88))
out = Path(__file__).parent / "fig_sdt.pdf"
fig.savefig(out); fig.savefig(out.with_suffix(".png"), dpi=160)
print("wrote", out)
