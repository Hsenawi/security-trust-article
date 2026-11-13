"""Tables of the amendment-21 injection check, written from the analysis outputs in ~/tool-trust-research.
No hand-copied numbers. Run: python3 tables/make_injection_ext_table.py
Writes tables_my_style/results_injection_ext.tex (main text: pooled forms, tuned wording, any wording, reserved-token form)
and tables_my_style/results_injection_forms.tex (supplement: attack success per form, every arm and seat)."""
import csv
import json
from pathlib import Path

R = Path.home() / "tool-trust-research" / "outputs" / "injection_ext"
T = Path(__file__).resolve().parent.parent / "tables_my_style"
PAIRS = [("A", "A, Qwen3-4B", [("QD1", "D1, adapter"), ("QD1m", "D1, merged"), ("QD2", "D2, adapter"), ("QD2m", "D2, merged")]),
         ("B", "B, Llama-3.1-8B", [("LD", "Meta-SecAlign, adapter"), ("LM", "Meta-SecAlign, merged"), ("LP", "SecPO")]),
         ("C", "C, Qwen2.5-7B", [("Cise", "ISE"), ("Caside", "ASIDE")])]
BASES = {"A": ("QB", "Base"), "B": ("LB", "Base"), "C": ("Cvan", "Vanilla")}
SEAT = {"input": r"\texttt{input}", "tool": "tool", "data": "data"}
FORMS = [("escape", "Escape"), ("spoof_text", "Fake turn"), ("combined", "Combined"), ("spanish", "Spanish"),
         ("other_task", "Other target"), ("start", "At start"), ("passage", "Passage"), ("spoof_tokens", "Reserved tokens")]


def f1(v):
    return f"{float(v):.1f}"


def main_table():
    out = []
    worst = 0.0
    for p, plabel, arms in PAIRS:
        rows = list(csv.DictReader(open(R / f"analysis_pair{p}.csv")))
        get = {(r["test"], r["arm"], r["seat"]): r for r in rows if r["test"] != "S2b"}
        first_pair = True
        for arm, alabel in arms:
            seats = [s for s in ("input", "tool", "data") if ("S1b", arm, s) in get]
            for i, s in enumerate(seats):
                b, t, a, k = (get[(x, arm, s)] for x in ("S1b", "S1t", "any", "spoof_tokens"))
                assert t["pool"] == a["pool"] and float(b["diff"]) < 0 and float(t["diff"]) < 0
                worst = max(worst, float(b["p_holm"]), float(t["p_holm"]))
                cells = [plabel if first_pair else "", alabel if i == 0 else "", SEAT[s], t["pool"],
                         f1(b["x"]), f1(b["y"]), f1(t["x"]), f1(t["y"]), f1(a["x"]), f1(a["y"]), f1(k["x"]), f1(k["y"])]
                out.append(" & ".join(cells) + r" \\")
                first_pair = False
        out.append(r"\addlinespace")
    out.pop()
    assert worst < 0.05, worst
    head = r"""% Written by tables/make_injection_ext_table.py from ~/tool-trust-research/outputs/injection_ext; do not edit by hand.
\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{4pt}
\caption{Attack success under the harder injection attacks, in percent, base and defended. Seven forms: pooled, 1,456 prompts per seat. Tuned: the wording chosen for each configuration on half of the items, measured on the other 106. Any: at least one wording of the pool succeeded on the item, 208 items. Tokens: the form built from the template's reserved tokens, 208 prompts. Every defended rate under the seven forms and the tuned wording is lower than the base's with Holm-adjusted $p<0.05$.}
\label{tab:injection_ext}
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{lllrrrrrrrrr}
\toprule
 & & & & \multicolumn{2}{c}{Seven forms} & \multicolumn{2}{c}{Tuned} & \multicolumn{2}{c}{Any} & \multicolumn{2}{c}{Tokens} \\
\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}\cmidrule(lr){11-12}
Pair & Arm & Seat & Pool & Base & Def. & Base & Def. & Base & Def. & Base & Def. \\
\midrule
"""
    tail = r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\end{table}
"""
    (T / "results_injection_ext.tex").write_text(head + "\n".join(out) + tail)


def forms_table():
    out = []
    for p, plabel, arms in PAIRS:
        rates = json.load(open(R / f"analysis_pair{p}.json"))["rates"]
        first_pair = True
        for arm, alabel in [BASES[p]] + arms:
            for i, s in enumerate(rates[arm]):
                cells = [plabel if first_pair else "", alabel if i == 0 else "", SEAT[s]] + [f1(rates[arm][s][f]) for f, _ in FORMS]
                out.append(" & ".join(cells) + r" \\")
                first_pair = False
        out.append(r"\addlinespace")
    out.pop()
    head = r"""% Written by tables/make_injection_ext_table.py from ~/tool-trust-research/outputs/injection_ext; do not edit by hand.
\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{4pt}
\caption{Attack success for each form of the extended suite, in percent of 208 prompts per arm and seat. The form built from reserved tokens is not part of the pooled rate.}
\label{tab:injection_forms}
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{lll""" + "r" * len(FORMS) + r"""}
\toprule
Pair & Arm & Seat & """ + " & ".join(n for _, n in FORMS) + r""" \\
\midrule
"""
    tail = r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\end{table}
"""
    (T / "results_injection_forms.tex").write_text(head + "\n".join(out) + tail)


if __name__ == "__main__":
    main_table()
    forms_table()
