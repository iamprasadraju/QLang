# X. STYLE

*Framework questions: {doc}`../../framework/10-style`*

## What style of programming does the language make natural?

### What does this language make easy?

Encoding invariants in types, refactoring with the compiler verifying every use site, systems programming with predictable performance, resource handling through RAII, safe concurrency, iterator pipelines over manual loops, and building libraries whose public/private boundary is explicit rather than conventional.

### What does it make awkward?

Reflection-heavy and dynamically typed code, self-referential or cyclic object graphs, exploratory prototyping while the design is still moving, deeply nested optional-field data (builder and serde crates exist for this), long compile times on heavily generic code, and REPL-style interaction - there is no first-class REPL.

### What does idiomatic code look like?

Small enums consumed by exhaustive `match`, `?`-based error propagation instead of nested callbacks, newtypes around primitive values, iterator adapters instead of index loops, `Arc<Mutex<T>>` only where data is genuinely shared, RAII guards for every resource, and code that is rustfmt-formatted, clippy-clean, and documented with runnable examples.

### What abstractions naturally emerge?

Newtype, builder, RAII guard, iterator adapter chains, typestate (encode the state machine in the type parameter), enum dispatch for closed sets versus trait objects for open sets, `From`/`Into` conversions, and `PhantomData` markers for parameters with no runtime representation.

```rust
struct Request<State> {
    url: String,
    marker: std::marker::PhantomData<State>,
}

struct Unsent;
struct Sent;

impl Request<Unsent> {
    fn new(url: &str) -> Self {
        Request { url: url.to_owned(), marker: std::marker::PhantomData }
    }
    fn send(self) -> Request<Sent> { Request { url: self.url, marker: std::marker::PhantomData } }
}

fn main() {
    let r = Request::new("https://example.com").send();
    // r.send();  // would not compile: Request<Sent> has no `send` method
}
```

### What patterns fight the language?

Cyclic object graphs without `Weak` or indices, inheritance hierarchies (traits plus composition instead), pervasive shared mutation, returning references into a struct's own fields (self-reference), mutable globals (`static mut` is unsafe), wide chains of `Arc<...>` passed everywhere, and holding a lock across an `.await` point (it makes the future non-`Send` and often breaks spawn).

### What way of thinking does the language encourage?

"Make invalid states unrepresentable" - design the type so the illegal configurations cannot be constructed - and, before asking who may touch data, asking who owns it. Errors are values, types are the documentation of intent, abstraction must cost nothing at run time, and threads are just ordinary consumers of `Send` types rather than a special hazard zone.
