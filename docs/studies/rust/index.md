# Rust

Rust is a statically typed systems language, originally developed at Mozilla
Research (first stable release in 2015), that provides memory safety and
thread safety *without* a garbage collector. Its core mechanism is
ownership: every value has exactly one owner, borrows are checked at compile
time against lifetimes, and unsafe code is quarantined behind an explicit
`unsafe` block. It compiles ahead of time through LLVM to native code.

How to read this study: every page mirrors a section of the
{doc}`framework <../../framework/index>`. Each question from the universal
map appears under its original heading, followed by Rust's answer. Code
snippets are meant to be run and broken - that is the learning loop.

```{toctree}
:maxdepth: 1

01-intent
02-meaning
03-computation
04-time-state-resources
05-world
06-knowledge-guarantees
07-programs-about-programs
08-scale
09-execution
10-style
11-uniqueness
12-mental-model
```
