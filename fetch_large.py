"""Resume the Lightman archive using checked 4 MiB ranges, then verify publisher MD5."""
import argparse
import concurrent.futures
import hashlib
from pathlib import Path
import shutil
import subprocess

from fetch_data import OPENAI

SIZE=2159374091
STEP=4*1024**2
MD5="b00756c70f195422c7855daed282205d"


def fetch(workers,proxy):
    root=Path("data")
    chunks=root/"lightman-chunks"
    chunks.mkdir(parents=True,exist_ok=True)
    final=root/"scored-test-samples.jsonl"
    if final.exists():
        with final.open("rb") as f:
            if hashlib.file_digest(f,"md5").hexdigest()!=MD5:
                raise ValueError("existing source digest mismatch")
        return

    def chunk(start):
        end=min(start+STEP,SIZE)-1
        dest=chunks/str(start)
        if dest.is_file() and dest.stat().st_size==end-start+1:
            return dest
        tmp=dest.with_suffix(".partial")
        cmd=["curl","--fail","--silent","--show-error","--location","--connect-timeout","8","--max-time","45"]
        if proxy:
            cmd.extend(("--proxy",proxy))
        for _ in range(8):
            res=subprocess.run([*cmd,"--range",f"{start}-{end}",OPENAI+f"?offset={start}",
                                "--output",str(tmp),"--write-out","%{http_code}"],capture_output=True)
            if res.returncode==0 and res.stdout==b"206" and tmp.stat().st_size==end-start+1:
                tmp.replace(dest)
                return dest
        raise OSError(f"range {start}-{end} unavailable")

    with concurrent.futures.ThreadPoolExecutor(workers) as ex:
        paths=list(ex.map(chunk,range(0,SIZE,STEP)))
    tmp=final.with_suffix(".assembled")
    with tmp.open("wb") as out:
        for path in paths:
            with path.open("rb") as f:
                shutil.copyfileobj(f,out)
    with tmp.open("rb") as f:
        if hashlib.file_digest(f,"md5").hexdigest()!=MD5:
            raise ValueError("assembled source digest mismatch")
    tmp.replace(final)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workers",type=int,default=8)
    p.add_argument("--proxy")
    args=p.parse_args()
    fetch(args.workers,args.proxy)
