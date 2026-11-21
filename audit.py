"""Exact label-reveal certificates for paired best-of-N selection."""
from collections import Counter
from functools import lru_cache
from itertools import groupby
from math import comb, lcm, isfinite


@lru_cache(maxsize=32)
def rank_counts(slots, draws):
    if not 1 <= draws <= slots:
        raise ValueError("draws must be between one and the pool size")
    return [comb(slots-i-1, draws-1) for i in range(slots)]


def tie_scale(pools):
    sizes = {1}
    for rows in pools.values():
        for column in (1, 2):
            sizes.update(Counter(row[column] for row in rows).values())
    return lcm(*sizes)


def mass(scores, slots, draws, scale):
    """Integer winner mass, denominator scale * C(slots, draws). Absent slots lose."""
    if len(scores) > slots or not all(isfinite(s) for s in scores):
        raise ValueError("invalid pool")
    ranks = rank_counts(slots, draws)
    order = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)
    out = [0] * len(scores)
    start = 0
    for _, ids in groupby(order, key=scores.__getitem__):
        group = list(ids)
        size = len(group)
        if scale % size:
            raise ValueError("tie scale must be divisible by block size")
        stop = start + size
        value = sum(ranks[start:stop]) * (scale // size)
        for i in group:
            out[i] = value
        start = stop
    return out


def interval(records, reviewed, errors=0):
    """records are (mass difference, reported binary grade). First reviewed are observed."""
    if not 0 <= reviewed <= len(records) or errors < 0:
        raise ValueError("invalid audit budget")
    seen = records[:reviewed]
    known = sum(d*y for d,y in seen)
    lo = known + sum(min(0,d) for d,_ in records[reviewed:])
    hi = known + sum(max(0,d) for d,_ in records[reviewed:])
    changes = sorted(d*(1-2*y) for d,y in seen)
    return (lo + sum(min(0,v) for v in changes[:errors]),
            hi + sum(max(0,v) for v in reversed(changes[len(changes)-min(errors,len(changes)):])))


def summarize(units, denominator):
    """units in release order, (A mass, B mass, grade). Integer arithmetic through comparison."""
    a_total = sum(a*y for a,b,y in units)
    b_total = sum(b*y for a,b,y in units)
    gap = a_total - b_total
    sign = 1 if gap >= 0 else -1
    count = len(units)
    budget = count // 10
    records = [(a-b,y) for a,b,y in units]
    order = sorted(records, key=lambda row: abs(row[0]), reverse=True)
    pooled = [(a-b,y) for a,b,y in sorted(units,key=lambda row:max(row[0],row[1]),reverse=True)]
    width = sum(abs(d) for d,y in records)
    budgets = {}
    for name,ranking in [('difference',order),('pooled',pooled)]:
        low = sum(min(0,sign*d) for d,y in ranking)
        # After orienting toward the final winner, only favorable reveals raise the lower endpoint.
        adverse = []
        stops = {0:None,1:None,5:None}
        for i,(delta,y) in enumerate(ranking,1):
            d = sign * delta
            gain = d*y-min(0,d)
            if gain:
                low += gain
                if len(adverse)<5 or gain>adverse[-1]:
                    adverse = sorted([*adverse,gain],reverse=True)[:5]
            for e in stops:
                if stops[e] is None and low > sum(adverse[:e]):
                    stops[e] = i
            if all(s is not None for s in stops.values()):
                break
        budgets[name] = {"sign":stops,
                         "width10":sum(abs(d) for d,y in ranking[budget:])/denominator}
    losses = sorted((sign*d*(2*y-1) for d,y in order if sign*d*(2*y-1)>0), reverse=True)
    remaining = abs(gap)
    radius = 0
    for loss in losses:
        if remaining <= 0:
            break
        remaining -= loss
        radius += 1
    intervals = {e:[v/denominator for v in interval(order,budget,e)] for e in (0,1,5)}
    return dict(units=count, A=a_total/denominator,B=b_total/denominator,gap=gap/denominator,
                initial_width=width/denominator,random_width10=width*(count-budget)/count/denominator,
                budget10=budget,policies=budgets,interval10=intervals,erase=radius)
