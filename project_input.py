"""Transport only used fields from a checksum-verified public archive."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ORIGINAL_MD5 = "b00756c70f195422c7855daed282205d"
FIELDS = ("problem","answer","prm_score","orm_score","is_correct")


def project(source, destination):
    raw_md5 = hashlib.md5()
    raw_sha = hashlib.sha256()
    compact_sha = hashlib.sha256()
    tmp = destination.with_suffix(".partial")
    with source.open("rb") as inp, gzip.open(tmp,"wb",compresslevel=4) as out:
        for raw in inp:
            raw_md5.update(raw)
            raw_sha.update(raw)
            row = json.loads(raw)
            row["answer"] = row.get("answer",row.get("given_answer"))
            payload=(json.dumps([row[k] for k in FIELDS],ensure_ascii=False,separators=(",",":"))+"\n").encode()
            out.write(payload)
            compact_sha.update(payload)
    if raw_md5.hexdigest()!=ORIGINAL_MD5:
        raise ValueError("publisher content MD5 mismatch")
    tmp.replace(destination)
    manifest=dict(raw_md5=raw_md5.hexdigest(),raw_sha256=raw_sha.hexdigest(),
                  content_sha256=compact_sha.hexdigest(),fields=FIELDS)
    destination.with_suffix(".json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    p.add_argument("destination",type=Path)
    args=p.parse_args()
    project(args.source,args.destination)
