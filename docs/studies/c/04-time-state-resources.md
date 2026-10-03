# IV. TIME, STATE, AND RESOURCES

*Framework questions: {doc}`../../framework/04-time-state-resources`*

## What can change?

### What is mutable?

Everything you can form a modifiable lvalue for: local and global objects,
heap memory, array elements, struct members, and - by intent - hardware
registers declared `volatile`. `const` is a compile-time promise to the
programmer, not a runtime property: cast away the qualifier or reach the
object through an earlier alias and nothing stops you.

### What is immutable?

Almost nothing. String literals are the exception - writing through one is
undefined behavior - and a `const` object at file scope usually lands in a
read-only page, but any pointer that existed before the qualification can be
used to write. C has no deep, enforced immutability.

### What is state?

The stored values of all objects: automatic locals, static globals and
function-local statics, allocated blocks, thread-local objects, plus library
state such as `errno`, stream buffers, and the `rand()` seed. State is exactly
"the bytes that a later read can observe".

### Where does state live?

Storage duration decides: automatic objects in the call frame (usually
registers or stack), static objects in the program's data/bss segments,
`malloc`ed blocks in the allocator's arena, `_Thread_local` objects in
per-thread storage. Struct layout, padding, and alignment are
implementation-defined but queryable with `sizeof`, `offsetof`, and
`_Alignof`.

### Who may change it?

Any code that can name the object or reach its address - pointers are
unchecked and there is no access control at run time. `const`, `static`, and
file scope constrain what the *compiler* lets you write, never what the
machine can do.

### Who observes the change?

Whoever next reads through any alias; the only ordering the language enforces
is that a full expression's side effects complete before the next full
expression (and that volatile accesses and I/O are not deleted). Observers in
other threads see whatever the hardware and synchronization allow.

### Can change be isolated?

Not by the language - only by convention (pass copies, keep state inside one
`.c` file) plus the `restrict` qualifier, which lets the compiler assume that
within a block the pointed-to objects are not accessed through other pointers.
Breaking that promise is undefined behavior.

```c
#include <stddef.h>
void add(float * restrict dst,
         const float * restrict a,
         const float * restrict b, size_t n)
{
    for (size_t i = 0; i < n; i++)
        dst[i] = a[i] + b[i];   /* may be vectorized: the three ranges are promised disjoint */
}
```

### Can the compiler reason about change?

Yes: through `const`, `volatile`, `restrict`, flow analysis, and the
effective-type rules of C11 6.5 (strict aliasing), which say a store through
`float *` updates the value of a `float` object - and that reading that
storage as `int` afterwards is undefined. With `-fstrict-aliasing` (on at
`-O2`) the compiler exploits exactly this.

```c
#include <stdio.h>
static int test(int *ip, float *fp) {
    *ip = 0;
    *fp = 1.0f;                 /* the compiler must assume fp does not alias ip */
    return *ip;                 /* ...so it returns the value it believes is stored */
}
int main(void) {
    int a = 5;
    int r = test(&a, (float *)&a);   /* both pointers designate the same object */
    printf("a=%d r=%d\n", a, r);
    return 0;
}
```

```console
$ clang -O0 punned.c -o p && ./p
a=1065353216 r=1065353216
$ clang -O2 punned.c -o p && ./p
a=1065353216 r=0
$ clang -O2 -fno-strict-aliasing punned.c -o p && ./p
a=1065353216 r=1065353216
```

The optimized build returns `0` because it folded `*ip` across the store,
assuming the pointers could not alias; `-fno-strict-aliasing` forces the reload
and the program behaves as written.

### What happens when multiple computations change the same thing?

If two threads modify the same non-atomic object without synchronization, the
result is a data race, and C11 5.1.2.4 states that a data race results in
undefined behavior - not "some value", not "a warning". The defined tools are
mutexes and `_Atomic` objects, and only they establish happens-before edges.

```c
#include <stdatomic.h>
#include <stdio.h>
static _Atomic int counter = 0;          /* the only race-free shared variable */
static void bump(void) {
    for (int i = 0; i < 100000; i++)
        atomic_fetch_add(&counter, 1);   /* read-modify-write, indivisible */
}
int main(void) {
    /* run bump() on two threads, then: */
    printf("%d\n", atomic_load(&counter));   /* always 200000 */
    return 0;
}
```

## What is the lifetime of a thing?

### When is something created?

Static objects exist from program start; automatic objects are created when
their declaration executes (block entry for ordinary types, the declaration
itself for VLAs and compound literals); `malloc` creates an allocated object at
the moment it returns a non-null pointer. There is no constructor concept -
"creation" is just storage becoming usable.

### Where does it live?

Static storage in `__DATA`/bss (or a read-only segment for `const`),
automatic storage in the stack frame, allocated storage wherever the platform
allocator's arena is, thread-local storage per thread, and registers for
values the compiler promotes. Nothing lives "in an object": objects *are* the
storage.

### Who is responsible for it?

