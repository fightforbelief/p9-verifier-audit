# Certifying best-of-N verifier comparisons with fallible answer judgments

Yunjie Guo and Hanqing Yang · Independent Researcher, Suzhou, China

[Read the manuscript](paper/main.pdf) · [Study protocol and dated amendments](PROTOCOL.md) · [Machine-readable results](reports/)

When two mathematical verifiers see the same candidate solutions, how many final-answer grades determine their ordering? This study computes an answer's exact chance of winning under each verifier and directs review toward the largest differences. It gives sharp bounds with missing or fallible grades, the fewest grade changes that erase a lead, and a minimax allocation for two review tiers with different costs.

At eight draws on AceMath MATH-500, 437 answer checks certify the 72B model's 1.21-point lead if returned checks are correct. Reviewing individual responses with the same priority takes 11,942 checks. Thirteen adverse answer-grade changes could erase the fully graded lead. These are finite-pool replay results. The grades come from the public archives. Across 1,390,800 eligible responses, the Lightman release contained one group of 67 responses with the same extracted answer but conflicting grades. We report the original response-level comparison and the sensitivity to assigning one answer-level grade. Reviewer time and future model performance were outside the estimand.

## Reproduce the tables

Research computation uses Python 3.12.10 and the standard library on Windows. From the project root, create a project-local environment once. Each run reuses this environment. Public releases provide both scores and final-answer grades. Downloads require network access, curl, and roughly 2.3 GB of source data plus temporary space. The resumable downloader keeps an additional copy in chunks.

```powershell
py -3.12 -m venv .venv
$py = '.\.venv\Scripts\python.exe'
& $py fetch_data.py ace
& $py fetch_large.py
.\Run-Study.ps1 ace
.\Run-Study.ps1 lightman
& $py tie_sensitivity.py lightman gsm8k math500 minerva_math gaokao2023en olympiadbench college_math mmlu_stem
& $py question_review.py lightman gsm8k math500 minerva_math gaokao2023en olympiadbench college_math mmlu_stem
& $py verify_reports.py
```

Each command should finish successfully before starting the next. For an already downloaded official OpenAI blob, place it at `data/scored-test-samples.jsonl`. The main runner checks the publisher's digest. An optional transport route runs `project_input.py SOURCE data/lightman-fields.jsonl.gz` to project five fields and record source and content hashes before copying to another machine. For AceMath the downloader pins the [dataset revision](https://huggingface.co/datasets/nvidia/AceMath-RewardBench/tree/4dcc58ef82ddc5915be91f9b4f2c18c8b503a0e4). The [OpenAI evaluator](https://github.com/openai/prm800k/blob/main/prm800k/eval/eval.py) specifies the full-attempt denominator.

Per-subject JSON files give integer-derived results, input and script digests, the interpreter version and platform. The CSV files hold one row per question and budget, with a hashed problem identifier. The `ties-*.json` files give full-grade sensitivity to tie priority. The `question-*.json` files count whole-problem checks and the minimum number of problems containing adverse grade changes. Raw solutions stay at the providers. Source material remains subject to its original terms. To rebuild the paper's presentation from returned reports, use Python with Matplotlib 3.10 and Tectonic.

```sh
cd paper
python display.py
tectonic main.tex
```

## Audit a new pair without exposing labels to the planner

Provide a JSONL file with one record per problem and two scores per eligible candidate. The example is a tiny fixture. Use the same nonempty unit key for answers that must share a grade, or unique response IDs for individual reviews. Leave unavailable attempts out of the candidate list and include them in the declared slot count. All questions in this CLI invocation use the same number of slots.

```json
{"problem":"example","candidates":[{"unit":"2","a":3,"b":1},{"unit":"2","a":2,"b":2},{"unit":"3","a":1,"b":3}]}
```

```sh
python review.py pools.jsonl --slots 3 --draws 3 --budget 2 --errors 0 > plan.jsonl
python review.py pools.jsonl --slots 3 --draws 3 --reviews returned.jsonl --errors 0
```

The plan contains a problem, unit, assigned tier and blank grade. Enter `true` or `false` for completed reviews in `returned.jsonl` and omit unreviewed entries. The evaluator accepts partial returns and reports exact rational endpoints plus a sign decision. With two grades of true for “2” and false for “3”, the interval is [1, 1]. Allowing one erroneous ordinary judgment changes it to [0, 1]. Gold-tier judgments are assumed correct. The `--gold-cost` option sets their price in ordinary-review credits.

The theory gives the smallest worst-case interval width among fixed designs for one prespecified contrast and budget. The sign stopping count depends on the grades actually revealed. Exact-string pooling applies to final-answer grading. A proof-level audit needs units that can meaningfully share a proof grade.
