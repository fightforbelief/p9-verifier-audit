"""Plan answer reviews and certify a partial transcript on unlabeled paired score pools."""
import argparse
from collections import defaultdict
from fractions import Fraction
import json
from math import comb
from pathlib import Path

from audit import mass, interval, tie_scale, tier_design


def coefficients(problems, slots, draws):
    if not problems:
        raise ValueError("empty benchmark")
    pools = {}
    for p in problems:
        q = p["problem"]
        if q in pools or not isinstance(q,str):
            raise ValueError("each problem needs a unique string ID")
        rows = [(c["unit"],c["a"],c["b"]) for c in p["candidates"]]
        if any(not isinstance(u,str) or not u for u,_,__ in rows):
            raise ValueError("each eligible candidate needs a nonempty review-unit key")
        pools[q] = rows
    scale = tie_scale(pools)
    weights = defaultdict(int)
    for q,rows in pools.items():
        a,b = [mass([r[j] for r in rows],slots,draws,scale) for j in (1,2)]
        for (unit,_,__),x,z in zip(rows,a,b):
            weights[q,unit] += x-z
    return weights, len(pools)*scale*comb(slots,draws)


def evaluate(weights,denom,reviews,errors):
    gold = 0
    ordinary = []
    seen = set()
    for r in reviews:
        key = r["problem"],r["unit"]
        if key not in weights or key in seen or type(r["grade"]) is not bool:
            raise ValueError("unknown, duplicate or nonbinary judgment")
        seen.add(key)
        if r["tier"]=="gold":
            gold += weights[key]*r["grade"]
        elif r["tier"]=="ordinary":
            ordinary.append((weights[key],r["grade"]))
        else:
            raise ValueError("tier must be gold or ordinary")
    rest = [(d,False) for key,d in weights.items() if key not in seen]
    lo,hi = interval(ordinary+rest,len(ordinary),errors)
    lo,hi = Fraction(lo+gold,denom),Fraction(hi+gold,denom)
    return dict(exact=[str(lo),str(hi)],gap_interval=[float(lo),float(hi)],
                decision="A" if lo>0 else "B" if hi<0 else "unresolved")


def plan(weights,budget,cost,errors):
    ranked = sorted(weights,key=lambda k:abs(weights[k]),reverse=True)
    res=tier_design([(weights[k],False) for k in ranked],budget,cost,errors)
    return [dict(problem=q,unit=u,tier="gold" if i<res["gold"] else "ordinary",grade=None)
            for i,(q,u) in enumerate(ranked[:res["gold"]+res["regular"]])]


def read_rows(path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("pool",type=Path)
    p.add_argument("--slots",type=int,required=True)
    p.add_argument("--draws",type=int,required=True)
    p.add_argument("--errors",type=int,default=0)
    action=p.add_mutually_exclusive_group(required=True)
    action.add_argument("--budget",type=int)
    action.add_argument("--reviews",type=Path)
    p.add_argument("--gold-cost",type=int,default=5)
    args=p.parse_args()
    w,den=coefficients(read_rows(args.pool),args.slots,args.draws)
    if args.reviews is None:
        for row in plan(w,args.budget,args.gold_cost,args.errors):
            print(json.dumps(row,ensure_ascii=True))
    else:
        print(json.dumps(evaluate(w,den,read_rows(args.reviews),args.errors),indent=2))
