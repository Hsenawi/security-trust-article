"""Write the results tables from the analysis outputs in ~/tool-trust-research (no hand-copied numbers).
Run with the research repo's venv: python tables/make_results_tables.py
Writes tables/results_contrasts.tex (corrected scorer, primary) and tables/results_contrasts_v1.tex (original)."""
from pathlib import Path
import pandas as pd

R = Path.home() / "tool-trust-research"
ARMS = [("Qwen, D1", "defense_qwen4b", "analysis_pairs_64", "D164"),
        ("Qwen, D2", "defense_qwen4b", "analysis_pairs_64", "D264"),
        ("Llama, Meta-SecAlign", "defense_llama8b", "analysis_pairs_64", "D64"),
        ("Llama, SecPO", "defense_llama8b", "analysis_pairs_64_secpo", "P64")]
SEATS = ["user", "tool", "system", "doc", "input"]
NAMES = {"doc": "document"}


def cell(r):
    star = r.p_holm < 0.05 and (r.lo > 0 or r.hi < 0)
    f = lambda v: f"{100 * v:+.1f}".replace("-", "$-$")
    return f"{f(r['diff'])} [{f(r.lo)}, {f(r.hi)}]" + ("$^{*}$" if star else "")


def table(suffix, label, caption, subset="main"):
    lines = [r"\begin{table}[ht]", r"\centering", r"\small", r"\setlength{\tabcolsep}{3pt}", rf"\caption{{{caption}}}", rf"\label{{{label}}}",
             r"\begin{tabular}{llrlrl}", r"\toprule",
             r" & & \multicolumn{2}{c}{Correct-note uptake, unknown} & \multicolumn{2}{c}{Wrong-note adoption, known} \\",
             r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}",
             r"Arm & Seat & Base, \% & D $-$ B, pp [95\%] & Base, \% & D $-$ B, pp [95\%] \\", r"\midrule"]
    for k, (name, run, f, arm) in enumerate(ARMS):
        t = pd.read_csv(R / "outputs" / (run + suffix) / f"{f}.csv")
        t = t[(t.subset == subset) & (t.arm == arm)].set_index(["outcome", "seat"])
        for i, s in enumerate(SEATS):
            c, w = t.loc[("correct_uptake", s)], t.loc[("wrong_adopt", s)]
            lines.append(f"{name if i == 0 else ''} & {NAMES.get(s, s)} & {100 * c.rate_B:.1f} & {cell(c)} & "
                         f"{100 * w.rate_B:.1f} & {cell(w)} \\\\")
        if k < len(ARMS) - 1:
            lines.append(r"\addlinespace")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


out = Path(__file__).parent
out.joinpath("results_contrasts.tex").write_text(table("_v2", "tab:contrasts",
    r"Defended minus base by seat, corrected scorer. $^{*}$: interval excludes zero and Holm $p<0.05$."))
out.joinpath("results_contrasts_v1.tex").write_text(table("", "tab:contrasts-v1",
    r"As Table~\ref{tab:contrasts}, original scorer."))
out.joinpath("results_contrasts_full.tex").write_text(table("_v2", "tab:contrasts-full",
    r"As Table~\ref{tab:contrasts}, on all 1,600 base-defined items per pair.", subset="B_strata"))


