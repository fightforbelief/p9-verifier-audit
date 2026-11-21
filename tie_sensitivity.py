"""Post-hoc exact sensitivity of the fully graded contrast to tie policies."""
import argparse
import hashlib
import json
from itertools import groupby
from math import comb

from audit import rank_counts
from run import OUT, SETS, load_ace, load_openai


def totals(pool, col, rank):
    order=sorted(range(len(pool)),key=lambda i:pool[i][col],reverse=True)
    start=0
    out=[0]*4
    for _,indices in groupby(order, key=lambda i:pool[i][col]):
        ids=list(indices)
        stop=start+len(ids)
        labels=[pool[i][3] for i in ids]
        correct=sum(labels)
        out[0]+=sum(rank[stop-correct:stop])
        out[1]+=sum(rank[start:start+correct])
        out[2]+=sum(rank[start+i] for i,g in enumerate(labels) if g)
        out[3]+=sum(rank[stop-i-1] for i,g in enumerate(labels) if g)
        start=stop
    return out


def sensitivity(name):
    pools,m,_=load_openai() if name=="lightman" else load_ace(name)
    reports={}
    for n in (8,32,m):
        counts=[0]*4
        ranks=rank_counts(m,n)
        for pool in pools.values():
            a=totals(pool,1,ranks)
            b=totals(pool,2,ranks)
            for j,(x,z) in enumerate(zip(a,(b[1],b[0],b[2],b[3]))):
                counts[j]+=x-z
        den=len(pools)*comb(m,n)
        reports[n]=dict(zip(("min","max","forward","reverse"),(x/den for x in counts)))
    return reports


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("datasets",nargs="+",choices=("lightman",*SETS))
    args=p.parse_args()
    for name in args.datasets:
        result=dict(dataset=name,source=hashlib.sha256(open(__file__,"rb").read()).hexdigest(),
                    results=sensitivity(name))
        (OUT/f"ties-{name}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
