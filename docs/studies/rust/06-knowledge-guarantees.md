# VI. KNOWLEDGE AND GUARANTEES

*Framework questions: {doc}`../../framework/06-knowledge-guarantees`*

## What does the language know before the program runs?

### What can be determined statically?

Types of every expression, ownership and borrow validity with their lifetime regions, trait resolution, pattern exhaustiveness, mutability permissions, `Send`/`Sync` eligibility, const-evaluated values (array lengths, `const fn` results), macro expansion success, and hundreds of lint-level facts (unreachable code, unused variables).

### What must wait until runtime?

Actual data values, which implementation a `dyn Trait` object dispatches to, whether a `RefCell` borrow conflicts, lock acquisition, panics from `unwrap` or out-of-bounds indexing, I/O outcomes, and thread/task interleavings. Out-of-memory aborts the process rather than returning an error.

### What can the compiler infer?

Local variable types by unification, closure signatures, method resolution (autoref/autoderef), the hidden type behind `impl Trait`, lifetime regions via elision plus NLL, and integer literal types (defaulting to `i32`). Public signatures sometimes need annotations to keep inference unambiguous across crates, not for correctness.

### What can it reject?

Type mismatches, missing trait impls, use-after-move and borrow conflicts, non-exhaustive matches, private-item access, outlives violations, non-constant values in const contexts, unsafe operations outside `unsafe`, and invalid `#[repr]` combinations - all before code generation.

```console
error[E0004]: non-exhaustive patterns: `None` not covered
 --> main.rs:3:11
  |
3 |     match x { Some(v) => { let _ = v; } }
  |           ^ pattern `None` not covered
  |
note: `Option<i32>` defined here
 --> /rustc/4d91de4e48198da2e33413efdcd9cd2cc0c46688/library/core/src/option.rs:572:1
 ::: /rustc/4d91de4e48198da2e33413efdcd9cd2cc0c46688/library/core/src/option.rs:576:5
  |
  = note: not covered
  = note: the matched value is of type `Option<i32>`
```

### What relationships can be expressed in the type system?

Trait bounds and supertraits, outlives relations (`'a: 'b`), associated-type equalities (`T: Iterator<Item = u8>`), const-generic equalities (`[T; N]`), and auto-trait membership (`Send`, `Sync`, `Unpin`, `RefUnwindSafe`). Variance among lifetimes and types is implicit and computed rather than written.

### Can types depend on values?

Yes, within const generics: array lengths `[T; N]`, structs parameterized by integers, `bool`s, and `char`s (`Flag<true>`), with generic const expressions on a best-effort stable subset. Types indexed by arbitrary runtime values, computed tuple sizes, or proofs do not exist - there are no full dependent types.

```rust
struct Buffer<const N: usize> {
    data: [u8; N],
}

fn checksum(buf: &Buffer<32>) -> u8 {
    buf.data.iter().fold(0u8, |a, b| a.wrapping_add(*b))
}
```

### Can the language express invariants?

By construction and encapsulation: newtypes with private fields (`Meters(f64)`), std's `NonZeroU32`, typestate (a checker function is the only way to obtain `Token<Valid>`), and `PhantomData` for phantom parameters. There is no `requires`/`ensures` syntax - an invariant is a property the code maintains, not a formula the compiler checks.

### Can programs be partially evaluated?

Effectively yes: monomorphization specializes generic code per instantiation, `const fn` runs in the compile-time interpreter, const generics substitute values into types, and `#[inline]` steers downstream optimization. There is no general staging system (no user-controlled multi-phase evaluation).

### Can properties be proved?

Not by the language: the compiler's proofs are limited to its built-in safety properties. External tools cover the rest - Kani (model checking), Prusti/Creusot/Verus (program verification), Miri (undefined behavior on a given execution) - and none of them is part of `rustc`.

## What does the language guarantee?

### What errors are prevented?

