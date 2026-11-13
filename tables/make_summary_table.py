"""Summary table by defence and data role (descriptive), written from the analysis outputs in ~/tool-trust-research.
No hand-copied numbers. Run with the research repo's venv: python tables/make_summary_table.py
Writes tables_my_style/results_summary.tex. The 'reading' column applies a fixed rule to the two primary contrasts:
  uptake lower* and adoption lower*      -> less use of true and false notes
  adoption lower*, uptake not lower*     -> protection, uptake kept
  uptake lower*, adoption not lower*     -> cost without protection
  otherwise                              -> no clear change
(* = 95% interval excludes zero and Holm p < 0.05, as in the contrast tables.)"""
from pathlib import Path
import pandas as pd

R = Path.home() / "tool-trust-research" / "outputs"
OUT = Path(__file__).resolve().parent.parent / "tables_my_style" / "results_summary.tex"
# label, contrasts csv, sdt csv, arm, injection csv, injection arm, seats
AB = [("D1", "defense_qwen4b_v2/analysis_pairs_64", "defense_qwen4b_v2/analysis_sdt_64", "D164", "injection/analysis_pairA", "QD1"),
      ("D2", "defense_qwen4b_v2/analysis_pairs_64", "defense_qwen4b_v2/analysis_sdt_64", "D264", "injection/analysis_pairA", "QD2"),
      ("Meta-SecAlign", "defense_llama8b_v2/analysis_pairs_64", "defense_llama8b_v2/analysis_sdt_64", "D64", "injection/analysis_pairB", "LD"),
      ("SecPO", "defense_llama8b_v2/analysis_pairs_64_secpo", "defense_llama8b_v2/analysis_sdt_64_secpo", "P64", "injection/analysis_pairB", "LP")]
C = [("ISE", "Cise"), ("ASIDE", "Caside")]


def num(v, d=1):
    return f"{v:+.{d}f}".replace("-", "$-$")


def reading(up, up_s, ad, ad_s):
    lo_up, lo_ad = up_s and up < 0, ad_s and ad < 0
    if lo_up and lo_ad:
        return "less use of true and false notes"
    if lo_ad:
        return "protection, uptake kept"
    if lo_up:
        return "cost without protection"
    return "no clear change"


rows = []
for name, cf, sf, arm, jf, jarm in AB:
    c = pd.read_csv(R / f"{cf}.csv"); c = c[(c.subset == "main") & (c.arm == arm)].set_index(["outcome", "seat"])
    s = pd.read_csv(R / f"{sf}.csv"); s = s[(s.subset == "main") & (s.set == "all") & (s.arm == arm)].set_index("seat")
    j = pd.read_csv(R / f"{jf}.csv"); j = j[(j.test == "S1") & (j.arm == jarm)].set_index("seat")
    for i, seat in enumerate(["input", "tool"]):
        u, w = c.loc[("correct_uptake", seat)], c.loc[("wrong_adopt", seat)]
        us = bool(u.p_holm < 0.05 and (u.lo > 0 or u.hi < 0)); ws = bool(w.p_holm < 0.05 and (w.lo > 0 or w.hi < 0))
        rows.append((name if i == 0 else "", r"\texttt{input}" if seat == "input" else "tool", j.loc[seat, "x"], j.loc[seat, "y"],
                     100 * u["diff"], us, 100 * w["diff"], ws, s.loc[seat, "dd"], s.loc[seat, "dc"]))
c = pd.read_csv(R / "pair_c/analysis_pair_c.csv"); c = c[(c.subset == "main") & (c.seat == "data")]
s = pd.read_csv(R / "pair_c/analysis_pair_c_sdt.csv"); s = s[(s.subset == "main") & (s.seat == "data")].set_index("arm")
j = pd.read_csv(R / "injection/analysis_pairC.csv"); j = j[(j.test == "S1") & (j.seat == "data")].set_index("arm")
for name, arm in C:
    star = {}
    for o in ["correct_uptake", "wrong_adopt"]:
        t = c[c.outcome == o].sort_values("p").reset_index(drop=True)  # Holm across the two defended arms
        ph, prev = {}, 0.0
        for k, r in t.iterrows():
            prev = max(prev, min(1.0, (len(t) - k) * r.p)); ph[r.arm] = prev
        r = t[t.arm == arm].iloc[0]
        star[o] = (100 * r["diff"], bool(ph[arm] < 0.05 and (r.lo > 0 or r.hi < 0)))
    rows.append((name, "data part", j.loc[arm, "x"], j.loc[arm, "y"], star["correct_uptake"][0], star["correct_uptake"][1],
                 star["wrong_adopt"][0], star["wrong_adopt"][1], s.loc[arm, "dd"], s.loc[arm, "dc"]))

L = [r"% Written by tables/make_summary_table.py from ~/tool-trust-research/outputs; do not edit by hand.",
     r"\begin{table}[ht]", r"\centering", r"\small", r"\setlength{\tabcolsep}{4pt}",
     r"\caption{Summary by defence and data role, primary configurations, corrected scorer. Attack success is the share of injected instructions followed, base and defended. Changes are defended minus base: correct-note uptake on unknown items and wrong-note adoption on known items in percentage points, $d'$ and $c$ on unknown items. $^{*}$: interval excludes zero and Holm $p<0.05$. The reading applies one fixed rule to the two starred columns and is descriptive.}",
     r"\label{tab:summary}", r"\begin{adjustbox}{max width=\textwidth}", r"\begin{tabular}{llrrrrrrl}", r"\toprule",
     r" & & \multicolumn{2}{c}{Attack success, \%} & \multicolumn{4}{c}{Defended minus base} & \\",
     r"\cmidrule(lr){3-4}\cmidrule(lr){5-8}",
     r"Defence & Role & base & defended & uptake & adoption & $d'$ & $c$ & Reading \\", r"\midrule"]
for k, (n, seat, x, y, up, us, ad, as_, dd, dc) in enumerate(rows):
    if n and k:
        L.append(r"\addlinespace")
    L.append(f"{n} & {seat} & {x:.1f} & {y:.1f} & {num(up)}{'$^{*}$' if us else ''} & {num(ad)}{'$^{*}$' if as_ else ''} & "
             f"{num(dd, 2)} & {num(dc, 2)} & {reading(up, us, ad, as_)} \\\\")
L += [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}", r"\end{table}"]
OUT.write_text("\n".join(L) + "\n")
print(OUT.read_text())
