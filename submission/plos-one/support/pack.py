"""Bundle the pinned numerical analysis with the current supporting-file guide and plot."""
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REVISION = "1845d771360fb34dfee2537d614103ea3d598bb3"


def git(*arguments):
    return subprocess.check_output(["git", "-C", str(ROOT), *arguments])


def add(archive, name, data):
    info = ZipInfo(name, date_time=(2026, 11, 21, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def main():
    tracked = git("ls-tree", "-r", "--name-only", REVISION).decode().splitlines()
    with ZipFile(HERE.parent / "S1_file.zip", "w") as archive:
        for name in tracked:
            path = Path(name)
            analysis = path.suffix == ".py" and (path.parent == Path(".") or path.parent == Path("tests"))
            report = path.parent == Path("reports") and path.suffix in {".json", ".csv"}
            if analysis or report or name in {"Run-Study.ps1", "PROTOCOL.md"}:
                add(archive, name, git("show", f"{REVISION}:{name}"))
        for name in ("README.txt", "Fig1_values.csv", "make_figure.py"):
            add(archive, name, (HERE / name).read_bytes())


if __name__ == "__main__":
    main()
