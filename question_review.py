"""Supplementary audit when a single check adjudicates every answer to a question."""
import argparse
from collections import defaultdict
import hashlib
import json
from math import comb
from pathlib import Path
from audit import mass,tie_scale
from run import load_openai,load_ace,OUT,SETS


def summarize_blocks(blocks):
    gap=sum(v for low,high,v in blocks)
    if gap<0:
        blocks=[(-high,-low,-v) for low,high,v in blocks]
    lower=sum(low for low,high,v in blocks)
    stop=None
    for i,(low,high,v) in enumerate(sorted(blocks,key=lambda r:r[1]-r[0],reverse=True),1):
        lower+=v-low
        if lower>0:
            stop=i
            break
    remaining=abs(gap)
    radius=0
    for reduction in sorted((v-low for low,high,v in blocks),reverse=True):
        if remaining<=0:
            break
        radius+=1
        remaining-=reduction
    return stop,radius,gap


def analyze(name):
    pools,slots,_=load_openai() if name=="lightman" else load_ace(name)
    scale=tie_scale(pools)
    results={}
    for n in (8,32,slots):
        blocks=[]
        for pool in pools.values():
            a,b=[mass([r[k] for r in pool],slots,n,scale) for k in (1,2)]
            grouped=defaultdict(int)
            grade={}
            for i,(answer,_,__,y) in enumerate(pool):
                key=answer if isinstance(answer,str) and answer else ('missing',i)
                grouped[key]+=a[i]-b[i]
                grade.setdefault(key,y)
            lo=sum(min(0,w) for w in grouped.values())
            hi=sum(max(0,w) for w in grouped.values())
            observed=sum(w*grade[k] for k,w in grouped.items())
            blocks.append((lo,hi,observed))
        stop,radius,gap=summarize_blocks(blocks)
        results[n]=dict(checks=stop,erase=radius,gap=gap/(scale*comb(slots,n)*len(pools)))
    return dict(dataset=name,results=results,source=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("datasets",nargs="+",choices=("lightman",*SETS))
    for name in p.parse_args().datasets:
        (OUT/f"question-{name}.json").write_text(json.dumps(analyze(name),indent=2)+"\n")
