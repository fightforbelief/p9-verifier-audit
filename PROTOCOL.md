# Finite-pool verifier replacement audit

Design recorded before computing comparison outcomes on 21 November 2026. This is a retrospective reanalysis of public graded pools. It is not an externally registered or blinded prospective experiment.

## Target

Compare process minus outcome reward in the Lightman et al. scored evaluation release and AceMath-72B-RM minus AceMath-7B-RM in all seven released subject sets. Give each problem equal weight within a set. A trial draws N slots uniformly without replacement and breaks maximum-score ties uniformly among tied candidates in the draw. For Lightman use 1,860 attempted slots per problem including discarded attempts, following the original runner. No eligible answer means zero credit. AceMath uses 64 slots. The fixed labels are the published final-answer grades.

## Endpoints and controls

At N=8, 32 and the full pool, compute the score gap, the sharp interval under arbitrary missing grades, the number of unit-cost grade reveals needed to certify the sign, and the fewest adverse grade changes needed to erase it after full review. The main audit unit is the pair of problem and exact extracted answer. Validate label consistency before pooling, including null or unavailable answer handling. Compare to treating each response as a separate unit. In case equal strings disagree in published grade, report the mismatch and present answer pooling only under an explicit reproducible resolution, with candidate-level analysis available independently.

Use absolute difference in selection mass for priority. Contrast with a symmetric pooled baseline ranking by the larger of the two selection masses, and uniform ordering (expected width). Report a 10% audit snapshot and sensitivity to one and five erroneous reviewed grades. Problem-level uncertainty for generalization, if reported, is supplementary to finite-pool certificates. A positive replacement gap or a specific level of savings is not required for reporting. Archive the input and executable hashes plus problem-level results. No fresh generation, benchmark tuning or API judgments are part of this design.
