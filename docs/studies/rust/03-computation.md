# III. COMPUTATION

*Framework questions: {doc}`../../framework/03-computation`*

## How does computation proceed?

### What causes computation to happen?

Running an executable enters `fn main`, and from there every function call, operator, and macro-expanded primitive eagerly evaluates its operands under call-by-value. Additional roots of computation are spawned threads, async tasks polled by an executor, and destructors firing as values leave scope.

### What determines the next step?

Ordinary control flow: sequencing, `if`/`else`, exhaustive `match`, loops, calls, and `return`. After compilation this is visible as the control-flow graph of MIR (and then LLVM IR); at run time the OS schedules threads and an async executor schedules tasks.

### In what order are things evaluated?

A specified left-to-right order: call arguments, operands, tuple/struct/array elements, and the `match` scrutinee are evaluated in written order. Temporaries created in an expression live until the end of the enclosing statement (with temporary lifetime extension in `let` initializers).

```rust
fn side(i: i32) -> i32 { println!("eval {i}"); i }

fn main() {
    let pair = (side(1), side(2));   // prints 1 then 2: written order is guaranteed
}
```

### Can evaluation be delayed?

Yes, in several independent ways: `&&` and `||` short-circuit, closures defer their body until called, iterator adapters are pull-based and lazy, `LazyLock`/`OnceLock` defer work until first access, and futures do nothing until polled.

```rust
let big = (0..1_000_000).map(|x| x * 2).filter(|x| x % 3 == 0); // nothing runs yet
let first = big.take(3).collect::<Vec<_>>();                     // only enough work for 3 results
```

### Can evaluation branch?

`if`/`else`, exhaustive `match` (optionally with guards), `if let`/`while let`, and the `?` operator, which branches to an early `return`. All of them are expressions, so a branch produces a value as well as choosing a path.

### Can evaluation backtrack?

Not natively: there are no choice points, no cut operator, and no resumable failure. Backtracking search must be written by hand as recursion returning `Option`/`Result`, or delegated to crates (parser combinators such as `nom`/`winnow` retry alternatives explicitly).

### Can computation be recursive?

Directly and mutually, at run time and in limited `const fn` contexts; recursive data types require indirection (`Box`, `Rc`) because a type cannot contain itself inline. Tail-call optimization is not guaranteed, so deep recursion overflows the stack and the run time panics rather than looping.

```console
$ ./deep_recursion
thread 'main' has overflowed its stack
fatal runtime error: stack overflow
```

### Can computation be suspended and resumed?

With `async`/`await`: the compiler converts the function body into a state machine (an anonymous future) that an executor polls to completion; `std` contains no executor, so Tokio, async-std, or smol supply one. OS threads are preempted by the kernel, and language-level generators/coroutines (`gen` blocks) are still unstable.

### Is computation driven by control flow, rewriting, reduction, search, data dependencies, or something else?

Control flow over eager evaluation, with two overlays: lazy pull-based dataflow (iterators, `Future`s) where the consumer drives the producer, and external scheduling by executors for async tasks. There is no term rewriting, unification-driven search, or dataflow graph scheduler inside the language.

## How is behavior defined and composed?

### How do I define reusable behavior?

With `fn` items, methods in `impl` blocks, trait methods that define behavior shared across types, closures for inline behavior, and `macro_rules!` when the repetition is syntactic rather than typed.

### What is a function?

A named item with typed parameters and a return type, callable directly, through a monomorphized generic instantiation, through a function pointer `fn(T) -> U`, or through a trait object. Function items are zero-sized types that coerce to `fn` pointers; `extern "C"` selects the C ABI (the only stable one) for FFI.

### Is behavior a value?

Yes: a function item coerces to a `fn` pointer, a closure is a value of a unique per-definition type, and `Box<dyn Fn()>` boxes behavior as ordinary data. Capture-free closures are zero-sized; closures with captures are sized structs holding the captured places.

### Can behavior be passed around?

As a generic parameter (`f: impl Fn(&str) -> bool`, or `F: FnOnce()` with a `where` clause), as a `fn` pointer when uniformity matters, or as `dyn Fn`. Higher-ranked requirements use `for<'a> Fn(&'a str)`, which the compiler checks against any lifetime.

