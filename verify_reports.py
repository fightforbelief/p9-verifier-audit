"""Check provenance and cross-artifact identities without model inference."""
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean

from fetch_data import SETS


def check(name):
    d = json.loads(Path(f"reports/{name}.json").read_text(encoding="utf-8"))
    ties = json.loads(Path(f"reports/ties-{name}.json").read_text(encoding="utf-8"))
    assert ties["source"]==hashlib.sha256(Path("tie_sensitivity.py").read_bytes()).hexdigest()
    question = json.loads(Path(f"reports/question-{name}.json").read_text(encoding="utf-8"))
    assert question["source"]==hashlib.sha256(Path("question_review.py").read_bytes()).hexdigest()
    for script in ("run.py","audit.py","fetch_data.py"):
        assert d["sha256"][script]==hashlib.sha256(Path(script).read_bytes()).hexdigest(),script
    with Path(f"reports/{name}_problems.csv").open(newline="") as f:
        rows=list(csv.DictReader(f))
    for n,x in d["results"].items():
        selected=[r for r in rows if r["N"]==n]
        assert len(set(r["problem_id_hash"] for r in selected))==d["problems"]==len(selected)
        assert sum(int(r["eligible"]) for r in selected)==d["eligible"]
        a=x["answer"]
        c=x["candidate"]
        block=question["results"][n]
        assert math.isclose(a["gap"],block["gap"],abs_tol=1e-12)
        assert 0<=block["erase"]<=min(d["problems"],a["erase"])
        if block["checks"] is not None:
            assert 1<=block["checks"]<=d["problems"]
        assert sum(int(r["answer_units"]) for r in selected)==a["units"]
        assert c["units"]==d["eligible"]
        assert math.isclose(mean(float(r["candidate_gap"]) for r in selected),c["gap"],abs_tol=1e-12)
        if not x["conflicting_groups"]:
            assert math.isclose(a["gap"],c["gap"],abs_tol=1e-12)
        for unit in (a,c):
            assert math.isclose(unit["A"]-unit["B"],unit["gap"],abs_tol=1e-12)
            assert unit["policies"]["difference"]["width10"]<=unit["policies"]["pooled"]["width10"]+1e-12
            assert unit["policies"]["difference"]["width10"]<=unit["random_width10"]+1e-12
            for e,ends in unit["interval10"].items():
                assert ends[0]-1e-12<=unit["gap"]<=ends[1]+1e-12
                k=unit["policies"]["difference"]["sign"][e]
                assert (k is None)==(unit["erase"]<=int(e))
        t=ties["results"][n]
        for value in (t["forward"],t["reverse"],c["gap"]):
            assert t["min"]-1e-12<=value<=t["max"]+1e-12
        for s in x["tiers"].values():
            assert s["worst"]<=min(s["ordinary"],s["gold_only"])+1e-12
            assert s["hi"]-s["lo"]<=s["worst"]+1e-12
            assert s["lo"]-1e-12<=a["gap"]<=s["hi"]+1e-12
    return d["problems"],d["eligible"]


if __name__=="__main__":
    for name in (*SETS,"lightman"):
        print(name,*check(name))
