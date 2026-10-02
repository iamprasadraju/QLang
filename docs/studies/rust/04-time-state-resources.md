# IV. TIME, STATE, AND RESOURCES

*Framework questions: {doc}`../../framework/04-time-state-resources`*

## What can change?

### What is mutable?

Bindings declared `let mut`, places reachable through `&mut` references, and anything behind an interior-mutability wrapper (`Cell`, `RefCell`, `Mutex`, atomics). A method taking `&mut self` mutates the receiver in place; without `mut` (or interior mutability) no assignment to a place is allowed.

### What is immutable?

Everything by default: `let x = 5;` cannot be reassigned, `&T` holders cannot mutate, `const` and `static` are fixed, and an `&self` method cannot modify fields even when it holds the owner. Immutability is the baseline; mutation must be requested and then checked.

### What is state?

The values inhabiting memory as execution proceeds: locals, struct fields, heap buffers owned by `Vec`/`String`, captured closure environments, thread-locals, and globals. In Rust state is always owned by some concrete storage location — there is no ambient store or collector-managed heap separate from ownership.

### Where does state live?

Stack frames (locals and temporaries), the heap (anything behind `Box`, `Rc`, `Vec`, `String`), static storage (`static`, with `const` substituted at use sites), and thread-local storage. Layout is queryable at compile time: `std::mem::size_of::<T>()` and `align_of::<T>()` even work in `const` contexts.

### Who may change it?

The unique owner, or whoever holds the sole `&mut` borrow; shared `&T` holders may not mutate unless the type offers interior mutability. The rule is "many readers XOR one writer," and the borrow checker proves it over MIR for every program point.

```console
error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
 --> main.rs:4:5
  |
3 |     let a = &v;
  |             -- immutable borrow occurs here
4 |     v.push(1);
  |     ^^^^^^^^^ mutable borrow occurs here
5 |     println!("{a:?}");
  |               ----- immutable borrow later used here
```

### Who observes the change?

Anyone holding a valid reference after the mutation ends — the checker guarantees no observer exists during an exclusive borrow. `RefCell` moves the check to run time (a conflicting `borrow` panics), and atomics let observers see writes ordered by an explicit memory ordering.

```rust
use std::cell::RefCell;

let counter = RefCell::new(0);
*counter.borrow_mut() += 1;         // checked at run time, not compile time
assert_eq!(*counter.borrow(), 1);   // ok: previous mutable borrow ended
```

### Can change be isolated?

By ownership (a moved value is unreachable at its old home), by locks (`Mutex`, `RwLock`), by channels (`std::sync::mpsc`, `crossbeam`, Tokio mpsc) that transfer ownership instead of sharing it, and by giving each thread its own data so nothing needs synchronization. `Send` and `Sync` police what may cross a thread boundary at all.

### Can the compiler reason about change?

Yes: borrow checking (NLL) plus MIR dataflow analyses prove there is no mutation through a shared reference, no use after move, no conflicting overlapping borrow, and that each `unsafe` operation is confined to an `unsafe` context. Const evaluation additionally rejects static mutation and arithmetic overflow at compile time.

### What happens when multiple computations change the same thing?

In safe Rust this cannot be an unsynchronized data race: sharing across threads requires `Sync`, so writers serialize through a lock or coordinate through atomics. Code without synchronization does not compile; with atomics the behavior is defined but correctness depends on the ordering you chose.

```rust
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::thread;

let hits = Arc::new(AtomicU64::new(0));
let mut handles = vec![];
for _ in 0..4 {
    let hits = Arc::clone(&hits);
    handles.push(thread::spawn(move || hits.fetch_add(1, Ordering::Relaxed)));
}
for h in handles { h.join().unwrap(); }
assert_eq!(hits.load(Ordering::Relaxed), 4);
```

## What is the lifetime of a thing?

### When is something created?

A stack value when its initializer runs, a temporary when an expression evaluates it (normally destroyed at the end of the statement, extended to the block in some `let` forms), heap memory when `Box`/`Vec` allocate, `static`s at program initialization, and `const`s never — they are inlined, not created.

### Where does it live?

Inline in its owner: inside a stack frame, inside a heap allocation, or in static memory. References are pointers with no storage of their own; the "region" side of a reference exists only for checking and is erased before code generation.

### Who is responsible for it?

Exactly one owner — the variable, field, or container that holds the value. Ownership moves on assignment or pass-by-value, and the new owner inherits drop responsibility; borrows confer access, never responsibility.

### Who can access it?

The owner unconditionally, plus anyone holding a live borrow: any number of `&T`, or exactly one `&mut T`. Name-level reachability (`pub`) is a separate permission from memory-level access — an item can be visible yet never aliased, or private yet reachable inside its module.

### When does it stop existing?

