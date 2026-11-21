"""Matched-cost design-based comparison using signed, mass-weighted grading errors."""
from bisect import bisect_right
from functools import lru_cache
import hashlib
from itertools import accumulate
import json
from math import comb
from pathlib import Path
import random

from grader_replay import source_pools, tie_scale, answer_records, cell, OUT


@lru_cache(maxsize=None)
def upper_binomial(n,k):
    """Outward-rounded Clopper-Pearson upper limit, tail risk 1/480."""
    if k==n:
        return 1.0
    grid=65536
    def lower_count(num):
        other=grid-num
        if 2*k<n:
            return sum(comb(n,j)*num**j*other**(n-j) for j in range(k+1))
        return grid**n-sum(comb(n,j)*other**j*num**(n-j) for j in range(n-k))
    lo,hi=0,grid
    while hi-lo>1:
        mid=(lo+hi)//2
        if 480*lower_count(mid)>grid**n:
            lo=mid
        else:
            hi=mid
    return hi/grid


def sampling(rows,col,count,draws,denom,rng):
    ordinary=rows[:count]
    unknown=rows[count:]
    center=sum(r[0]*r[col] for r in ordinary)
    lo=(center+sum(min(r[0],0) for r in unknown))/denom
    hi=(center+sum(max(r[0],0) for r in unknown))/denom
    sides=[[r for r in ordinary if (r[0]*(1-2*r[col])>0)==positive] for positive in (False,True)]
    sums=[sum(abs(r[0]) for r in side) for side in sides]
    n0=min(draws-int(bool(sums[1])),max(int(bool(sums[0])),round(draws*sums[0]/sum(sums))))
    cached=0
    for i,(side,total,n) in enumerate(zip(sides,sums,(n0,draws-n0))):
        if not total:
            continue
        ranks=list(accumulate(abs(r[0]) for r in side))
        ids=[bisect_right(ranks,rng.randrange(total)) for _ in range(n)]
        k=sum(side[j][col]!=side[j][1] for j in ids)
        cached+=len(set(ids))
        low=(1-upper_binomial(n,n-k))*total/denom
        high=upper_binomial(n,k)*total/denom
        if i:
            lo+=low
            hi+=high
        else:
            lo-=high
            hi-=low
    return [lo,hi],cached


def main():
    pools=source_pools()
    scale=tie_scale(pools)
    study={}
    for n in (8,32,1860):
        rows=answer_records(pools,n,scale)
        denom=scale*comb(1860,n)*len(pools)
        count=min(len(rows)//10,sum(r[0]!=0 for r in rows))
        s=min(256,count//4)
        h=min(128,(count-s)//4)
        outputs=[]
        for offset in range(32):
            seed=20261121+n+offset
            sample=set(random.Random(seed).sample(range(count),s))
            for col,grader in ((2,'literal'),(3,'rational')):
                replay=cell(rows,denom,col,count,sample,h)
                ci,unique=sampling(rows,col,count,s+h,denom,random.Random(seed))
                outputs.append(dict(offset=offset,grader=grader,pps=ci,unique=unique,
                                    upgrade=replay['policies']['conditional']['endpoints'],
                                    magnitude=replay['policies']['magnitude']['endpoints']))
        study[n]=outputs
    report=dict(results=study,scripts={name:hashlib.sha256(Path(name).read_bytes()).hexdigest()
                for name in ("sampling_control.py","grader_replay.py","adjudication.py","audit.py")})
    (OUT/'sampling-control.json').write_text(json.dumps(report,indent=2)+"\n")


if __name__=="__main__":
    main()
