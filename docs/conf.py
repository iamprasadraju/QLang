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

html_context = {
    "display_github": True,
    "github_user": "iamprasadraju",
    "github_repo": "QLang",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

myst_heading_anchors = 3
suppress_warnings = ["myst.header"]
