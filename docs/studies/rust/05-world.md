# V. WORLD

*Framework questions: {doc}`../../framework/05-world`*

## How does a program interact with the outside world?

### How does it perform I/O?

Through the `std::io` traits: `Read`/`Write` on files, sockets, and pipes; `println!`/`eprintln!` for stdout/stderr; `stdin().lock()` for input, usually wrapped in `BufReader`. `std` I/O is synchronous; asynchronous I/O comes from runtimes such as Tokio or async-std, which supply their own executors and reactors.

```rust
use std::io::Read;

fn load() -> std::io::Result<String> {
    let mut file = std::fs::File::open("Cargo.toml")?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}
```

### How does it access files?

With `std::fs` — `File`, `read_to_string`, `OpenOptions`, `copy`, `create_dir` — using `Path`/`PathBuf` for paths and `metadata`/`symlink_metadata` for inspection. Async file operations are runtime-specific (`tokio::fs`), and permissions/symlink behavior vary by platform behind the same API.

### Networks?

`std::net` offers blocking `TcpStream`, `TcpListener`, and `UdpSocket`; TLS, HTTP, and async transports are crates (`rustls`, `reqwest`, `hyper`). Nothing in the language models a protocol — networking is ordinary library code over file-descriptor-like handles.

### Processes?

`std::process::Command` spawns children with arguments, environment, and working directory, capturing stdout/stderr or piping stdin; `Child::wait`, `try_wait`, and `kill` manage lifetime. Signal handling and path lookup differ per OS, abstracted but not fully unified.

### Hardware?

Not from safe `std`: bare-metal code uses `core` under `no_std`, MMIO through `ptr::read_volatile`/`write_volatile` inside `unsafe`, vendor PAC crates generated from SVD descriptions, and `std::arch` for SIMD intrinsics. The hardware contract (addresses, orderings, side effects) is the programmer's to state.

### Time?

`std::time::Instant` for monotonic elapsed time, `SystemTime` for wall-clock time (which can jump), `Duration` for arithmetic, and `thread::sleep` for waiting. Calendars, time zones, and leap seconds belong to crates (`chrono`, `time`).

### Randomness?

Not in `std`: the ecosystem standard is the `rand` crate, backed by `getrandom` for OS entropy (`/dev/urandom`, `getrandom(2)`). Deterministic simulation requires seeding explicitly; the language has no built-in source of nondeterminism.

### Operating-system functionality?

`std::env`, `std::fs`, `std::process`, `std::os::*` platform extension traits, and `std::thread` cover the common surface; the `libc` and `windows-sys` crates expose raw syscalls and C APIs when `std` is too thin. Platform differences surface as `cfg`-gated code.

### Foreign code?

C ABI interop: declare functions in an `unsafe extern "C"` block (mandatory since edition 2024), mark structs `#[repr(C)]` for layout, and call them inside `unsafe` because the compiler cannot check foreign contracts; `bindgen`/`cbindgen` generate the declarations. Only the C ABI is stable — Rust's own ABI is explicitly unstable, so exported symbols must be C-shaped.

```rust
unsafe extern "C" {
    fn abs(input: i32) -> i32;   // from libc
}

fn main() {
    let n = unsafe { abs(-42) }; // contract (preconditions) is the caller's responsibility
    assert_eq!(n, 42);
}
```

### External resources?

Represented as RAII values whose `Drop` releases them: `File` closes, `MutexGuard` unlocks, `TcpStream` disconnects, `Child` is reaped — scope exit is the cleanup point, so early returns cannot leak. Lifetimes tie borrows to the resource, and `Arc` shares ownership of long-lived handles across threads.

## How do multiple computations coexist?

### Can computations execute simultaneously?

Yes: `std::thread::spawn` creates OS threads that run in true parallel (the closure must be `Send + 'static`), and `thread::scope` lets threads borrow stack data safely for the scope's duration. Async tasks are concurrent and parallel only if the executor uses multiple threads; processes are separate address spaces via `std::process`.

```rust
use std::thread;

let counts: Vec<usize> = thread::scope(|s| {
    let handles: Vec<_> = (0..4).map(|i| s.spawn(move || i * i)).collect();
    handles.into_iter().map(|h| h.join().unwrap()).collect()
});
assert_eq!(counts, vec![0, 1, 4, 9]);
```

### What can they share?

`Arc<T>` whenever `T: Send + Sync`, guarded state (`Mutex<T>`, `RwLock<T>`), atomics, immutable `Sync` data, and — inside `thread::scope` — plain `&mut` to the enclosing stack. A `static` can be read from any thread only if its type is `Sync`.

### How do they communicate?

Message passing with channels (`std::sync::mpsc` — multi-producer, single-consumer; `crossbeam` and Tokio for wider shapes), which moves ownership of payloads between threads; or shared memory coordinated by locks and atomics. Actor-style designs are libraries (`actix`, `ractor`) layered on channels.

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();
thread::spawn(move || tx.send(String::from("ping")).unwrap());
let msg = rx.recv().unwrap();   // ownership of the String crossed the thread boundary
assert_eq!(msg, "ping");
```

### How is shared state handled?

By wrapping it so sharing is explicit and checked: `Arc<Mutex<T>>` for the common case, `RwLock` when reads dominate, with lock scopes kept short. The type system blocks unsynchronized sharing outright: a non-`Sync` type cannot be borrowed across threads, and a non-`Send` type cannot be moved into one.

### How is synchronization handled?

`Mutex`, `RwLock`, `Condvar`, `Barrier`, `Once`, and atomics with explicit orderings — `Relaxed`, `Acquire`, `Release`, `AcqRel`, `SeqCst`. Orderings are memory-model contracts, not hints: choosing the wrong one yields defined but undesired behavior rather than a compile error.

### Can races occur?

Data races — simultaneous conflicting accesses where at least one writes, with no synchronization — are undefined behavior and unreachable from safe code. Logical races (order-dependent results, lost updates in a hand-rolled lock-free algorithm, check-then-act bugs) remain entirely possible.

### Can the language detect or prevent them?

Prevention is static: ownership plus the `Send`/`Sync` auto traits make data races a compile error, since sharing requires those bounds. Detection is dynamic: Miri reports data races on an execution it interprets, and ThreadSanitizer works on nightly (`-Zsanitizer=thread`); neither can see a logical race.

```console
error[E0277]: `Rc<Cell<i32>>` cannot be sent between threads safely
 --> main.rs:8:18
  |
8 |     require_send(x);
  |     ------------ ^ `Rc<Cell<i32>>` cannot be sent between threads safely
  |     |
  |     required by a bound introduced by this call
  |
  = help: the trait `Send` is not implemented for `Rc<Cell<i32>>`
```

### Who schedules execution?

The OS kernel for threads and processes, and the async *executor* — Tokio, async-std, smol, or a custom reactor — for tasks; `std` schedules nothing (the pre-1.0 green-thread runtime was removed). The language layer only defines how a task yields (`.await`), never when it resumes.

### How are distributed computations represented?

They are not represented natively: distribution is libraries over sockets — gRPC (`tonic`), HTTP (`reqwest`/`hyper`), serialization (`serde`) — with `Arc` and channels staying strictly process-local. There is no distributed object model, no remote reference, and no location transparency in the type system.
