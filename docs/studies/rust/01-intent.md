# I. INTENT

*Framework questions: {doc}`../../framework/01-intent`*

## Why does this language exist?

### What problem was it created to solve?

Rust began as Graydon Hoare's personal project in 2006 and was sponsored by Mozilla to solve memory-safety and concurrency-safety problems in large C++ codebases (Firefox) without a garbage collector. The founding premise is that use-after-free, double-free, and data-race bugs should be rejected by the compiler rather than found in production.

### What existed before it?

Systems code was written in C/C++ with manual memory management, while safety came from garbage-collected languages (Java, C#, Go, ML-family research languages) that do not offer bare-metal control. Research languages such as Cyclone and the ML/Haskell lineage demonstrated safer designs, and Erlang demonstrated lightweight concurrency, but none was usable for writing an operating system or a browser engine.

### What was considered insufficient?

C/C++ demands vigilance that even experts fail to sustain: dangling pointers, buffer overflows, double frees, and data races are all legal programs. Garbage-collected languages buy safety with run-time pauses, memory overhead, and a run-time presence that is unacceptable for kernels, embedded targets, and FFI-heavy code. Older safe-by-design systems languages existed but were tied to runtimes or toolchains that never achieved the cross-platform package-ecosystem reach of C/C++.

### What does it prioritize?

Safety and concurrency guarantees with no garbage collector and no required run time; zero-cost abstractions, so unused features cost nothing; ahead-of-time native compilation through LLVM; and ergonomics that improve across editions (non-lexical lifetimes, edition 2018/2021/2024 refinements) without breaking existing code.

### What does it sacrifice?

Compile time and a famously steep learning curve: the borrow checker rejects designs that are perfectly valid in other languages, forcing redesign. Without a collector, cyclic graphs, self-referential structs, and heavily shared mutable object models require `Rc`/`RefCell`/`Weak`, index-based designs, or `unsafe`. Dynamic features such as reflection, `eval`, and runtime code loading simply do not exist.

```rust
// A cycle cannot be expressed with plain ownership; it needs Rc + RefCell (or indices).
use std::cell::RefCell;
use std::rc::Rc;

struct Node {
    next: Option<Rc<RefCell<Node>>>,
}
```

### Who is it designed for?

Systems programmers first — Mozilla, then embedded, OS, networking, and cloud-infrastructure teams (AWS, Cloudflare, Meta, Microsoft) — plus application programmers who want the compiler to enforce safety. Rust was adopted as a second supported language of the Linux kernel (upstreamed 2022-2024) and is used throughout Android's userspace.

### What kinds of programs does it make natural?

Operating-system components, `no_std` embedded firmware, command-line tools, network servers, WebAssembly modules, C-compatible shared libraries, and long-lived infrastructure services where invariants should be checked statically and performance should be predictable.

### What kinds of programs does it make difficult?

Highly dynamic, reflection-heavy programs; deep-inheritance or shared-mutable-graph object models; REPL-style exploratory programming (there is no first-class REPL); and scripts where start-up speed and duck typing matter more than guarantees.

### What languages or ideas influenced it?

C++ contributed RAII, move semantics, and control over memory layout; ML and Haskell contributed algebraic data types, pattern matching, type inference, and type classes (reworked into traits); Cyclone and region/lifetime research contributed lifetimes; affine type theory contributed ownership; Erlang influenced early actor-style APIs; LLVM supplies the back end.

```console
$ rustc --version
rustc 1.85.0 (4d91de4e4 2025-02-17)
$ rustc --edition 2024 hello.rs && ./hello
hello, world
```
