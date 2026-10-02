# VIII. SCALE

*Framework questions: {doc}`../../framework/08-scale`*

## How are programs organized and composed at scale?

### How are pieces of a program separated?

Into translation units: each `.c` file compiles independently into an object
file, and the linker merges them into one program. There are no modules,
packages, or namespaces in C11/C17 — separation of concerns is expressed as
file boundaries plus whatever your build system enforces.

### How are names shared?

Through external linkage: a non-`static` definition in one translation unit
satisfies `extern` declarations in others, and the linker resolves everything
in one flat, global namespace. Objects declared without an initializer
(`int counter;`) are *tentative definitions*, which the linker may merge with
compatible definitions in other files.

```c
/* t1.c and t2.c each contain: */
int counter;            /* tentative definition, external linkage */
```

```console
$ clang -fno-common -c t1.c -o t1.o && clang -fno-common -c t2.c -o t2.o && clang t1.o t2.o
duplicate symbol '_counter' in:
    .../t2.o
    .../t1.o
ld: 1 duplicate symbols
clang: error: linker command failed with exit code 1 (use -v to see invocation)
$ clang -c t1.c -o t1.o && clang -c t2.c -o t2.o && clang t1.o t2.o && echo linked
linked
```

Historically the second behavior was universal: tentative definitions were
emitted as "common" symbols and merged silently. GCC 10 and Clang 11 changed
the default to `-fno-common`, turning that silent merge into the link error
above — a 40-year-old compatibility rule visible as a compiler flag.

### How is visibility controlled?

At compile time by `static` (internal linkage, invisible to the linker) versus
`extern`, and at link time by symbol visibility for shared libraries:
`-fvisibility=hidden` plus `__attribute__((visibility("default")))` on
GCC/Clang, `__declspec(dllexport)`/`dllimport` on Windows. Block scope hides
names inside functions, but there is no per-module visibility.

```c
/* util.h */
extern int  shared_counter;      /* published for other translation units */
extern void helper(void);        /* a call the linker must resolve */
/* util.c */
static int cache[64];            /* internal linkage: never leaves this file */
int shared_counter;
void helper(void) { cache[0] = 1; }
```

### How are dependencies represented?

Textually: `#include` splices another file's tokens into yours, guarded by an
include guard or `#pragma once`, and that is the whole dependency mechanism.
The language has no dependency graph, so build systems (Make, CMake, ninja)
reconstruct one from file modification times and manual include paths.

```c
#ifndef QLANG_UTIL_H
#define QLANG_UTIL_H           /* the classic guard: the macro is the identity */
struct widget;                 /* forward declaration beats a nested include */
struct widget *widget_create(void);
void widget_destroy(struct widget *w);
#endif /* QLANG_UTIL_H */

/* Most compilers also accept the non-standard but universal one-liner: */
#pragma once                    /* identifies the file itself, immune to guard-name clashes */
```

### How are interfaces defined?

By header files: prototypes, public `typedef`s and `struct` layouts,
`enum` constants, configuration macros, and comments stating the contract.
The discipline that matters is keeping implementations out of headers — an
opaque struct in the header and the definition in the `.c` file keeps the ABI
stable when the implementation changes.

### How are libraries created?

Compile objects, then either archive them into a static library
(`ar rcs libutil.a util.o`) or build a shared object
(`-shared -fPIC` → `libutil.so`/`.dylib`/`.dll`), and publish the matching
headers as the interface. Linkers pull in static archives member by member and
record shared libraries as runtime dependencies.

```console
$ clang -O2 -c util.c
$ ar rcs libutil.a util.o
$ clang -O2 main.c -L. -lutil -o app
$ otool -L app
app:
	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1351.0.0)
$ nm libutil.a | head -3

util.o:
0000000000000000 T _util_add
```

The archive's `util_add` is copied into `app` at link time (only the platform
runtime remains a dynamic dependency), which is the difference between static
and dynamic linking made visible with one command.

### How are versions handled?

Outside the language entirely: soname versioning (`libfoo.so.2`), ELF symbol
version scripts, header feature-test macros (`_POSIX_C_SOURCE`,
`_DEFAULT_SOURCE`), compile-time probes (`__STDC_VERSION__`, `__has_attribute`),
and platform guards (`#ifdef _WIN32`). There is no package manifest, no
lockfile, and no way for two versions of a library to coexist in one process
without renaming every symbol.

### How does a program grow without becoming unmanageable?

Only through convention: prefix all exported names (`qtp_widget_new`), keep
state `static` by default, prefer forward declarations to nested includes,
expose opaque types instead of layouts, keep translation units small, and
treat the header as a reviewed interface. Nothing in the language stops two
libraries from colliding at link time or a header from pulling in half the
program — the cost of scale is paid in house style and build tooling.
