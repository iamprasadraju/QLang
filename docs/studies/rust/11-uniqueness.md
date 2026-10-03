# XI. UNIQUENESS

*Framework questions: {doc}`../../framework/11-uniqueness`*

## What is fundamentally unusual about this language?

### What does this language do differently?

It treats ownership as a checked semantic layer of the language: every value has exactly one owner, borrows are validated against lifetime regions by the borrow checker, and anything that could break memory safety is confined to explicit `unsafe` - with `Send`/`Sync` derived structurally from type composition rather than declared by the programmer.

```rust
let owned = String::from("resource");
let moved = owned;              // ownership transfers; `owned` is now unusable
// println!("{owned}");          // error[E0382]: borrow of moved value
let count = moved.len();        // only the current owner may use the value
assert_eq!(count, 8);
```

### What problem does that difference solve?

It statically eliminates use-after-free, double-free, dangling pointers, and data races - the bug classes that C leaves to vigilance and that garbage-collected languages defer to run time - while keeping ahead-of-time native code with no collector and no run-time overhead.

```console
error[E0499]: cannot borrow `items` as mutable more than once at a time
 --> main.rs:4:13
  |
3 |     let a = &mut items;
  |             ---------- first mutable borrow occurs here
4 |     let b = &mut items;
  |             ^^^^^^^^^^ second mutable borrow occurs here
5 |     a.push(1);
  |     - first borrow later used here
```

### Why is the ordinary solution insufficient?

Garbage collection buys safety with pause latency, memory overhead, and a run-time presence unacceptable in kernels, embedded targets, and FFI-heavy code; manual management buys control but no safety net. Rust's claim is that a *static* discipline - affine types plus regions - can deliver both, and production adoption (Linux kernel, Android, embedded, cloud infrastructure) is the evidence.

### What does this mechanism enable?

Fearless concurrency: any `Send` value can cross threads, non-`Sync` types simply cannot be shared, so whole categories of race are compile errors; RAII extends the same discipline to files, locks, sockets, and child processes; and a signature alone tells a reader what a function may alias, move, or free.

```console
error[E0277]: `Rc<RefCell<String>>` cannot be sent between threads safely
 --> main.rs:8:18
  |
8 |     require_send(x);
  |     ------------ ^ `Rc<RefCell<String>>` cannot be sent between threads safely
  |     |
  |     required by a bound introduced by this call
  |
  = help: the trait `Send` is not implemented for `Rc<RefCell<String>>`
```

### What does it cost?

A steep learning curve - the checker rejects designs that are logically fine elsewhere - longer compile times, `Rc<RefCell<T>>` or index-based workarounds for graphs and self-reference, occasional lock-`Send` friction in async code, and an ecosystem whose async runtimes remain fragmented. The cost is paid in design iteration, not in run time.

### What concepts depend on it?

Lifetimes and outlives relations, move semantics and the moved-value error, receiver choice (`&self` versus `&mut self`), borrow-based iterators, the `Send`/`Sync` auto traits, drop checking (`dropck`), variance among references, interior mutability as the sanctioned exception to "shared means immutable," and the whole "fearless concurrency" story.

### What would be difficult without it?

Compiler-verified absence of dangling pointers and data races, confident refactoring of aliasing-heavy code, safe abstractions whose signatures alone prove their memory behavior, and any credible claim that a systems language needs neither a garbage collector nor programmer omniscience - the guarantee that makes Rust's ecosystem safe by default would not exist.
