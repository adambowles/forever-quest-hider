"""Create the installable ZIP; TOC is the only version source."""
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "ForeverQuestHider"

def version():
    value = re.search(r"^## Version: (.+)$", (ADDON / "ForeverQuestHider.toc").read_text(), re.M).group(1)
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value):
        raise ValueError("TOC version must be stable SemVer")
    return value

def package(tag=None):
    current = version()
    if tag is not None and tag != "v" + current:
        raise ValueError(f"Tag {tag!r} does not match v{current}")
    target = ROOT / "dist" / f"ForeverQuestHider-{current}-Forever.zip"
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in ("ForeverQuestHider.toc", "Core.lua"):
            archive.write(ADDON / name, "ForeverQuestHider/" + name)
        for name in ("LICENSE", "README.md"):
            archive.write(ROOT / name, "ForeverQuestHider/" + name)
    return target

if __name__ == "__main__":
    print(package(sys.argv[1] if len(sys.argv) > 1 else None))
