# QLang

Learning a new programming language often starts with syntax: variables, functions, loops, classes, and keywords. But knowing the syntax does not necessarily mean understanding the language.

**QLang** is an attempt to solve that problem.

Instead of starting with *"What features does this language have?"*, QLang starts with *"What questions should I ask to understand this language?"*

It provides a universal set of questions for exploring how programming languages represent data, perform computation, manage state and resources, handle failure, interact with the outside world, provide guarantees, and turn source code into execution. Each language can then be investigated by answering the same questions through code, experiments, and observations.

> **A programming language is a collection of answers to problems in programming.**

QLang is about finding the questions behind those answers.

## Repository map

| Path | What it is |
|---|---|
| [`framework.md`](framework.md) | The universal map: 11 sections, 19 sub-questions, 159 checklist questions, plus the learning loop and self-correction rule. Single source of truth. |
| [`docs/`](docs/) | Sphinx site source. The framework pages include their section straight from `framework.md`; [`.readthedocs.yaml`](.readthedocs.yaml) prepares it for Read the Docs. |
| [`docs/studies/rust/`](docs/studies/rust/) | Complete study: all 159 questions answered for Rust. |
| [`docs/studies/c/`](docs/studies/c/) | Complete study: all 159 questions answered for C. |
| [`LICENSE`](LICENSE) | CC-BY-4.0. |

## Using the framework

1. Pick a language you think you know.
2. Open a framework section and take one question.
3. Run the learning loop: **ask → understand → find the language's answer → build a small experiment → break it → observe → explain → identify tradeoffs → connect to other questions.**
4. Record the answers in your own study directory, in the framework's structure.
5. When the language does something the map cannot explain, do not force it into an existing category — ask *"What question did we fail to ask?"* and improve the map.

Two worked studies exist as proof of concept: [Rust](docs/studies/rust/index.md) and [C](docs/studies/c/index.md). Read them alongside the framework sections they mirror.

## Building the documentation site

```sh
python3 -m venv .venv
.venv/bin/pip install -r docs/requirements.txt
.venv/bin/sphinx-build -W docs docs/_build
# open docs/_build/index.html
```

`-W` treats warnings as errors; the build is expected to be warning-free. `.readthedocs.yaml` applies the same `-W` strictness once the project is imported into Read the Docs.

## Contributing

### A new language study

1. Create `docs/studies/<lang>/` with an `index.md` (intro + toctree) and one file per framework section, `01-intent.md` … `12-mental-model.md`, mirroring `docs/studies/rust/`.
2. Answer **every** question from the corresponding `framework.md` section, in order, with the question text verbatim as an `###` heading.
3. Prefer evidence: real compiler output, small runnable snippets, observed experiments.
4. Register the study in the toctree in `docs/studies/index.md`, then build with `-W` and fix every warning.
5. Open a pull request.

### Improving the framework

Edits to `framework.md` are welcome when they make a question more universal (see the seven criteria at the top of the file and the self-correction rule at the bottom). Keep the section structure intact — the docs site and both studies split on the exact `##` headings. If you change a heading, update the `{include}` markers in `docs/framework/*.md` to match.

## License

[CC-BY-4.0](LICENSE) — reuse and adapt with attribution.
