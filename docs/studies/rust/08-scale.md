# VIII. SCALE

*Framework questions: {doc}`../../framework/08-scale`*

## How are programs organized and composed at scale?

### How are pieces of a program separated?

Into modules and crates: a module is a file (or `mod` block) inside a module tree, and a crate is the unit of compilation with a single root (`lib.rs` for a library, `main.rs` for a binary). A Cargo package holds one or more crates, so a codebase is split into separately compilable, separately privacy-checked units.

```rust
// src/lib.rs - crate root
pub mod config;      // src/config.rs, public API
mod internal;        // src/internal.rs, crate-private

// src/config.rs
pub struct Config {
    pub port: u16,
    secret: String,   // field-level privacy: readable only inside `config`
}
```

### How are names shared?

Through path-based `use` imports, `pub use` re-exports that curate a public surface, the automatically imported std prelude (or the `core` prelude under `no_std`), and crate names coming from `[dependencies]` addressed as `serde::Deserialize`. Since the 2018 edition, `extern crate` declarations are unnecessary except for renaming and `#[macro_use]` legacy macros.

```rust
// A facade crate re-exports one stable path over its internal modules.
mod internal {
    pub struct Config {
        pub port: u16,
    }
}

pub use internal::Config;       // users of this crate see only `facade::Config`
use std::collections::HashMap;  // private import: internal shorthand

pub fn sample() -> HashMap<&'static str, u32> {
    let mut m = HashMap::new();
    m.insert("answer", 42);
    m
}
```

### How is visibility controlled?

Default-private items plus `pub`, `pub(crate)`, `pub(super)`, `pub(in path)`, and `pub(self)`, with individual enum variants and struct fields also gated. Privacy follows the module tree - an item is visible only in its own subtree unless exported - and since there are no friends or classes, architecture must be expressed with module boundaries.

### How are dependencies represented?

As entries in `Cargo.toml` with SemVer version requirements, feature flags, optional and target-specific dependencies, plus dev-dependencies for tests and a `Cargo.lock` pinning exact versions for reproducible builds.

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["rt-multi-thread"], optional = true }

[dev-dependencies]
tempfile = "3"
```

### How are interfaces defined?

By the reachable `pub` surface: function signatures, trait definitions (behavioral contracts with default methods), public fields or accessor methods, and re-exports. rustdoc renders the interface with runnable examples, and SemVer - checked by tools such as `cargo-semver-checks` - decides what counts as a breaking change.

### How are libraries created?

With `cargo new --lib`, developed against unit tests and integration tests under `tests/`, published to crates.io with `cargo publish` (name ownership, metadata, license), and documented automatically on docs.rs. Crate types select the artifact: `rlib` (default), `cdylib`/`staticlib` (C-consumable), and `proc-macro` for compiler plugins.

### How are versions handled?

SemVer for the API, with Cargo's resolver selecting the newest compatible version (caret requirements by default), `Cargo.lock` recording exact picks, `rust-version` declaring a minimum supported compiler, and yanking removing bad releases from resolution. Language editions (2015, 2018, 2021, 2024) are per-crate and independent of the package's SemVer version.

```console
$ cargo tree -i serde
serde v1.0.210
├── api v0.2.0 (/home/u/api)
└── myapp v0.3.0 (/home/u/myapp)
```

### How does a program grow without becoming unmanageable?

By splitting into a Cargo workspace so crates enforce layering (a crate cannot reach another's private items at all), hiding internals behind `pub(crate)` and traits, using feature flags for optionality, keeping each module's `pub` surface deliberate, and relying on rustfmt, clippy, doc tests, and CI to hold the line. The compiler's privacy rules double as architectural enforcement: illegal layering does not build.