When its owner's scope ends (drop glue runs `Drop::drop`, then recursively drops fields), when `mem::drop` is called explicitly, or immediately upon move (the source place becomes unusable). `mem::forget` and `ManuallyDrop` opt out; `Box::leak` deliberately never stops.

```rust
struct Lock(&'static str);

impl Drop for Lock {
    fn drop(&mut self) {
        println!("releasing {}", self.0);
    }
}

fn main() {
    let _a = Lock("mutex");
    let _b = Lock("file");
    println!("work");
}
// prints: work / releasing file / releasing mutex (reverse declaration order)
```

### Can its lifetime be extended?

By moving the value into a longer-lived owner, by returning a reference whose region is tied to an input lifetime, by temporary lifetime extension (`let s = &String::new();` keeps the temporary alive to the end of the block), or by `Box::leak` for `'static`. The checker never extends a region beyond what the referent can support.

### Can multiple things refer to it?

Many shared borrows, or one exclusive borrow; `Rc`/`Arc` turn borrows into counted *owners*, and `Weak` handles cycles without leaks. Borrow splitting at field granularity lets disjoint parts be referenced simultaneously, and raw pointers can alias freely but only inside `unsafe`.

### What happens when it becomes invalid?

In safe code it cannot be observed: use-after-move (E0382), use-after-free, and borrowing across an invalidating mutation are compile errors, and holding `&str` across a `String` reallocation is likewise rejected. If `unsafe` code defeats the checker, the behavior is undefined — Miri can flag it on an execution it analyzes.

```console
error[E0382]: borrow of moved value: `s`
 --> main.rs:4:15
  |
2 |     let s = String::from("data");
  |         - move occurs because `s` has type `String`, which does not implement the `Copy` trait
3 |     let t = s;
  |             - value moved here
4 |     println!("{s}");
  |               ^^^ value borrowed here after move
```

### Who releases its resources?

The owner, through compiler-inserted drop glue at scope exit or explicit drop, chaining into the type's `Drop` impl — RAII: `File` closes, `MutexGuard` unlocks, sockets disconnect, child processes are waited on. `Rc`/`Arc` release their inner value when the last count disappears, the global allocator frees heap memory, and no collector ever runs.

## What happens when computation does not proceed normally?

### How is absence represented?

As `Option<T>` — `None` or `Some(value)` — with no null anywhere in the language. Idiomatic APIs return it (`HashMap::get`, `Iterator::find`), and `#[must_use]` makes ignoring the result a warning.

### How does failure happen?

Recoverably, as `Result::Err(e)` returned by fallible functions; unrecoverably, as a `panic!` (from `unwrap`, `assert!`, out-of-bounds indexing, or explicit `panic!`), which unwinds or aborts according to the crate's panic strategy; catastrophically, as undefined behavior from unsound `unsafe` code.

### How does failure propagate?

With `?`, which converts the error through `From` and returns it to the caller in one expression; explicit `match` handles it manually. Panics unwind up the thread until `catch_unwind` (unwinding panics only) or the process dies; Rust has no exceptions, and unwinding across an `extern "C"` boundary is undefined behavior unless the `C-unwind` ABI is used.

```rust
use std::num::ParseIntError;

fn double(input: &str) -> Result<i32, ParseIntError> {
    let n: i32 = input.parse()?;   // error converted via From and returned
    Ok(n * 2)
}

assert_eq!(double("21"), Ok(42));
assert!(double("x").is_err());
```

### How are exceptional situations represented?

As ordinary data: an error enum implementing `Display` and `std::error::Error` (often derived with `thiserror`), or `Box<dyn Error>` for heterogeneous errors (`anyhow` in applications). Panics carry a message, a location, and a thread name — there are no catchable typed exception objects.

```console
thread 'main' panicked at src/main.rs:2:5:
called `Option::unwrap()` on a `None` value
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

### Can computation have multiple possible outcomes?

Yes, at the value level: `Result`/`Option` alternatives, exhaustive `match` over variants, and nondeterministic inputs (clock, RNG — the latter via the `rand` crate). The language itself has no nondeterminism operator and no built-in notion of probability.

### Can it backtrack?

Only by writing it: recursion that returns `Option`, explicit state stacks, or parser combinators that retry alternatives. There are no choice points and no cut; `?` aborts the current computation, it does not try a sibling alternative.

### Can failure be recovered from?

By matching the `Err` and continuing, by defaults (`unwrap_or`, `unwrap_or_else`), by catching an unwinding panic with `std::panic::catch_unwind`, and by recovering poisoned locks through `PoisonError::into_inner`. Recovery is ordinary code — nothing about failure is privileged.

### Can the programmer be forced to handle failure?

Partially: `#[must_use]` on `Result`/`Option` makes discarding them a warning (an error under `-D warnings`), and exhaustive `match` forces consideration of `None`/`Err` branches. But `unwrap()` always satisfies the compiler, converting the obligation into a run-time panic instead.
