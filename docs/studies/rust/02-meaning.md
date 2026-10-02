# II. MEANING

*Framework questions: {doc}`../../framework/02-meaning`*

## What can a program represent?

### What kinds of things can programs represent?

Scalars (12 sized integer types, `f32`/`f64`, `bool`, `char`), compound values (structs, tuples, fixed arrays `[T; N]`, slices `&[T]`, `String`/`&str`), algebraic data types built from enums, references and raw pointers, function pointers and closures, and trait objects (`dyn Trait`). Everything inhabits a statically known type; there is no untyped "any value" (`dyn Any` is the closest, and it still carries a `TypeId`).

### What are the fundamental values?

Primitive scalars: `i8`…`i128`/`isize`, `u8`…`u128`/`usize`, `f32`, `f64`, `bool`, `char` (a four-byte Unicode scalar value, not a byte), and `()` (the unit value). References (`&T`, `&mut T`) and raw pointers (`*const T`, `*mut T`) are also primitive; `usize` is pointer-sized and used wherever sizes or indices must match the machine.

### How are values combined?

Product types (structs, tuples, arrays) combine components, sum types (enums) combine alternatives, and generics parameterize either. There is no implicit numeric widening, no truthiness, and no null coalescing: combining different numeric types requires an explicit `as` cast or a `From`/`Into` conversion.

### How are new kinds of values created?

By declaring nominal `struct` and `enum` types and attaching behavior with `impl` blocks; `type` only aliases an existing type. New behavior for existing types comes from trait implementations, so there are no classes, no structural record types, and no inheritance-based type creation.

```rust
struct Point { x: f64, y: f64 }                 // product type
enum Shape { Circle(f64), Rect(f64, f64) }       // sum type, variants carry data

impl Shape {
    fn area(&self) -> f64 {
        match self {
            Shape::Circle(r) => std::f64::consts::PI * r * r,
            Shape::Rect(w, h) => w * h,
        }
    }
}
```

### Can values represent alternatives?

Yes: enums carry data per variant, and `match` destructures them exhaustively (the compiler rejects uncovered cases). Behavioral alternatives come from trait objects at run time or from enum dispatch when the set of alternatives is closed and known statically.

```rust
enum Shape { Circle(f64), Rect(f64, f64) }   // the type defined above

fn describe(s: &Shape) -> &'static str {
    match s {
        Shape::Circle(_) => "round",
        Shape::Rect(w, h) if w == h => "square",
        Shape::Rect(_, _) => "rectangular",
    }
}
```

### Can they represent absence?

As `Option<T>`, which is either `None` or `Some(value)`; the language has no null. `Option` is marked `#[must_use]`, so discarding one is a warning, and the `?` operator threads absence through call chains without nested `if let`.

### Can they represent relationships?

Borrowed relationships are references with explicit or inferred lifetimes, and shared graphs are `Rc`/`Arc` counts with `Weak` for back-edges. Directly self-referential structs are not expressible in safe Rust; the standard designs are split indices, arenas, or helper crates such as `self_cell`.

### What can the language express as data?

Anything that inhabits a type: deeply nested structs and enums, raw byte strings (`&[u8]`), Unicode text, and statically initializable data in `const`/`static`, with shapes parameterized by const generics. Arbitrary-precision numbers, open row types, and value-indexed dependent pairs need crates (`num-bigint`) or type-level encoding tricks.

### What cannot be expressed naturally?

Types created at run time, structural/row polymorphism, inheritance hierarchies, null, and truly self-referential values. "Object with optional fields" becomes an enum or a builder crate, and type-level computation stops at const generics — there are no types indexed by arbitrary computed values.

## What does source code mean?

### What constructs does the language recognize?

Items (`fn`, `struct`, `enum`, `trait`, `impl`, `mod`, `use`, `const`, `static`, `type`), statements (`let`, expression statements, nested items), expressions (blocks included — a block is an expression), attributes `#[...]`, and macro invocations. Because macros are part of the grammar, the compiler accepts a token stream at invocation sites before deciding what it means.

### How is syntax mapped to meaning?

rustc lexes and parses into an AST, expands macros, lowers to HIR (desugared, fully resolved), type-checks with trait solving, lowers to MIR for borrow checking and optimization, monomorphizes, and emits LLVM IR. The Rust Reference specifies the semantics, and it explicitly marks unspecified areas such as `repr(Rust)` memory layout.

### What is the semantic model?

An eager, call-by-value operational semantics over typed expressions, constrained by an affine ownership system with regions (lifetimes). It is neither denotational nor proof-carrying: meaning is what evaluation does, while type and borrow checking are static preconditions for running.

### What does an expression mean?

An expression evaluates, in a specified order, to a value of exactly one type (or to `!`, the never type) and may perform side effects. The value of a block is its trailing expression; a trailing `;` instead yields `()`.

