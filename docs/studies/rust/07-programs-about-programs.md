# VII. PROGRAMS ABOUT PROGRAMS

*Framework questions: {doc}`../../framework/07-programs-about-programs`*

## What can a program know or do about other programs?

### Can code inspect code?

Only syntactically, and only at compile time: `macro_rules!` matches token trees, and a procedural macro parses its token stream into an AST (typically with `syn`) where identifiers are opaque tokens - no types, no scopes, no resolution. At run time there is no reflection at all; `std::any` inspects *types*, not code.

### Can code generate code?

Yes, at compile time: `macro_rules!` expands a pattern into a token template, `#[derive]` and other procedural macros emit whole `impl` blocks, and `build.rs` scripts generate files before compilation even starts. Nothing generates machine code at run time - there is no JIT or runtime code loading.

```rust
macro_rules! as_bytes {
    ($s:expr) => {
        $s.as_bytes()   // token-level template substitution, hygienic for local names
    };
}

let text = String::from("qlang");
let bytes: &[u8] = as_bytes!(text);
```

### Can syntax be manipulated?

Inside macro invocations, arbitrarily: declarative macros rearrange token trees, and procedural macros parse with `syn`, transform the AST, and emit tokens with `quote!`. Manipulation happens before type checking, so macros cannot ask what a name resolves to - they rearrange syntax blind to its meaning.

```rust
macro_rules! swap_order {
    ($a:expr, $b:expr) => { ($b, $a) };   // rewrite the argument order before it is typed
}

let pair = swap_order!(1, 2);
assert_eq!(pair, (2, 1));   // the expansion, not the call site, decides the meaning
```

### Can programs execute during compilation?

Yes, three ways: the const evaluator runs `const fn` bodies and static initializers; procedural-macro crates and build scripts are compiled for the host and executed by the compiler itself; and `include!`/`env!`/`concat!` read compile-time state during expansion. Const evaluation is sandboxed - no I/O, no unbounded execution.

```rust
// A procedural macro: code that runs inside rustc while compiling your crate.
#[proc_macro_derive(Model)]
pub fn derive_model(input: TokenStream) -> TokenStream {
    let ast: syn::DeriveInput = syn::parse_macro_input!(input);
    let name = &ast.ident;
    quote::quote! {
        impl Model for #name {
            fn table_name() -> &'static str { stringify!(#name) }
        }
    }
    .into()
}
```

### Can programs inspect types?

Statically, through trait resolution and associated types - asking the compiler for `T::Output` is the language's real type reflection. Dynamically, `Any`/`TypeId`/`type_name` allow downcasting `dyn Any` and printing type names, but there is no field enumeration, no reflection-driven construction, and no invoking methods by name.

```rust
use std::any::{Any, TypeId};

fn kind(value: &dyn Any) -> &'static str {
    if value.is::<u32>() { "u32" }
    else if value.is::<String>() { "String" }
    else { "other" }
}

let v: Box<dyn Any> = Box::new(7u32);
assert_eq!(kind(&*v), "u32");
assert_eq!((*v).type_id(), TypeId::of::<u32>());
```

### Can the language extend itself?

Within a fixed grammar: macros define new call-shaped constructs (`vec!`, `matches!`, `sqlx::query!`, `lazy_static!`) that expand into existing ones, and attributes attach metadata that derives and lints interpret. Existing constructs cannot be redefined - how `if`, operators, and paths parse is not open for extension.

### Can the programmer introduce new syntax?

New surface phrases inside macro delimiters: `!`, `(...)`, `{...}`, or `[...]` enclose an arbitrary token tree, so DSLs (`println!`, `html!`-style markup, `query!`) are just macro arguments. New keywords, infix operators, and precedence rules are impossible - the lexer and grammar are closed, the token language inside a macro call is open.

### Can proof or metadata about programs be represented?

As attributes and documentation: `#[derive]`, `#[repr]`, `#[must_use]`, `#[cfg]`, doc comments (whose code blocks are compiled and run as doc tests), and lint attributes that make properties enforceable in CI. There are no proof terms or certified evidence in the language itself - verification lives in external tools and leaves no trace the compiler checks.
