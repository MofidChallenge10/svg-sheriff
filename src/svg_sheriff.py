"""Static SVG accessibility and security auditor."""
from __future__ import annotations
import argparse, json, re, sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse

@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str
    element: str = "svg"

ANIM_TAGS={"animate","animateMotion","animateTransform","set"}
ACTIVE_TAGS={"script","foreignObject"}
URL_ATTRS={"href","{http://www.w3.org/1999/xlink}href"}

def local_name(tag: str) -> str:
    return tag.rsplit("}",1)[-1]

def audit_svg(source: str) -> list[Finding]:
    findings=[]
    try: root=ET.fromstring(source)
    except ET.ParseError as exc: return [Finding("SVG001","error",f"Invalid XML: {exc}")]
    if local_name(root.tag)!="svg": return [Finding("SVG002","error","Root element must be <svg>.")]
    title=any(local_name(e.tag)=="title" and (e.text or "").strip() for e in root.iter())
    labelled=any(k in root.attrib for k in ("aria-label","aria-labelledby"))
    if not title and not labelled: findings.append(Finding("A11Y001","warning","Add a non-empty <title> or accessible name."))
    if "viewBox" not in root.attrib: findings.append(Finding("SVG003","warning","Missing viewBox can make responsive scaling unreliable."))
    for element in root.iter():
        tag=local_name(element.tag)
        if tag in ACTIVE_TAGS: findings.append(Finding("SEC001","error",f"Active content <{tag}> is not permitted.",tag))
        if tag in ANIM_TAGS: findings.append(Finding("MOTION001","warning",f"Animation <{tag}> needs reduced-motion review and a static alternative.",tag))
        for attr,value in element.attrib.items():
            name=local_name(attr).lower()
            if name.startswith("on"): findings.append(Finding("SEC002","error",f"Event handler attribute '{attr}' is unsafe.",tag))
            if attr in URL_ATTRS:
                scheme=urlparse(value.strip()).scheme.lower()
                if scheme not in ("","http","https"): findings.append(Finding("SEC003","error",f"Disallowed URL scheme '{scheme}'.",tag))
            if name=="style" and re.search(r"@import|url\(\s*['\"]?(?:https?:)?//",value,re.I):
                findings.append(Finding("SEC004","warning","External resource reference found.",tag))
    return findings

def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser(description="Audit SVG accessibility, motion and unsafe constructs.")
    p.add_argument("files",nargs="+"); p.add_argument("--format",choices=("text","json"),default="text")
    p.add_argument("--strict",action="store_true",help="Fail on warnings as well as errors")
    args=p.parse_args(argv); results={}; failed=False
    for filename in args.files:
        path=Path(filename)
        try: findings=audit_svg(path.read_text(encoding="utf-8"))
        except OSError as exc: findings=[Finding("IO001","error",str(exc))]
        results[str(path)]=[asdict(f) for f in findings]
        failed |= any(f.severity=="error" or (args.strict and f.severity=="warning") for f in findings)
    if args.format=="json": print(json.dumps(results,indent=2,ensure_ascii=False))
    else:
        for filename,items in results.items():
            print(f"\\n{filename}")
            if not items: print("  ✓ No findings")
            for f in items: print(f"  {f['severity'].upper():7} {f['rule']} [{f['element']}] {f['message']}")
    return 1 if failed else 0

if __name__=="__main__": sys.exit(main())