```rust
let sum = {
    let a = 2;
    let b = 3;
    a + b          // trailing expression: block's value is 5
};
let nothing = { sum; };   // `;` discards 5; block's value is ()
```

### What is a statement?

`let` bindings, expression statements terminated by `;`, and item declarations inside blocks. Statements produce no value of their own, which is why `let x = if c { 1 } else { 2 };` works but `let x = if c { 1 } else { 2 };` written as two statements would require the `if` to be balanced as an expression.

### What does a declaration mean?

It introduces a name into a scope: items are order-independent inside a module (so functions may be mutually recursive without forward declarations), `let` bindings enter at their statement and are dropped at scope end, and `const` items are substituted at use sites while `static` items exist once for the whole program.

### What does a program mean?

A crate: for an executable, the meaning is `fn main` running to completion — plus any threads and async tasks it spawns — on a target platform; for a library, the meaning is the observable behavior of its public items. Statics initialize before `main`, and destructors run as owned values die, so meaning includes initialization and teardown, not just `main`'s body.

### Is meaning defined by evaluation, transformation, proof, relation, effects, or something else?

Primarily operational evaluation (eager, with specified left-to-right order), layered with mandatory compile-time transformation (macro expansion, desugaring, monomorphization, const evaluation). Safety is a checked typing/borrow judgment rather than a program-supplied proof, and effects are unrestricted — the type system records only incidental consequences such as `io::Result`.

## What does a name refer to?

### What can be named?

Values (`let` bindings, `const`, `static`), items (functions, types, traits, modules, crates), struct fields, generic parameters, labels (`'outer:`), lifetimes (`'a`), and macros. A path such as `crate::net::Server` names an item through the module tree, while a variable name denotes a *place* — a location in memory — not just a value.

### What does a name denote?

A binding to a place with a type and, for references, a lifetime region: `x` denotes where the value lives, and the type says what may be done there. This is why assignment is possible only for `mut` places and why borrowing a name borrows the place, not a copy of the value.

### How are bindings created?

By `let` (optionally `let mut`), function and closure parameters, patterns in `match`, `if let`, `while let`, and `for` loops, plus `const`/`static` declarations. The pattern forms `ref` and `ref mut` bind by borrow instead of by move/copy.

```rust
let name = String::from("ada");   // owned binding
let n = 42;                       // Copy binding
let r = &name;                    // borrowed binding (place -> &String)
let ref alias = name;             // `ref` binds by borrow, not move
```

### Where is a name visible?

From its declaration to the end of its enclosing block, with inner `let`s shadowing outer ones; items are visible throughout their enclosing module and cross module boundaries only through `pub` and `use`. Macro-defined names follow textual scope until exported with `#[macro_use]` or a path-based `use`.

### How are names resolved?

Innermost scope first, through separate namespaces (types, values, macros, lifetimes), then outward through the module tree, then the prelude, then the extern prelude (dependency crate names). A name that exists in two namespaces can legitimately mean two different things.

### Can two names refer to the same thing?

Yes: `use` creates aliases, `let b = a;` copies (for `Copy` types) or moves the same value, and `&x`/`&y` can alias one place. The borrow checker permits any number of shared aliases but only one exclusive alias, and never an exclusive one alongside any other live reference.

### Can names be rebound?

Shadowing is legal: a second `let x` introduces a new binding that hides the old one, which remains alive (and drops at scope end) but unreachable; `let mut x` reassigns the same binding in place. `const` and `static` names are never rebound.

### Can names be captured?

Closures capture enclosing names automatically — per variable, by shared reference, mutable reference, or move, inferred from use — and `move` forces by-value capture (required for `'static` thread spawns). Since edition 2021, capture is per place element, so a closure may capture only `self.field` rather than all of `self`.

```rust
let limit = 10;
let items = vec![1, 2, 3];

let by_ref = || items.iter().filter(|&&x| x < limit).sum::<i32>(); // borrows items and limit
let force_move = move || (items, limit);   // both moved into the closure
```

### What happens when scopes overlap?

Non-lexical lifetimes compute each borrow's region as exactly the program points where it can still be used; an overlapping exclusive borrow ends the other's region, while disjoint field borrows coexist. NLL is what lets `let r = &mut v;` borrow only `v.first` while `v.second` stays usable, and lets borrows end before the closing brace.

```rust
let mut v = (vec![1], vec![2]);
let a = &mut v.0;
a.push(3);                 // borrow of v.0 ends after its last use
let b = &mut v.1;          // legal: disjoint place, earlier region ended
println!("{a:?} {b:?}");
```

### Are there multiple namespaces?

Four: the type namespace, the value namespace, the macro namespace, and the lifetime/label namespace. A struct name occupies both the type and value namespaces (its constructor), while `use std::vec;` (module) and `vec![]` (macro) coexist because they live in different namespaces.