### Can behavior be returned?

Yes: `impl Iterator<Item = u8>` returns an opaque concrete type, `Box<dyn Error>` returns a boxed trait object, and `fn` pointers can be returned when callers must share one representation. Returning a capturing closure needs `impl Fn` or boxing, since every closure expression has a distinct type.

### Can behavior capture context?

Closures capture enclosing names automatically - per variable and (since edition 2021) per place element - by `&`, `&mut`, or move, inferred from how the body uses them; `move` forces by-value capture, which is what `'static` thread spawns require.

```rust
let threshold = 3;
let above = move |xs: &[i32]| xs.iter().filter(|&&x| x > threshold).count();
// `threshold` is owned by the closure, so it can outlive this scope (e.g. sent to a thread)
```

### How is behavior combined with other behavior?

By chaining rather than nesting: iterator adapters (`map`/`filter`/`flat_map`), `Option`/`Result` combinators (`and_then`, `map_err`), trait composition through supertraits and stacked bounds, and `.await` chains in async code. True function composition must be written by hand or taken from a crate.

```rust
let evens_squared_sum: i32 = (1..=10)
    .filter(|x| x % 2 == 0)
    .map(|x| x * x)
    .sum();
```

### What are the basic units of composition?

Functions and closures (behavior), traits plus impls (interfaces), generics with bounds (parameterized composition), modules (namespace composition), iterator adapters (dataflow composition), and macros (syntactic composition). The newtype pattern is the usual way to compose an existing type with a fresh interface.

## How are abstractions formed?

### How do I avoid repeating an idea?

Move the idea into a generic function or struct (type repetition), a trait (behavioral repetition), a `macro_rules!` or procedural macro (syntactic repetition), or a const generic (value repetition). Two similar lines stay duplicated; repetition that encodes an idea gets abstracted.

### How can an idea be generalized?

By stating a trait bound - `fn largest<T: Ord>(xs: &[T]) -> &T` - refined with `where` clauses, associated types for fixed relationships (`Iterator::Item`), supertraits for refinement, and blanket impls such as `impl<T: Display> ToString for T` for derived coverage.

```rust
fn max_all<T: Ord>(xs: &[T]) -> Option<&T> {
    xs.iter().max()
}

println!("{:?}", max_all(&[3, 1, 4, 1, 5]));  // works for any Ord, monomorphized per type
```

### What can be parameterized?

Types, lifetimes, const values (primitive integers, `bool`, `char`, and array lengths - the stable const-generic subset), associated types chosen by each impl, and opaque `impl Trait` parameters. Types indexed by arbitrary computed values or proofs (full dependent types) are out of scope.

```rust
struct Grid<const ROWS: usize, const COLS: usize> {
    cells: [[f64; COLS]; ROWS],
}

let g: Grid<2, 3> = Grid { cells: [[0.0; 3]; 2] };
```

### What can be hidden?

Private fields and items (the default visibility is module-private), `pub(crate)`/`pub(super)` restricted exposure, the concrete type behind an `impl Trait` return, macro internals via hygiene, and whole extension points through sealed traits (a private supertrait blocks external impls).

### What can be exposed?

Anything reachable: `pub` items, public fields or their accessors, trait implementations, `pub use` re-exports that curate a public surface, and individually `pub` enum variants or struct fields. Visibility is hierarchical - `pub(in path)` narrows it, and an item can never be more visible than its parent module.

### What can depend on another abstraction?

Trait bounds including associated-type bounds (`T: Iterator<Item: Clone>`), supertraits, explicit outlives relations (`'a: 'b`), const parameters depending on generic parameters (`[T; N]`), and `where` clauses that bundle several such dependencies. Every dependency is checked statically at monomorphization.

### How can abstractions be composed?

By implementing a local trait for a foreign type (governed by orphan rules: the trait or the type must be local), stacking bounds (`T: Clone + Default + Send`), intersecting trait objects (`dyn Error + Send + Sync + 'static`), and wrapping types in newtypes that delegate to the inner value.

### At what level can abstraction happen?

At five levels: values (closures), types (generics, traits, const generics), modules (visibility and re-exports), syntax (macros), and evaluation (`const fn`). All are resolved during compilation and monomorphized away, so abstraction costs nothing at run time.
