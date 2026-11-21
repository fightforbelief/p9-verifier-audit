"""Replay actual provisional graders, calibrated allowances and matched-cost upgrades."""
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from math import comb
from pathlib import Path
import random
import re
import sys

from adjudication import error_upper, upgrade
from audit import interval, mass, tie_scale
from run import DATA, OUT

SOURCE = "46a01478dceefe8194304f9e2db92fedefab8c8cc47033a9d7e059f3b18c5f82"


def rational(s):
    if len(s)>128:
        return None
    frac = re.fullmatch(r"([+-]?)\\(?:d?frac|tfrac)\{(-?\d+)\}\{(-?\d+)\}",s)
    if frac:
        sign,num,den = frac.groups()
        return (-1 if sign=="-" else 1)*Fraction(int(num),int(den)) if int(den) else None
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:/\d+)?",s):
        try:
            return Fraction(s)
        except (ValueError,ZeroDivisionError):
            return None
    return None


def grades(answer, reference):
    a, b = answer.strip(), reference.strip()
    literal = bool(a and a==b)
    x = rational(a)
    return literal, literal or (x is not None and x==rational(b))


def source_pools():
    path = DATA / "scored-test-samples.jsonl"
    digest=hashlib.sha256()
    pools=defaultdict(list)
    with path.open("rb") as f:
        for line in f:
            digest.update(line)
            r=json.loads(line)
            rows=pools[r["problem"]]
            answer=r.get("answer",r.get("given_answer"))
            if answer is not None:
                reference=r["ground_truth_answer"]
                if not isinstance(answer,str) or not isinstance(reference,str):
                    raise ValueError("expected answer and reference strings")
                rows.append((answer,r["prm_score"],r["orm_score"],r["is_correct"],reference))
    if digest.hexdigest()!=SOURCE or len(pools)!=500:
        raise ValueError("archive mismatch")
    return pools


def answer_records(pools,n,scale):
    rows=[]
    for pool in pools.values():
        a,b=[mass([r[c] for r in pool],1860,n,scale) for c in (1,2)]
        cells={}
        for i,(answer,_,__,y,ref) in enumerate(pool):
            key=answer if answer else ('missing',i)
            if key not in cells:
                cells[key]=[0,y,*grades(answer,ref)]
            cells[key][0]+=a[i]-b[i]
        rows.extend(cells.values())
    return sorted(rows,key=lambda r:abs(r[0]),reverse=True)


def bounds(records,e,unknown,known,denom):
    lo,hi=interval(records,len(records),e)
    return [(lo+unknown[0]+known)/denom,(hi+unknown[1]+known)/denom]


def cell(rows,denom,column,r_count,sample,checks):
    reviewed=rows[:r_count]
    outside=rows[r_count:]
    unknown=(sum(min(r[0],0) for r in outside),sum(max(r[0],0) for r in outside))
    p=[(r[0],r[column]) for r in reviewed]
    observed=bounds(p,5,unknown,0,denom)
    sample_errors=sum(reviewed[i][column]!=reviewed[i][1] for i in sample)
    remaining=[r for i,r in enumerate(reviewed) if i not in sample]
    known=sum(reviewed[i][0]*reviewed[i][1] for i in sample)
    upper=error_upper(r_count,len(sample),sample_errors,120)-sample_errors
    provisional=[(r[0],r[column]) for r in remaining]
    baseline=list(range(checks))  # remaining rows preserve decreasing |d|
    chosen=upgrade(provisional,checks,upper)
    plans={}
    for name,ids in (("magnitude",baseline),("conditional",chosen)):
        picked=set(ids)
        rest=[t for i,t in enumerate(provisional) if i not in picked]
        matches=known+sum(remaining[i][0]*remaining[i][column] for i in picked)
        worst=bounds(rest,upper,unknown,matches,denom)
        found=sum(remaining[i][column]!=remaining[i][1] for i in picked)
        resolved=known+sum(remaining[i][0]*remaining[i][1] for i in picked)
        realized=bounds(rest,upper-found,unknown,resolved,denom) if found<=upper else None
        plans[name]=dict(disagreements=found,match_width=worst[1]-worst[0],endpoints=realized)
    truth=sum(r[0]*r[1] for r in rows)/denom
    return dict(total_disagreements=sum(r[column]!=r[1] for r in rows),reviewed_disagreements=sum(r[column]!=r[1] for r in reviewed),
                fixed_five_interval=observed,fixed_five_contains_target=observed[0]<=truth<=observed[1],
                target=truth,calibration_errors=sample_errors,remaining_upper=upper,
                before_upgrades=bounds(provisional,upper,unknown,known,denom),policies=plans)


def main():
    pools=source_pools()
    scale=tie_scale(pools)
    results={}
    for n in (8,32,1860):
        rows=answer_records(pools,n,scale)
        r_count=min(len(rows)//10,sum(r[0]!=0 for r in rows))
        s=min(256,r_count//4)
        h=min(128,(r_count-s)//4)
        sample=set(random.Random(20261121+n).sample(range(r_count),s))
        denom=scale*comb(1860,n)*len(pools)
        results[n]=dict(units=len(rows),ordinary=r_count,calibration=s,upgrades=h,
                        graders={name:cell(rows,denom,col,r_count,sample,h) for col,name in
                                 ((2,"literal"),(3,"rational"))})
    report=dict(source_sha256=SOURCE,python=sys.version,results=results,
                scripts={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
                         for p in ("grader_replay.py","adjudication.py","audit.py")})
    (OUT/"grader-replay.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
