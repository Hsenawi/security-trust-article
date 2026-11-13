"""Figure 3: Pair A, correct notes on unknown items: re-call rate and uptake among direct answers by seat,
corrected scorer, main subset (descriptive, amendment 5l). Reads analysis_pairs_64.csv from ~/tool-trust-research.
Run with the research repo's venv: python figures/make_fig_recalls.py  ->  figures/fig_recalls.pdf
Colours match Figures 1 and 2 (D1 blue circle, D2 orange square); the base is a neutral hollow circle."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

R = Path.home() / "tool-trust-research" / "outputs" / "defense_qwen4b_v2" / "analysis_pairs_64.csv"
SEATS = ["user", "tool", "system", "doc", "input"]
LABEL = {"doc": "document"}
INK, MUTED, GRID = "#101418", "#5b646d", "#e1e0d9"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": INK})
t = pd.read_csv(R)
t = t[(t.subset == "main") & (t.outcome == "correct_uptake")].set_index(["arm", "seat"])
series = [("Qwen base", lambda s, k: t.loc[("D164", s), k + "_B"], dict(marker="o", mfc="white", mec=INK, color=INK), -0.2),
          ("Qwen D1", lambda s, k: t.loc[("D164", s), k + "_D"], dict(marker="o", color="#2a78d6", mec="white"), 0.0),
          ("Qwen D2", lambda s, k: t.loc[("D264", s), k + "_D"], dict(marker="s", color="#eb6834", mec="white"), 0.2)]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4), sharey=True)
for ax, (k, title) in zip(axes, [("recall", "Re-call rate"), ("nonrecall", "Uptake among direct answers")]):
    for name, get, style, dy in series:
        xs = [100 * get(s, k) for s in SEATS]
        ax.plot(xs, [i + dy for i in range(len(SEATS))], ls="none", ms=6, mew=1.1, zorder=3, label=name, **style)
    ax.grid(axis="x", color=GRID, lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xlim(-3, 103)
    ax.set_title(title, fontsize=9, color=INK, loc="left")
    ax.set_xlabel("% of replies to correct notes, unknown items" if k == "recall" else "% of direct answers that give the gold answer")
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
axes[0].set_yticks(range(len(SEATS)), [LABEL.get(s, s) for s in SEATS])
axes[0].invert_yaxis()
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0), handletextpad=0.3, columnspacing=1.6)
fig.tight_layout(rect=(0, 0, 1, 0.92))
out = Path(__file__).parent / "fig_recalls.pdf"
fig.savefig(out); fig.savefig(out.with_suffix(".png"), dpi=160)
print("wrote", out)
