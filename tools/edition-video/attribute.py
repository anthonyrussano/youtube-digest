#!/usr/bin/env python3
"""Write post-attribution.md from a workdir's script, handles, and (optional) report.

Runs anywhere (including the box). Does not render video.

    python3 attribute.py WORKDIR

Reads WORKDIR/script.md, optional WORKDIR/xposts.json, WORKDIR/handles.json,
and WORKDIR/report.json (for already-resolved YouTube channel metadata).
Writes WORKDIR/post-attribution.md and updates WORKDIR/report.json "unresolved"
plus WORKDIR/attribution.json.

handles.json maps a name or YouTube uploader to a confirmed X handle, and may
include "_entities": { "09": [{"entity": "Nvidia", "handle": "nvidia"}, ...] }
for companies or people who appear in a segment but are not a visual source.
Never guess handles; only put accounts you have confirmed.
"""
import importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("evbuild", os.path.join(HERE, "build.py"))
ev = importlib.util.module_from_spec(spec)
# build.py executes argparse at import if we aren't careful — it only parses in main(),
# but it also sets WD from sys.argv at the old top level. Current build.py does not.
spec.loader.exec_module(ev)

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: attribute.py WORKDIR")
    ev.WD = os.path.abspath(sys.argv[1])
    ev.C = lambda *p: os.path.join(ev.WD, *p)
    ev.report = {"sources": {}, "failures": [], "substitutions": [], "xposts": [], "unresolved": []}
    include_edition = os.environ.get("EV_INCLUDE_EDITION") in {"1", "true", "yes"}
    include_open_close = os.environ.get("EV_INCLUDE_OPEN_CLOSE") in {"1", "true", "yes"}
    edition, segs = ev.parse(ev.C("script.md"), include_edition=include_edition,
                             on_camera_open_close=include_open_close)
    ev.merge_xposts(segs, ev.C("xposts.json"))
    # If this is a full delivered video that still included open/close/edition,
    # attribute what the script lists, not the new defaults. Use --as-shot for that.
    as_shot = "--as-shot" in sys.argv or os.environ.get("EV_ATTR_AS_SHOT") in {"1", "true"}
    if as_shot:
        edition, segs = ev.parse(ev.C("script.md"), include_edition=True, on_camera_open_close=False)
        ev.merge_xposts(segs, ev.C("xposts.json"))
        for s in segs:
            s["on_camera"] = False
            s["in_video"] = True
    # Attach YouTube channel metadata from a previous report or cache if present.
    for s in segs:
        s["in_video"] = (not s["on_camera"]) if not as_shot else True
        for v in s["visuals"]:
            if v["kind"] == "yt":
                vid = ev.vid_id(v["url"])
                cache = ev.C("cache/yt", f"{vid}.channel.json")
                if os.path.exists(cache):
                    try:
                        v["_channel"] = json.load(open(cache))
                    except Exception:
                        pass
    ev.write_attribution(segs, ev.C("handles.json"))
    report_path = ev.C("report.json")
    if os.path.exists(report_path):
        try:
            existing = json.load(open(report_path))
        except Exception:
            existing = {}
        existing["unresolved"] = ev.report["unresolved"]
        # keep previously recorded xposts; add any from the sidecar
        if ev.report.get("xposts"):
            existing.setdefault("xposts", []).extend(ev.report["xposts"])
        json.dump(existing, open(report_path, "w"), indent=1)
    else:
        json.dump({"unresolved": ev.report["unresolved"], "xposts": ev.report.get("xposts", [])},
                  open(report_path, "w"), indent=1)
    print(open(ev.C("post-attribution.md")).read())
    if ev.report["unresolved"]:
        print("unresolved:", json.dumps(ev.report["unresolved"], indent=1), file=sys.stderr)

if __name__ == "__main__":
    main()
