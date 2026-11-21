"""Download public inputs. Set HF_ENDPOINT to a mirror if required."""
import argparse
import concurrent.futures
import hashlib
import os
from pathlib import Path
import subprocess

REVISION = "4dcc58ef82ddc5915be91f9b4f2c18c8b503a0e4"
OPENAI = "https://openaipublic.blob.core.windows.net/process-supervision/scored-test-samples.jsonl"
SETS = ("gsm8k", "math500", "minerva_math", "gaokao2023en", "olympiadbench", "college_math", "mmlu_stem")
MODELS = ("acemath_72b_rm", "acemath_7b_rm")


def ace_names(dataset, model):
    shards = range(1, 5) if model == MODELS[0] and dataset in ("college_math", "mmlu_stem") else [None]
    return [f"{dataset}{'_' + str(i) if i else ''}_{model}_s0.jsonl" for i in shards]


def fetch(pair):
    name, url = pair
    path = Path("data") / name
    if path.is_file():
        return
    tmp = path.with_suffix(".download")
    subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error", "--retry", "2",
                    "--connect-timeout", "15", "--max-time", "900", "-o", str(tmp), url], check=True)
    if name == "scored-test-samples.jsonl":
        with tmp.open("rb") as f:
            if hashlib.file_digest(f,"md5").hexdigest() != "b00756c70f195422c7855daed282205d":
                raise ValueError("OpenAI blob checksum mismatch")
    tmp.replace(path)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("source", choices=("ace", "openai", "all"), default="all", nargs="?")
    source = p.parse_args().source
    Path("data").mkdir(exist_ok=True)
    files = []
    if source in ("ace", "all"):
        endpoint = os.environ.get("HF_ENDPOINT", "https://huggingface.co").rstrip("/")
        for model in MODELS:
            base = f"{endpoint}/datasets/nvidia/AceMath-RewardBench/resolve/{REVISION}/scripts/orm_eval/{model}"
            for dataset in SETS:
                files.extend((name, base + "/" + name) for name in ace_names(dataset, model))
    if source in ("openai", "all"):
        files.append(("scored-test-samples.jsonl", OPENAI))
    with concurrent.futures.ThreadPoolExecutor(4) as executor:
        list(executor.map(fetch, files))