def recall_table():
    t = pd.read_csv(R / "outputs" / "defense_qwen4b_v2" / "analysis_pairs_64.csv")
    t = t[(t.subset == "main") & (t.outcome == "correct_uptake")].set_index(["arm", "seat"])
    lines = [r"\begin{table}[ht]", r"\centering", r"\small",
             r"\caption{Pair~A, correct notes on unknown items: re-call rate and uptake among direct answers, in \%. Descriptive.}",
             r"\label{tab:recalls}", r"\begin{tabular}{lrrrrrr}", r"\toprule",
             r" & \multicolumn{3}{c}{Re-call rate} & \multicolumn{3}{c}{Uptake among direct answers} \\",
             r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}", r"Seat & Base & D1 & D2 & Base & D1 & D2 \\", r"\midrule"]
    for s in SEATS:
        b, d1, d2 = t.loc[("D164", s)], t.loc[("D164", s)], t.loc[("D264", s)]
        lines.append(f"{NAMES.get(s, s)} & {100 * b.recall_B:.1f} & {100 * d1.recall_D:.1f} & {100 * d2.recall_D:.1f} & "
                     f"{100 * b.nonrecall_B:.1f} & {100 * d1.nonrecall_D:.1f} & {100 * d2.nonrecall_D:.1f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


out.joinpath("results_recalls.tex").write_text(recall_table())


def merged_table():
    """Merged-before-quantization arms (amendments 6 and 9), corrected scorer, main subset."""
    arms = [("Qwen, D1 merged", "defense_qwen4b", "analysis_pairs_64_merged", "D1m64"),
            ("Qwen, D2 merged", "defense_qwen4b", "analysis_pairs_64_merged", "D2m64"),
            ("Meta-SecAlign merged", "defense_llama8b", "analysis_pairs_64_merged", "M64")]
    global ARMS
    saved, ARMS = ARMS, arms
    try:
        return table("_v2", "tab:contrasts-merged",
                     r"As Table~\ref{tab:contrasts}, with each LoRA defence merged into its base before quantization.")
    finally:
        ARMS = saved


out.joinpath("results_contrasts_merged.tex").write_text(merged_table())
print("wrote", [p.name for p in out.glob("results_contrasts*.tex")])


def pair_c_table():
    """Pair C (amendment 8): ISE and ASIDE minus vanilla, main subset; rates in pp, d' and c as differences."""
    t = pd.read_csv(R / "outputs" / "pair_c" / "analysis_pair_c.csv")
    s = pd.read_csv(R / "outputs" / "pair_c" / "analysis_pair_c_sdt.csv")
    t, s = t[t.subset == "main"].copy(), s[s.subset == "main"].copy()

    def holm2(frame, pcol, keys):  # Holm across the two defended arms, as in the registered C1 to C4 rule
        frame[pcol + "_holm"] = 1.0
        for _, g in frame.groupby(keys):
            ps = g[pcol].sort_values()
            adj = [min(1.0, max((len(ps) - r) * v for r, v in enumerate(ps.values[:k + 1]))) for k in range(len(ps))]
            frame.loc[ps.index, pcol + "_holm"] = adj
        return frame
    t = holm2(t, "p", ["outcome", "seat"]).rename(columns={"p_holm": "p_holm"})
    s = holm2(holm2(s, "dd_p", ["seat"]), "dc_p", ["seat"])
    t, s = t.set_index(["outcome", "arm", "seat"]), s.set_index(["arm", "seat"])
    f = lambda v: f"{v:+.2f}".replace("-", "$-$")
    lines = [r"\begin{table}[ht]", r"\centering", r"\small",
             r"\caption{Pair~C: ISE and ASIDE minus the vanilla baseline, corrected scorer. Rates in percentage points; $d'$ and $c$ as differences. $^{*}$: interval excludes zero and Holm $p<0.05$.}",
             r"\label{tab:pairc}", r"\begin{tabular}{llrll}", r"\toprule",
             r"Seat & Measure & Vanilla & ISE $-$ vanilla [95\%] & ASIDE $-$ vanilla [95\%] \\", r"\midrule"]
    for k, seat in enumerate(["data", "instruction"]):
        for oc, name in (("correct_uptake", "correct-note uptake, \\%"), ("wrong_adopt", "wrong-note adoption, \\%")):
            i, a = t.loc[(oc, "Cise", seat)], t.loc[(oc, "Caside", seat)]
            lines.append(f"{seat if oc == 'correct_uptake' else ''} & {name} & {100 * i.rate_B:.1f} & {cell(i)} & {cell(a)} \\\\")
        for m, name in (("dd", "$d'$"), ("dc", "$c$")):
            i, a = s.loc[("Cise", seat)], s.loc[("Caside", seat)]
            base = i.dprime_B if m == "dd" else i.c_B
            st = lambda r: "$^{*}$" if r[m + "_p_holm"] < 0.05 and (r[m + "_lo"] > 0 or r[m + "_hi"] < 0) else ""
            lines.append(f" & {name} & {f"{base:.2f}".replace("-", "$-$")} & {f(i[m])} [{f(i[m + '_lo'])}, {f(i[m + '_hi'])}]{st(i)} & {f(a[m])} [{f(a[m + '_lo'])}, {f(a[m + '_hi'])}]{st(a)} \\\\")
        if k == 0:
            lines.append(r"\addlinespace")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


out.joinpath("results_pair_c.tex").write_text(pair_c_table())
