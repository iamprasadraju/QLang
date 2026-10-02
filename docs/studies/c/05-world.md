# V. WORLD

*Framework questions: {doc}`../../framework/05-world`*

## How does a program interact with the outside world?

### How does it perform I/O?

Through the standard library's `FILE` streams (`printf`, `scanf`,
`fgetc`, `fwrite`) and, outside ISO C, through the platform's byte-level
descriptors (POSIX `read`/`write`, Windows `_read`). The language itself has
no I/O operators — everything beyond the abstract machine is library
behavior, specified by the library clause or by the platform.

### How does it access files?

`fopen`/`freopen`/`tmpfile` produce a `FILE *`, then `fread`/`fwrite`/
`fseek`/`ftell` move bytes through it; wide-character variants handle text
encodings, and `"b"` mode matters on platforms that translate newlines.
Large-file offsets, locking, and permissions come from POSIX, not from ISO C.

```c
#include <stdio.h>
#include <errno.h>
#include <string.h>
FILE *f = fopen("data.txt", "r");
if (!f) {
    fprintf(stderr, "open failed: %s\n", strerror(errno));  /* failure is data */
    return -1;
}
```

### Networks?

Not provided by ISO C at all: sockets come from the platform
(`sys/socket.h` on POSIX, `winsock2.h` on Windows) or from a library such as
libcurl. C has no URL or stream-of-network type; a networking program is
always platform code plus hand-written protocols.

### Processes?

Also outside the standard: POSIX `fork`, `execve`, `waitpid`, `popen`, or
Windows `CreateProcess`. The only ISO C process primitive is `system()`, whose
behavior and quoting rules are implementation-defined.

```c
#include <unistd.h>
#include <sys/wait.h>
pid_t pid = fork();
if (pid == 0) _exit(0);                  /* child */
else if (pid > 0) waitpid(pid, NULL, 0); /* parent */
```

### Hardware?

Through raw pointers to memory-mapped I/O registers declared `volatile`,
through compiler intrinsics, and through inline assembly in the compiler's own
dialect (`__asm__ volatile` on GCC/Clang, `__asm` on MSVC) — all
non-standard. Exact-width types and `struct` layout make device registers
representable.

```c
#include <stdint.h>
volatile uint32_t *const STATUS = (volatile uint32_t *)0x40021000;
while (*STATUS & 0x01u) { /* the compiler must re-read: volatile access */ }
__asm__ volatile ("dmb sy" ::: "memory");   /* GCC/Clang barrier, not ISO C */
```

### Time?

`time`, `clock`, `difftime`, and C11's `timespec_get`; `clock()` measures CPU
time, not wall time. Monotonic high-resolution clocks, timers, and deadlines
are platform APIs (`clock_gettime(CLOCK_MONOTONIC)`, `QueryPerformanceCounter`).

### Randomness?

`rand()`/`srand()` — deterministic, often a weak PRNG, and explicitly not for
security — plus Annex K's `rand_s` where the implementation provides it.
Serious randomness requires the OS (`/dev/urandom`, `getrandom`,
`BCryptGenRandom`) or a hardware intrinsic such as `_rdrand64_step`.

### Operating-system functionality?

Through the platform C library, which is effectively the real standard library
on any hosted system: POSIX defines the interfaces most C programs actually
use for processes, sockets, threads, and file systems, while ISO C covers only
the portable core (stdio, string, math, stdlib, time, locale, threads).

### Foreign code?

C *is* the foreign interface: other languages expose C calling conventions,
and any C library is directly callable from C. Within a program, `dlopen`/
`dlsym` (POSIX) or `LoadLibrary`/`GetProcAddress` (Windows) resolve symbols at
run time; there is no sandbox — loaded code executes with full privilege.

### External resources?

Represented as raw handles: `FILE *`, file descriptors, `malloc`ed buffers,
mutexes, sockets — each with an open/close pair and no automatic cleanup.
`atexit` handlers and signal handlers are the only ISO hooks that run at
shutdown.

## How do multiple computations coexist?

### Can computations execute simultaneously?

Yes, but only through the platform: OS processes, or threads created by C11's
`thrd_create`, POSIX `pthread_create`, or Win32 `CreateThread`. C11 defines
the memory model those threads run under, but the language has no task,
future, or async construct of its own.

```console
$ clang -std=c11 -Wall thrd.c -o thrd
thrd.c:1:10: fatal error: 'threads.h' file not found
    1 | #include <threads.h>
      |          ^~~~~~~~~~~
1 error generated.
```

That is real toolchain evidence of the gap: even the standard's own thread
header is missing on this system (macOS ships no `threads.h`), so portable C
code reaches for pthreads, and Windows code for Win32.

### What can they share?

Any memory reachable by both: globals, heap objects, mmap'ed regions,
hardware registers, and `_Atomic` objects. `_Thread_local` is the only storage
the language keeps private to one thread.

### How do they communicate?

By shared memory plus synchronization, or by leaving the language entirely:
pipes, sockets, and message queues between processes. Inside one process,
condition variables (`cnd_t`, `pthread_cond_t`) and atomics carry the
"messages".

### How is shared state handled?

By manual discipline: protect every shared non-atomic object with a mutex, or
make it `_Atomic`. The only edges the memory model orders are those created
by atomics, mutexes, thread creation, and thread join — everything else is a
race.

### How is synchronization handled?

`mtx_t` mutexes (plain, recursive, timed), `cnd_t` condition variables,
`once_flag`/`call_once`, spin locks built on `atomic_flag`, and platform
primitives such as futexes and SRW locks. The standard has no reader-writer
lock, no barrier, and no lock-free queue — those are libraries you write.

### Can races occur?

Always, unless you build the synchronization yourself: two unsynchronized
writes, or a write racing a read, silently lose or reorder updates. The
hardware memory model (TSO on x86, much weaker on ARM) is what lets a race
survive on one machine and corrupt data on the next.

### Can the language detect or prevent them?

No. C11 makes a data race undefined behavior but says nothing to the compiler
about diagnosing it, so no warning and no runtime check appears by default —
the standard's answer to a race is "the program has no defined behavior".
Tooling, not the language, catches it:

```console
$ clang -fsanitize=thread -O1 race.c -o race_tsan -lpthread && ./race_tsan
==================
WARNING: ThreadSanitizer: data race (pid=12304)
  Write of size 4 at 0x000104604000 by main thread:
    #0 main <null> (race_tsan:arm64+0x100000698)

  Previous write of size 4 at 0x000104604000 by thread T1:
    #0 work <null> (race_tsan:arm64+0x10000071c)

  Location is global 'counter' at 0x000104604000 (race_tsan+0x100008000)
  Thread T1 (tid=611626, finished) created by main thread at:
    #0 pthread_create <null> (libclang_rt.tsan_osx_dynamic.dylib:arm64e+0x32b00)
    #1 main <null> (race_tsan:arm64+0x10000067c)

SUMMARY: ThreadSanitizer: data race (race_tsan:arm64+0x100000698) in main+0x48
==================
100000
ThreadSanitizer: reported 1 warnings
```

The final `100000` (instead of `200000`) is the race's real cost: half the
increments were lost, and the compiler and CPU were both entitled to do that.

### Who schedules execution?

The operating system (or the hardware, for interrupt handlers). C has no
cooperative scheduler, no fiber library, and no event loop in the standard —
green threads require platform APIs such as `ucontext`, or a library.

### How are distributed computations represented?

Not at all: no message types, no remote references, no location transparency.
Distribution is expressed as separate processes exchanging bytes over sockets,
with serialization, framing, and failure handling designed entirely by hand.
