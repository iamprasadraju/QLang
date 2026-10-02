# The Final Mental Model

*Framework questions: {doc}`../../framework/12-mental-model`*

## Answer

- **Why does it exist?** To let one program run on any machine while still
  controlling that machine's memory and instructions — UNIX rewritten without
  rewriting it per processor.
- **What can programs represent?** A flat world of typed bytes: scalars,
  aggregates, pointers, and the layouts you assemble from them — alternatives,
  absence, and invariants all exist only as conventions you maintain.
- **What does source code mean?** The behavior of an abstract machine that
  runs statements in an order the standard mostly leaves unspecified; where it
  specifies nothing, the answer is "no meaning at all", which is why the
  pitfalls are the semantics.
- **What does a name refer to?** To storage or to code, bound lexically in one
  of four separate namespaces, linkable across files but never checked at the
  moment of use — two names may designate the same bytes at any time.
- **How does computation proceed?** Eager, straight-line control flow over a
  program counter: branch, call, loop, and jump, with no laziness, no
  resumption, and no backtracking unless you code them.
- **How is behavior defined and composed?** Named bodies of statements,
  composed by calling them and by indirect calls through pointers; behavior can
  travel as a pointer but never carries its own environment with it.
- **How are abstractions formed?** By naming and hiding: a helper function, a
  private file-scope definition, an opaque handle in a header, and — for
  anything the type system cannot express — a textual rewrite before parsing.
- **What can change?** Any object some pointer can reach; `const` and
  `restrict` are promises to the compiler, not walls, and the compiler will
  punish you for breaking them rather than for forgetting them.
- **What is the lifetime of a thing?** Storage begins at block entry, at
  program start, or at allocation, and ends when the code you wrote ends it —
  no component of the language decides, tracks, or enforces any of it.
- **How does failure work?** As data: a sentinel, a status code, a thread-local
  `errno`, checked (or not) by the next line you wrote; nothing unwinds,
  nothing propagates, and nothing forces you to look.
- **How does the program interact with the world?** Through a library that is
  mostly the platform's own: streams and descriptors for the standard part,
  system headers and calling conventions for everything else, since the
  language itself defines no I/O.
- **How do multiple computations coexist?** As OS threads sharing memory, made
  correct only by mutexes and atomics you install yourself — the memory model
  is specified, the discipline is not, and a race is undefined behavior rather
  than a diagnosis.
- **What does the language know before execution?** Types, scopes, linkage, and
  constants; it can reject ill-typed or undeclared usage and fold constants,
  but it knows nothing about values, bounds, or validity.
- **What does it guarantee?** Only that a program free of undefined behavior
  behaves as written — layout, widths, sequencing, and library results — and
  that the compiler may assume you kept your side of that bargain.
- **What can programs do about programs?** Rewrite tokens before the language
  starts, select expressions by type, and run constant arithmetic; they cannot
  inspect, reflect on, or generate structured code, so generation is delegated
  to external tools that print more C.
- **How do programs scale?** By translation units joined at link time with
  headers as the only interface, held together by naming conventions, build
  tooling, and review — the language offers no module, package, or version.
- **How does source become execution?** Text is spliced and preprocessed,
  parsed and type-checked, lowered to machine code, assembled into objects,
  and merged by a linker into one flat address space where most of the
  source-level information no longer exists.
- **What style does it make natural?** Procedural, data-oriented code with
  explicit lifetimes, explicit error checks, and a single cleanup path — fast,
  readable in small doses, and increasingly expensive as the codebase grows.
- **What makes it unusual?** Its answer to every problem is to hand the
  programmer the machine instead of a service, including a pre-language text
  stage that can rewrite the program without understanding it.

## C Without Feature Lists

C is an agreement that the programmer will think like the machine the program
is about to run on. Every value has a place, every place has a duration, every
operation has a cost, and nothing in the language will tell you when you have
gotten any of that wrong. Meaning lives in a small abstract machine whose
behavior is fully defined only for programs that never make a mistake the
standard names — for everything else, silence is the specified outcome, which
is why careful C is written defensively and read suspiciously.

Work in C happens in layers, each unaware of the one below it. First text is
rewritten and stitched together by a stage that knows only characters and
tokens; then declarations and types are checked against each other; then the
result is lowered to instructions and, at the end, merged with other people's
compiled files by a linker that matches names. Abstraction therefore means
naming things well and deciding what not to show: hide the definition behind a
declaration, keep the state inside one file, pass the context explicitly
because nothing will capture it for you. State, failure, and resources are all
handled the same way — as values you check and pair by hand, with the whole
burden of correctness resting on convention, comments, and the discipline of
the person who wrote it.

The result is a language whose real subject is not computation but
commitment: you commit to a layout, a lifetime, an error protocol, an
ownership rule, and the compiler's only job is to keep you from saying
something it cannot translate. That is why C feels small and reads as
severe — it is not trying to model your problem, only to get out of the way
between your model and the hardware, and to remain portable while doing it.

## What the Map Missed

- The preprocessor does not fit "programs about programs": it runs before C
  exists, sees tokens rather than syntax, and cannot know a single type, so
  the map's reflection questions assume a view of the program that C's
  metaprogramming layer structurally cannot have. A better question would be:
  *what layer transforms the program before the language begins, and what is
  that layer forbidden to know?*
- "What is the lifetime of a thing?" presupposes that the language assigns
  responsibility for ending existence, and C declines to do so. The question
  should split in two for C: *when does storage end* (fully defined) and *who
  is expected to end it* (always the programmer) — one question, two
  unrelated answers.
- Nothing in the map asks where a name finally gets matched: common symbols,
  visibility flags, calling conventions, and archive member selection all
  decide program meaning *after* compilation, in the linker and the object
  format. For C, half of "what does a name refer to" is answered outside the
  language entirely, which the map does not have a slot for.
