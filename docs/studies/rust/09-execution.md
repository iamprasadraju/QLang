# IX. EXECUTION

*Framework questions: {doc}`../../framework/09-execution`*

## How does source become execution?

### How is source parsed?

rustc lexes the input into tokens and parses with a recursive-descent parser into an AST, capturing macro invocations as raw token trees that are expanded (and re-parsed) around the surrounding items. Parsing is edition-aware — for example, `gen` is a reserved keyword in edition 2024 but an identifier in earlier editions.

### How is meaning checked?

After macro expansion: name resolution over the module and macro namespaces, lowering to HIR, type checking with trait selection (in-memory inference variables and obligation solving), lowering to MIR, then borrow checking (NLL), exhaustiveness checking, const evaluation, and lint passes — all before any machine code is emitted.

### What is elaborated?

Desugaring into a smaller core: `for` becomes `loop` over an `IntoIterator`, `?` becomes a `match` on the `Try` trait, `async fn` becomes an anonymous state-machine type polled by an executor, closures become capture structs implementing `Fn`/`FnMut`/`FnOnce`, method calls become autoref/autoderef adjustments, `impl Trait` becomes an opaque type, and trait objects become a fat pointer to data plus vtable.

```rust
let collection = vec![10, 20, 30];

// What you write:
for x in &collection { println!("{x}"); }

// What it elaborates toward (conceptually):
let mut it = IntoIterator::into_iter(&collection);
while let Some(x) = it.next() { println!("{x}"); }
```

### What is inferred?

Local types by unification, closure parameter and return types, method and receiver resolution, trait selection, the concrete type behind each `impl Trait`, lifetime regions (elision plus NLL inference), and literal types with their defaults (`i32`, `f64`). Anything that could be ambiguous across crates may require an annotation in a public signature.

### What code is generated?

Monomorphized MIR is lowered to LLVM IR, optimized, and emitted as native object files, then linked into an executable or static library (std is statically linked by default; LTO is optional). There is no bytecode and no virtual machine — the intermediate stages are exposed only as compiler output flags.

```console
$ rustc --edition 2024 --emit=mir,llvm-ir,asm hello.rs
$ ls
hello.ll  hello.mir  hello.rs  hello.s
```

### What is evaluated at compile time?

`const` and `static` initializers, `const fn` bodies inside const contexts, array lengths and const-generic arguments, explicit enum discriminants, and macro-expanded constant expressions — all executed by rustc's const interpreter (the same engine Miri uses), which forbids I/O, unbounded loops, and mutation of statics. The result is baked into the binary; nothing re-runs at startup.

```rust
const TABLE: [u64; 4] = {
    let mut t = [0u64; 4];   // allowed in const: bounded loop, no I/O
    let mut i = 0;
    while i < 4 { t[i] = (i as u64) * (i as u64); i += 1; }
    t
};

static PAGE: usize = 4096 * 4;   // computed by the compiler, stored in the binary

fn main() {
    assert_eq!(TABLE[3], 9);
    assert_eq!(PAGE, 16384);
}
```

Violations are compile errors, not run-time surprises:

```console
error[E0080]: evaluation of constant value failed
 --> main.rs:1:18
  |
1 | const BAD: u32 = 7 / 0;
  |                  ^^^^^ attempt to divide `7_u32` by zero
```

### What gets erased?

Lifetimes and regions — they exist only for checking and are gone before code generation — plus zero-sized types and `PhantomData` (no storage is emitted), generic parameters (replaced per instantiation by monomorphization rather than shared), `const` items (inlined at use), and debug information unless `-g` is passed. Trait objects erase the concrete type but keep a vtable pointer.

```rust
use std::marker::PhantomData;
use std::mem::size_of;

struct Tagged<T>(u64, PhantomData<T>);   // phantom parameter, no runtime footprint

assert_eq!(size_of::<PhantomData<String>>(), 0);
assert_eq!(size_of::<Tagged<u8>>(), 8);  // only the u64 field occupies space
assert_eq!(size_of::<&str>(), 16);       // fat pointer: data + length on 64-bit
```