The programmer, without exception. There is no destructor, no RAII, no
garbage collector, and no reference counting in ISO C - every allocation has a
matching `free` because you wrote it.

### Who can access it?

Whoever holds its address, plus any code that can compute it (globals,
`extern` declarations, offsets). The language provides no owner check, no
borrow check, no private heap: aliasing is the default and only `restrict`
temporarily narrows it.

### When does it stop existing?

Automatic objects at block exit (or when a `longjmp` leaves the block),
static objects at program termination, allocated objects at `free`, and
temporaries at the end of the full expression that uses them. After that, the
storage may be reused - but existing pointers still hold the old address.

### Can its lifetime be extended?

Only by moving the data somewhere longer-lived - copying into a static buffer,
promoting a local to `static`, or re-allocating - and then updating every
pointer yourself. A pointer never extends the life of its pointee, and C has
no reborrow, pin, or scoped-timing construct.

### Can multiple things refer to it?

Yes, arbitrarily many: pointers, arrays that decay to pointers, structs
holding addresses, and pointers to pointers. Two pointers may designate the
same object at the same time with no way to ask whether they do.

### What happens when it becomes invalid?

Nothing visible happens - until you dereference, and then it is undefined
behavior: you read reused bytes, corrupt unrelated data, or crash. Use-after
free, dangling pointers to dead frames, and double free are the three common
forms, and the language detects none of them.

```c
int *bad(void) {
    int local = 42;
    return &local;             /* storage duration ends at return */
}
/* *bad() is undefined behavior: the frame is gone, the address still "works" until it doesn't */
```

### Who releases its resources?

The programmer, typically in an error path that jumps to a shared cleanup
label. `free(NULL)` is a no-op, double `free` is undefined behavior, and each
non-memory resource (files, sockets, mutexes) has its own manual close routine
that must pair exactly once with its open.

```c
char *p = malloc(n);
if (!p) return -1;             /* allocation failure is a return value, never an exception */
/* ... use p ... */
free(p);
p = NULL;                      /* discipline: only you can prevent dangling pointers */
```

## What happens when computation does not proceed normally?

### How is absence represented?

Sentinel values: `NULL` for pointers, `EOF` for character streams, `(size_t)-1`
or `-1` for lengths and indices, a zero count, or an extra flag field. Which
sentinel a given function uses is documentation, not type information.

### How does failure happen?

A function returns an error indication (negative value, `NULL`, a status code)
and, where the C library specifies it, sets the thread-local `errno`. Failure
is an ordinary return path - nothing unwinds, nothing is thrown, and the
return type is unchanged.

### How does failure propagate?

Manually, one frame at a time: each caller checks the return value and then
returns it, translates it, logs it, or jumps to cleanup. Nothing propagates by
itself, so an unchecked result is a silent failure, not a compile error.

### How are exceptional situations represented?

Not at all in ISO C. The platform provides asynchronous *signals*
(`signal`/`raise`, `SIGSEGV`, `SIGFPE`) whose handlers may only call
async-signal-safe functions, and `setjmp`/`longjmp` provides a two-way
non-local jump that skips every intermediate frame and its cleanup code.

```c
#include <setjmp.h>
#include <stdio.h>
static jmp_buf recovery;
static void deep(int depth, int fail) {
    if (depth == 0) { if (fail) longjmp(recovery, 42); else return; }
    deep(depth - 1, fail);
}
int main(void) {
    int v = 0;
    if (setjmp(recovery) == 0) { v = 1; deep(5, 1); v = 2; }
    else printf("recovered, v=%d\n", v);   /* v is indeterminate: modified after setjmp */
    return 0;
}
```

Compiling that at `-O2` prints `recovered, v=0` while `-O0` prints `v=1`:
automatic variables modified between `setjmp` and `longjmp` keep whatever
value they had in storage, and the register-cached one is lost - the standard
calls them indeterminate.

### Can computation have multiple possible outcomes?

Yes, but only as data: an integer status, a struct with a code, or a sentinel.
The expression's type does not change with the outcome, so "what does this
function return when things go wrong" is always a question about the header's
comments.

### Can it backtrack?

Only by building it yourself: recursion that returns a failure and unwinds the
stack, saved state to restore at each choice point, or `longjmp` to a prior
decision. The language has no trail, no undo, and no resumable computation to
resume *at*.

### Can failure be recovered from?

Anywhere the code checks: `errno` can be cleared, `ferror` can be cleared
after a partial read, `malloc` can be retried, a broken connection can be
reopened. Recovery is always possible in principle and always optional in
practice.

### Can the programmer be forced to handle failure?

Never. Ignoring a return value is legal and common; C23's `[[nodiscard]]`
turns the common case into a warning, and `_Noreturn` documents functions that
never return normally - but no construct makes forgetting an error a
constraint violation.

```c
#include <assert.h>
void set(int *p) {
    assert(p != NULL);         /* erased entirely when NDEBUG is defined */
    *p = 1;
}
```
