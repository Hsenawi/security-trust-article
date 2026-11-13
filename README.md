# Message Roles and Factual Uptake: A Paired Study of Prompt-Injection Defences

Scripts that build the figures and tables of the study, which asks whether training a language model
against prompt injection changes how it uses correct and wrong facts that arrive through the user turn,
the system message, a document block, the `input` role or a tool result.

The manuscript is under review and is not included here.

## Contents
- `figures/`: scripts for the figures (`make_fig_contrasts.py`, `make_fig_recalls.py`, `make_fig_sdt.py`).
- `tables/`: scripts for the result tables (`make_results_tables.py`, `make_summary_table.py`,
  `make_injection_ext_table.py`).

The scripts read the analysis outputs of the study's experiment code from `~/tool-trust-research/outputs`
and write LaTeX tables or PDF figures. No number is copied by hand.

## License
MIT, see `LICENSE`.
