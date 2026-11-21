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


def check_grader_reports():
    directory = Path("reports")
    replay = json.loads((directory / "grader-replay.json").read_text())
    seeds = json.loads((directory / "sampling-control.json").read_text())
    archive = json.loads((directory / "lightman.json").read_text())
    assert replay["source_sha256"] == archive["sha256"]["scored-test-samples.jsonl"]
    for report in (replay, seeds):
        for script, fingerprint in report["scripts"].items():
            assert hashlib.sha256(Path(script).read_bytes()).hexdigest() == fingerprint, script
    assert set(replay["results"]) == set(seeds["results"]) == {"8", "32", "1860"}
    for n, cell in replay["results"].items():
        entries = seeds["results"][n]
        assert len(entries) == 64
        reference = archive["results"][n]["answer"]
        assert cell["units"] == reference["units"]
        for grader, detail in cell["graders"].items():
            target = detail["target"]
            assert math.isclose(target, reference["gap"], abs_tol=1e-12)
            lo, hi = detail["fixed_five_interval"]
            assert (lo <= target <= hi) == detail["fixed_five_contains_target"]
            if detail["reviewed_disagreements"] <= 5:
                assert lo <= target <= hi
            policies = detail["policies"]
            assert policies["conditional"]["match_width"] <= policies["magnitude"]["match_width"] + 1e-12
            actual_left = detail["reviewed_disagreements"] - detail["calibration_errors"]
            if actual_left <= detail["remaining_upper"]:
                for policy in policies.values():
                    lo, hi = policy["endpoints"]
                    assert lo - 1e-12 <= target <= hi + 1e-12
                    assert hi - lo <= policy["match_width"] + 1e-12
            runs = [r for r in entries if r["grader"] == grader]
            assert sorted(r["offset"] for r in runs) == list(range(32))
            for r in runs:
                assert 0 < r["unique"] <= cell["calibration"] + cell["upgrades"]
                assert r["pps"][0] <= r["pps"][1]
                if r["offset"] == 0:
                    assert r["upgrade"] == policies["conditional"]["endpoints"]
                    assert r["magnitude"] == policies["magnitude"]["endpoints"]


if __name__=="__main__":
    for name in (*SETS,"lightman"):
        print(name,*check(name))
    check_grader_reports()
    print("Grader replay and 32-seed control verified.")
