"""Reproduce an archive or its individual subject sets from the project root."""
import argparse
from collections import defaultdict
import csv
import gzip
import hashlib
import json
import platform
from math import comb
from pathlib import Path
import sys

from audit import mass, summarize, tie_scale, tier_design
from fetch_data import SETS, MODELS, ace_names

DATA = Path("data")
OUT = Path("reports")
SIZES = dict(zip(SETS, (1319,500,272,385,675,2818,3018)))


def load_ace(dataset):
    models = []
    files = []
    for model in MODELS:
        problems = {}
        for name in ace_names(dataset, model):
            path = DATA / name
            files.append(path)
            with path.open(encoding="utf-8") as f:
                for line in f:
                    row = json.loads(line)
                    key = row['idx']
                    if key in problems:
                        raise ValueError(f"duplicate {key} in {name}")
                    problems[key] = row
        models.append(problems)
    a,b = models
    if a.keys()!=b.keys() or len(a)!=SIZES[dataset]:
        raise ValueError(f"problem mismatch in {dataset}: {len(a)}, {len(b)}")
    pools = {}
    for key in sorted(a):
        x,y = a[key],b[key]
        if x['pred']!=y['pred'] or x['score']!=y['score'] or len(x['pred'])!=64:
            raise ValueError(f"unaligned candidates in {dataset}/{key}")
        pools[key] = list(zip(x['pred'],x['rm_score'],y['rm_score'],x['score'],strict=True))
    return pools,64,files


def load_openai():
    path = DATA / "scored-test-samples.jsonl"
    compact = DATA / "lightman-fields.jsonl.gz"
    if not path.is_file() and compact.is_file():
        manifest = compact.with_suffix(".json")
        meta = json.loads(manifest.read_text(encoding="utf-8"))
        if meta["raw_md5"] != "b00756c70f195422c7855daed282205d":
            raise ValueError("unexpected original source")
        content = hashlib.sha256()
        pools = defaultdict(list)
        with gzip.open(compact,"rb") as f:
            for line in f:
                content.update(line)
                problem,answer,a,b,y = json.loads(line)
                rows = pools[problem]
                if answer is not None:
                    rows.append((answer,a,b,y))
        if content.hexdigest()!=meta["content_sha256"] or len(pools)!=500:
            raise ValueError("incomplete transport projection")
        return pools,1860,[compact,manifest]
    with path.open('rb') as f:
        if hashlib.file_digest(f,'md5').hexdigest() != "b00756c70f195422c7855daed282205d":
            raise ValueError("OpenAI source mismatch")
    pools = defaultdict(list)
    with path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            key = r['problem']
            rows = pools[key]
            answer = r.get('answer',r.get('given_answer'))
            if answer is not None:
                rows.append((answer,r['prm_score'],r['orm_score'],r['is_correct']))
    if len(pools)!=500:
        raise ValueError("wrong Lightman problem count")
    return pools,1860,[path]


def study(dataset):
    pools,slots,inputs = load_openai() if dataset=="lightman" else load_ace(dataset)
    scale = tie_scale(pools)
    results = {}
    problem_rows = []
    for draws in (8,32,slots):
        denom = comb(slots,draws)*scale
        full = denom*len(pools)
        answers,candidates = [],[]
        conflicts = conflict_mass = ambiguous_rows = 0
        for key,pool in pools.items():
            a = mass([r[1] for r in pool],slots,draws,scale)
            b = mass([r[2] for r in pool],slots,draws,scale)
            grouped = {}
            delta = 0
            for i,(answer,_,__,y) in enumerate(pool):
                if type(y) is not bool:
                    raise ValueError(f"non-boolean grade {type(y)}")
                candidates.append((a[i],b[i],y))
                delta += (a[i]-b[i])*y
                group_key = answer if isinstance(answer,str) and answer else ('missing',i)
                cell = grouped.setdefault(group_key,[0,0,y,False,0])
                cell[0] += a[i]
                cell[1] += b[i]
                cell[3] |= cell[2]!=y
                cell[4] += 1
            for x,z,y,mixed,size in grouped.values():
                answers.append((x,z,y))
                if mixed:
                    conflicts += 1
                    conflict_mass += abs(x-z)
                    ambiguous_rows += size
            problem = hashlib.sha256(str(key).encode()).hexdigest()[:20]
            problem_rows.append((problem,draws,len(pool),len(grouped),delta/denom))
        results[draws] = dict(answer=summarize(answers,full),candidate=summarize(candidates,full),
                              conflicting_groups=conflicts,affected_rows=ambiguous_rows,
                              conflict_width=conflict_mass/full)
        tiers={}
        for percent in (1,10):
            effort=len(answers)*percent//100
            for cost in (2,5):
                res=tier_design([(a-b,y) for a,b,y in answers],effort,cost,5)
                tiers[f"{percent}pct_cost{cost}"]={k:(v if k in ("gold","regular") else v/full) for k,v in res.items()}
        results[draws]["tiers"]=tiers
    with (OUT/f"{dataset}_problems.csv").open("w",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("problem_id_hash","N","eligible","answer_units","candidate_gap"))
        writer.writerows(problem_rows)
    source = {}
    for path in [*inputs,Path("run.py"),Path("audit.py"),Path("fetch_data.py")]:
        with path.open("rb") as f:
            source[path.name]=hashlib.file_digest(f,"sha256").hexdigest()
    report = dict(dataset=dataset,problems=len(pools),slots=slots,eligible=sum(map(len,pools.values())),
                  environment=[platform.platform(),sys.version],sha256=source,results=results)
    (OUT/f"{dataset}.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(dataset,len(pools),"complete",flush=True)


if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument("datasets",nargs="*",default=["lightman",*SETS])
    args=p.parse_args()
    OUT.mkdir(exist_ok=True)
    for name in args.datasets:
        if name not in ("lightman",*SETS):
            p.error("unknown dataset")
        study(name)
