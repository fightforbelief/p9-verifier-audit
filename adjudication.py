"""Gold adjudication after observing provisional binary grades."""
from itertools import accumulate
from math import comb


def upgrade(records, checks, errors):
    """Return indices attaining minimum worst remaining width conditional on the transcript.

    records contain (signed coefficient, ordinary grade). Every mismatch discovered by
    an upgrade consumes one of the allowed errors in the original ordinary transcript.
    """
    if not 0 <= checks <= len(records) or errors < 0:
        raise ValueError("invalid adjudication budget")
    sides = [[], []]
    for i, (weight, grade) in enumerate(records):
        # The sign of the change if this ordinary grade is wrong.
        sides[int(weight * (1 - 2 * grade) > 0)].append(i)
    for side in sides:
        side.sort(key=lambda i: abs(records[i][0]), reverse=True)
    prefix = [[0, *accumulate(abs(records[i][0]) for i in side)] for side in sides]

    def tail(side, used):
        sums = prefix[side]
        return sums[min(len(sums) - 1, used + errors)] - sums[used]

    options = range(max(0, checks - len(sides[1])), min(checks, len(sides[0])) + 1)
    count = min(options, key=lambda k: tail(0, k) + tail(1, checks-k))
    return sides[0][:count] + sides[1][:checks-count]


def error_upper(population, sample, mismatches, risk_denominator):
    """Upper bound on total errors by inversion at risk 1/risk_denominator."""
    if not 0 <= mismatches <= sample <= population or risk_denominator <= 1:
        raise ValueError("invalid calibration sample or risk")
    ways = comb(population, sample)
    low, high = mismatches, population - sample + mismatches
    while low < high:
        total = (low+high+1)//2
        lower_tail = sum(comb(total, j) * comb(population-total, sample-j)
                         for j in range(max(0, sample-population+total), mismatches+1))
        if lower_tail*risk_denominator > ways:
            low = total
        else:
            high = total-1
    return low
