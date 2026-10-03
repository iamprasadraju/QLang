project = "QLang"
author = "Prasad Raju G"
copyright = "2026, Prasad Raju G"
release = "0.1"

extensions = ["myst_parser"]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
root_doc = "index"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_title = "The Questions Behind Programming Languages"
html_favicon = "_static/favicon.svg"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_context = {
    "display_github": True,
    "github_user": "iamprasadraju",
    "github_repo": "QLang",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

myst_heading_anchors = 3
suppress_warnings = ["myst.header"]


def _strip_studies_from_search(app, exception):
    """Keep studies pages browsable but out of the site search index.

    Study answers repeat framework wording verbatim, so indexing them
    makes search results collide with the core framework pages.
    """
    if exception is not None or app.builder.format != "html":
        return
    import json
    import os
    import re

    path = os.path.join(app.outdir, "searchindex.js")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    m = re.match(r"Search\.setIndex\((.*)\)\s*$", raw, re.S)
    if not m:
        return
    data = json.loads(m.group(1))

    keep = [
        i
        for i, doc in enumerate(data["docnames"])
        if not doc.startswith("studies/")
    ]
    if len(keep) == len(data["docnames"]):
        return
    remap = {old: new for new, old in enumerate(keep)}

    def rl(indices):
        out = []
        for i in indices:
            if i in remap:
                out.append(remap[i])
        return out

    for key in ("docnames", "filenames", "titles"):
        data[key] = [data[key][i] for i in keep]

    for key in ("terms", "titleterms", "indexentries"):
        if key not in data:
            continue
        new = {}
        for term, idxs in data[key].items():
            if isinstance(idxs, int):
                if idxs in remap:
                    new[term] = remap[idxs]
            else:
                r = rl(idxs)
                if r:
                    new[term] = r
        data[key] = new

    if "alltitles" in data:
        new = {}
        for title, entries in data["alltitles"].items():
            r = [[remap[i], anchor] for i, anchor in entries if i in remap]
            if r:
                new[title] = r
        data["alltitles"] = new

    for key in ("objects", "objterms"):
        if key not in data or not data[key]:
            continue
        new = {}
        for name, idxs in data[key].items():
            r = rl(idxs if isinstance(idxs, list) else [idxs])
            if r:
                new[name] = r
        data[key] = new

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(
            "Search.setIndex("
            + json.dumps(data, separators=(",", ":"), ensure_ascii=False)
            + ")"
        )


def setup(app):
    app.connect("build-finished", _strip_studies_from_search)