In safe code: use-after-free, double free, dangling and null references, data races, and mutation through shared references; at the type level, mismatched types and non-exhaustive matches; plus ignored `#[must_use]` results (as a warning). Out-of-bounds indexing is checked at run time (panic), not prevented.

### What errors are detected?

Every statically checkable failure, as a compile error: type and trait mismatches, borrow and move violations, unreachable or overlapping patterns, privacy violations, invalid lifetimes, and const-eval failures such as overflow inside `const`.

```console
$ cargo build
   Compiling guarantees v0.1.0 (/home/u/guarantees)
error[E0597]: `s` does not live long enough
 --> src/main.rs:7:13
  |
6 |         let s = give();
  |             - binding `s` declared here
7 |         r = &s;
  |             ^^ borrowed value does not live long enough
8 |     }
  |     - `s` dropped here while still borrowed
9 |     println!("{r}");
  |               --- borrow later used here

For more information about this error, try `rustc --explain E0597`.
error: could not compile `guarantees` (bin "guarantees") due to 1 previous error
```

### What remains the programmer's responsibility?

Logic correctness, absence of panics (`unwrap`, division, indexing), deadlock freedom, logical race freedom, integer overflow in release builds (overflow checks are off by default there), and the soundness of every `unsafe` block, `unsafe fn`, and manual `Send`/`Sync` impl.

### What properties can be guaranteed?

Memory safety and data-race freedom for safe code, no null dereferences, deterministic destruction (fields in declaration order, locals in reverse declaration order), exactly-once drop unless `mem::forget` intervenes, stable layout for `#[repr(C)]` and `#[repr(transparent)]`, and C-compatible FFI layout. `repr(Rust)` layout is explicitly *not* guaranteed.

### What properties can only be tested?

Performance, absence of deadlocks, business-logic correctness, liveness under concurrency, and the general soundness of `unsafe` code - Miri and sanitizers find bugs only on the paths they exercise. Completeness of error handling is also a testing/review concern, not a compiler one.

### What can the compiler prove?

That well-typed safe programs cannot exhibit undefined behavior (assuming a sound standard library and sound dependencies), that matches are exhaustive, that every borrow stays inside its region, that unsafe operations sit in unsafe contexts, and that const-evaluated code obeys const rules. It proves nothing about functional correctness.

### What programs are impossible to express safely?

Self-referential structs, intrusive or cyclic graphs with live back-pointers, aliasing-plus-mutation structures, and arbitrary pointer arithmetic. Each requires `unsafe`, `Rc`/`RefCell`/`Weak`, index-based designs, or an arena - the design must change before the code compiles.

### Where can the guarantees be bypassed?

Inside `unsafe` blocks, `unsafe fn` bodies, and `unsafe impl`s; through raw pointers, FFI calls, `static mut`, `mem::transmute`, `MaybeUninit`, and `ManuallyDrop`; and - rarely but real - through unsound bugs in dependencies or the standard library. `unsafe` disables some *checks*, not the type system: you owe the compiler the documented contract.

```rust
use std::mem::MaybeUninit;

let mut cell = MaybeUninit::<i32>::uninit();
let raw = cell.as_mut_ptr();     // a raw pointer may point at uninit memory
unsafe {
    // `ptr::read`'s contract demands initialized memory; violating it is UB,
    // and the compiler lets this through only because of `unsafe`.
    let _ = std::ptr::read(raw);
}
```

Miri catches the above on an execution it interprets:

```console
$ cargo +nightly miri run
error: Undefined Behavior: reading memory at alloc206[0x0..0x4], but memory is uninitialized at [0x0..0x4], and this operation requires initialized memory
 --> src/main.rs:9:17
  |
9 |         let _ = std::ptr::read(raw);
  |                 ^^^^^^^^^^^^^^^^^^^ Undefined Behavior occurred here
  |
  = help: this indicates a bug in the program: it performed an invalid operation, and caused Undefined Behavior
  = help: see https://doc.rust-lang.org/nightly/reference/behavior-considered-undefined.html for further information
```
