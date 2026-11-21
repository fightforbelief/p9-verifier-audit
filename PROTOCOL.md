# Finite-pool verifier replacement audit

Design recorded before computing comparison outcomes on 21 November 2026. This is a retrospective reanalysis of public graded pools. It is not an externally registered or blinded prospective experiment.

## Target

Compare process minus outcome reward in the Lightman et al. scored evaluation release and AceMath-72B-RM minus AceMath-7B-RM in all seven released subject sets. Give each problem equal weight within a set. A trial draws N slots uniformly without replacement and breaks maximum-score ties uniformly among tied candidates in the draw. For Lightman use 1,860 attempted slots per problem including discarded attempts, following the original runner. No eligible answer means zero credit. AceMath uses 64 slots. The fixed labels are the published final-answer grades.

## Endpoints and controls

At N=8, 32 and the full pool, compute the score gap, the sharp interval under arbitrary missing grades, the number of unit-cost grade reveals needed to certify the sign, and the fewest adverse grade changes needed to erase it after full review. The main audit unit is the pair of problem and exact extracted answer. Validate label consistency before pooling, including null or unavailable answer handling. Compare to treating each response as a separate unit. In case equal strings disagree in published grade, report the mismatch and present answer pooling only under an explicit reproducible resolution, with candidate-level analysis available independently.

Use absolute difference in selection mass for priority. Contrast with a symmetric pooled baseline ranking by the larger of the two selection masses, and uniform ordering (expected width). Report a 10% audit snapshot and sensitivity to one and five erroneous reviewed grades. Problem-level uncertainty for generalization, if reported, is supplementary to finite-pool certificates. A positive replacement gap or a specific level of savings is not required for reporting. Archive the input and executable hashes plus problem-level results. No fresh generation, benchmark tuning or API judgments are part of this design.

### Design extension before result inspection

The main comparison uses equally costly binary judgments. We additionally study a hypothetical second, error-free review tier. Its cost is two or five ordinary judgments. With up to five errors among ordinary reviews, compute the exact minimax allocation at 1% and 10% of the number of answer units in ordinary-review credits. Costs and error allowances are sensitivity parameters. The archive provides no labor-time or human error measurements.

### Follow-up after the AceMath replay

The sign for Gaokao changes across N under the specified uniform-tie policy. To assess this finding, compute full-grade gaps under file-order and reversed file-order tie priority and under independent extreme within-score permutations for each verifier. Report the diagnostic for every subject and budget. This is an exploratory robustness check.

### Alternative unit of work

After inspecting the AceMath replay, add a question-level sensitivity. One error-free question check returns all its answer grades. Order questions by the sum of absolute answer-mass differences. Allow changing all answer judgments within each affected question for the question-level erasure radius. The number of problems checked and the number of individual grades checked are distinct cost units.

### Reviewer-requested extension (after the original archive analysis)

Use the complete Lightman scored blob, which contains reference answer strings. Compare two operational preliminary grades to the published binary answer grades. The first uses stripped literal equality. The second additionally accepts exact equality of syntactically elementary rational numbers. Both compare strings without using the archived verdict. Preserve the original answer-level first-occurrence convention. Report the full disagreement count, the count in the reviewed set, and whether the illustrative allowance of five is valid there. The target of this check is archive fidelity.

For each original Lightman draw budget, let R be the first floor(10% of all answer units) in the original contrast order, dropping zero weights. Leave all other nonzero units unreviewed. Select a simple random sample without replacement of min(256, floor(|R|/4)) units from R, using seed 20261121+N. Use the same sample for both graders. Invert an exact hypergeometric lower tail with per-cell risk 1/120 for six simultaneous allowances. Use this allowance after subtracting observed errors. Compare two policies for the next min(128, floor(remaining/4)) reliable checks at equal cost: largest absolute coefficients, and the exact conditional minimax choice using preliminary grades. Report worst-branch width, realized endpoints and upgrade errors for both, plus a fixed-five comparison before calibration. Include unresolved decisions. No human adjudication is claimed. Summarize the full original two-tier grid with equal weight per cell and strict improvement over the better of the two single-tier baselines.

After the first calibrated replay, add a sampling comparator to test whether a cardinality allowance is costly relative to estimating the signed correction directly. Use the same R, provisional grades, S+H gold-draw budget and per-cell confidence level. Stratify by the sign of an adverse flip, allocate proportional to absolute mass, sample with replacement proportional to absolute mass, and invert binomial tails in each direction. Report the original fixed seed and 32 fixed seed offsets (0 through 31) for both approaches. Repeats describe design variability. The six-cell confidence statement applies within a seed and method.
