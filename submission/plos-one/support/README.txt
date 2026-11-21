S1 File. Analysis code, protocol and numerical results
Certifying best-of-N verifier comparisons with fallible answer judgments

Start in this directory after extracting the archive. The recorded research environment
was Windows with Python 3.12.10. The numerical analysis uses the standard library.
The published archive verdict measures final-answer agreement. No human reviews were collected.

Inspect the results without downloading the source pools
  python verify_reports.py
This verifies input provenance across returned reports, script checksums, shared
contrasts, per-question aggregates, and the first seed of the sampling comparison.
The exact analysis code corresponds to commit 1845d771360fb34dfee2537d614103ea3d598bb3
of https://github.com/fightforbelief/p9-verifier-audit .

Results map
  Tables 1 and 2: reports/COLLECTION.json, results[N].answer and .candidate.
    A and B are expected accuracies, and gap is A minus B. N is the number of
    generation slots sampled without replacement. Lightman compares the process
    and outcome verifiers; AceMath compares the 72B and 7B reward models.
    units counts distinct review units. erase counts adverse flips to erase the
    lead; policies.difference.sign["0"] counts reliable checks until the sign is
    fixed. A null stopping count denotes an unresolved comparison.
    tiers stores the original 96 budget/price cells (a hypothetical five-error ceiling).
  Fig 1: Fig1_values.csv, one row per collection. Each value is the fraction of
    initial interval width left after 10% of answer units are checked at N=8.
    make_figure.py regenerates both this CSV and Fig1.tif using Matplotlib 3.10,
    Pillow and Arial. It reads the JSON and does not re-run the study.
  Table 3: reports/grader-replay.json, results[N].graders[rule].
    reviewed_disagreements compares the provisional rule with the archive in the
    reviewed set; calibration_errors is the sampled count; remaining_upper is
    the bound after removing that sample. policies.conditional.endpoints is the
    interval after adjudication. match_width is the all-confirming-branch width.
  Table 4: reports/sampling-control.json, results[N]. Each of 32 seed offsets
    appears once per rule. pps and upgrade give lower and upper limits for direct
    sampling and calibrated upgrades. magnitude gives the comparison allocation.
    unique counts distinct sampled units in the with-replacement design.
  Intervals, gaps and widths in JSON are in accuracy units. Multiply by 100 for
    percentage points in the manuscript. Counts and the normalized Fig 1 ratios
    are unscaled. Each six-cell confidence statement applies within one method
    and seed; seeds are repeated draws on a single fixed collection.
  reports/COLLECTION_problems.csv: one row per problem and generation budget.
    problem_id_hash identifies the problem in that collection; N, eligible and
    answer_units are counts; candidate_gap is the response-level contribution
    for that problem before averaging over problems.
  reports/ties-*.json: min/max over extreme tie orders plus forward/reverse order.
  reports/question-*.json: whole-question stopping counts, erasure counts and gap.
  PROTOCOL.md records the original design and timing of amendments.

Reproduce from source data (PowerShell from the extracted directory)
  py -3.12 -m venv .venv
  $py = '.\.venv\Scripts\python.exe'
  & $py fetch_data.py ace
  & $py fetch_large.py
  .\Run-Study.ps1 ace
  .\Run-Study.ps1 lightman
  & $py tie_sensitivity.py lightman gsm8k math500 minerva_math gaokao2023en olympiadbench college_math mmlu_stem
  & $py question_review.py lightman gsm8k math500 minerva_math gaokao2023en olympiadbench college_math mmlu_stem
  & $py grader_replay.py
  & $py sampling_control.py
  & $py verify_reports.py
The runner executes the unit tests before analysis. Allow at least 5 GB local space
for the inputs, downloads in chunks and reports. Wait for each step to succeed.
The data sources are the public provider files. The full OpenAI blob includes
the reference strings used by the two provisional graders.
  https://openaipublic.blob.core.windows.net/process-supervision/scored-test-samples.jsonl
  SHA-256 46a01478dceefe8194304f9e2db92fedefab8c8cc47033a9d7e059f3b18c5f82
  https://huggingface.co/datasets/nvidia/AceMath-RewardBench/tree/4dcc58ef82ddc5915be91f9b4f2c18c8b503a0e4
The per-collection JSON supplies input digests. fetch_data.py lists the precise
AceMath files and shards. The two data providers host the full original scores.
