# VI. KNOWLEDGE AND GUARANTEES

*Framework questions: {doc}`../../framework/06-knowledge-guarantees`*

## What does the language know before the program runs?

### What can be determined statically?

Every expression's type, declarations and their scopes, linkage and storage
duration, constant expressions (enumeration values, static array sizes,
`_Static_assert` conditions), lvalue-ness, format-string/argument agreement
under `-Wformat`, and all the constraint rules of the standard. What it cannot
determine statically is any *fact about values* — only types.

### What must wait until runtime?

All values: pointer validity, whether an index is in bounds, whether `malloc`
returned memory, what `errno` will be, the actual size of a VLA, which union
member was last written, and which function a function pointer will call.

### What can the compiler infer?

Almost nothing by modern standards: no type inference for variable
declarations (C23's `auto` copies the initializer's type, nothing more), no
return-type inference, no closure or field inference. It infers only what the
grammar already fixes: implicit conversions, `sizeof` results, and the
selection performed by `_Generic`.

### What can it reject?

Constraint violations: calling an undeclared function, assigning between
incompatible pointer types without a diagnostic, wrong argument counts against
a prototype, non-constant initializers for static storage, duplicate
definitions at link time, and non-lvalues in assignment.

```console
$ clang -std=c11 -c undecl.c
undecl.c:1:25: error: call to undeclared function 'helper'; ISO C99 and later do not support implicit function declarations [-Wimplicit-function-declaration]
    1 | int main(void) { return helper(1); }
      |                         ^
1 error generated.
```

```console
$ clang -Wall -c warn2.c
warn2.c:5:12: warning: incompatible pointer types passing 'double *' to parameter of type 'int *' [-Wincompatible-pointer-types]
    5 |     handle(d);
      |            ^
warn2.c:2:18: note: passing argument to parameter 'p' here
    2 | void handle(int *p);
      |                  ^
warn2.c:7:27: warning: format specifies type 'char *' but the argument has type 'int' [-Wformat]
    7 |     printf("value: %s\n", 42);
      |                    ~~     ^~
      |                    %d
warn2.c:4:9: warning: unused variable 'unused' [-Wunused-variable]
    4 |     int unused = 3;
      |         ^~~~~
3 warnings generated.
```

Notice the second block: only the argument-count error is a hard error by
default. Wrong types and wrong format specifiers are *warnings* that a build
without `-Werror` will happily ship.

### What relationships can be expressed in the type system?

Assignment compatibility, qualifiers (`const`/`volatile`/`restrict`/
`_Atomic`), pointer depth, function signatures via prototypes, and struct
identity. There is no subtyping, no variance, no trait bound, no "pointer to
non-null T", no "array of exactly n", and no "either T or error".

### Can types depend on values?

Barely: an array type carries a size expression (constant, or a run-time VLA
value), and `_Generic`/`sizeof` reason about types but not about values of
those types. No dependent types exist, so the type system cannot say "the
length argument matches this array".

```c
#include <stdio.h>
void f(size_t n) {
    int a[100];              /* fixed: requires a constant expression */
    int b[n];                /* VLA: size is only known when this line runs */
    printf("%zu %zu\n", sizeof a, sizeof b);
}
```

VLAs are optional in C11 and later, signalled by `__STDC_NO_VLA__`; this
toolchain implements them, and `-Wvla` reminds you that the size is a run-time
stack allocation.

### Can the language express invariants?

Only weakly: `const` (a promise the programmer can defeat with a cast),
`volatile` (a promise to the optimizer), `_Static_assert` (an invariant over
types and constants), and C23's `constexpr` (values checked by the compiler).
There are no preconditions, postconditions, or refinement types.

```c
#include <stdint.h>
struct wire { uint32_t id; uint16_t kind; };
_Static_assert(sizeof(struct wire) == 8, "wire layout must be 8 bytes");
_Static_assert(sizeof(void *) == 4, "expected 32-bit pointers");
```

```console
$ clang -c asserts.c
asserts.c:4:16: error: static assertion failed due to requirement 'sizeof(void *) == 4': expected 32-bit pointers
    4 | _Static_assert(sizeof(void *) == 4, "expected 32-bit pointers");
      |                ^~~~~~~~~~~~~~~~~~~
asserts.c:4:31: note: expression evaluates to '8 == 4'
    4 | _Static_assert(sizeof(void *) == 4, "expected 32-bit pointers");
      |                ~~~~~~~~~~~~~~~^~~~
1 error generated.
```

### Can programs be partially evaluated?

At the edges, yes: the preprocessor evaluates `#if` arithmetic over macro
constants, constant expressions are folded (enumerations, array bounds,
initializers), whole `static` functions are inlined, and C23 adds `constexpr`
functions called at translation time. There is no general staging, no
partial evaluation of arbitrary functions, and no user-visible compilation
API.

### Can properties be proved?

Not by the language: no proof terms, no dependent types, no refinement or
effect system. Assurance comes from outside — static analyzers (the Clang
static analyzer, cppcheck, Coverity), sanitizers, and tests — none of which
the standard mentions.

## What does the language guarantee?

### What errors are prevented?

Few. The compile step is a legality filter: you cannot use an undeclared
identifier, call a function without a prototype in scope (C99 and later), or
initialize static storage with a non-constant expression. Almost everything
that hurts — bounds, lifetimes, null, races — is not prevented at all.

### What errors are detected?

Constraint violations at compile time (with a required diagnostic), certain
useless-code and format mistakes under `-Wall`, duplicate and undefined
symbols at link time, and nothing whatsoever about values at run time unless
you add tooling.

### What remains the programmer's responsibility?

Memory safety, bounds, initialization, lifetimes, null checks, resource
pairing, thread safety, overflow policy, and the algorithm's correctness — in
short, everything about whether the program is *right*. The standard only
promises that a program without undefined behavior behaves as written.

### What properties can be guaranteed?

That a well-defined program follows the abstract machine: sequencing rules,
storage durations, layout (`sizeof`, `offsetof`, `_Alignof`), minimum integer
widths (`int` at least 16 bits, two's complement since C23), and the specified
library behavior. That is a guarantee about *conforming* programs only.

```c
#include <limits.h>
_Static_assert(INT_MAX >= 32767, "the standard only promises a 16-bit int");
_Static_assert(CHAR_BIT == 8, "a byte may be something other than 8 bits");
_Static_assert(sizeof(long) >= 4, "long is 4 bytes on some ABIs, 8 on others");
```

### What properties can only be tested?

Everything about run-time behavior: absence of leaks, absence of races,
absence of overflows, termination, performance, and correct output. The
language supplies no property to state and no checker to run it.

```console
$ clang -O2 -fsanitize=undefined signed.c -o sg && ./sg
signed.c:4:11: runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
SUMMARY: UndefinedBehaviorSanitizer: undefined-behavior signed.c:4:11
-2147483648
```

Undefined behavior printed here only because a sanitizer was linked in; in a
normal build the same line is simply "whatever the compiler decided".

### What can the compiler prove?

Type correctness of every expression, constantness where required, and — by
assuming you never invoke undefined behavior — that certain branches are
impossible. That last power lets it delete code that your program's logic
relies on.

```c
int no_overflow(int x) {
    if (x + 1 < x) return 1;   /* implies signed overflow: the compiler may assume it cannot happen */
    return 0;                   /* ...and may fold the whole function to `return 0` */
}
```

### What programs are impossible to express safely?

Any program whose safety depends on a fact the type system cannot hold: an
array whose length matches a parameter, a pointer that is non-null, a union
whose active member matches its tag, or data used by two threads under an
unwritten protocol. Those programs can be written, but never *checked* — and
there is no way to mark a function "unsafe" because nothing is safe to begin
with.

### Where can the guarantees be bypassed?

Everywhere, by design: casts (especially through `void *` and `char *`, which
may inspect any object's bytes), unions, `memcpy` into typed storage, inline
assembly, `restrict` promises you break, `const` you cast away, and the
platform's FFI. The bypasses are not escape hatches from an otherwise safe
language — they are the ordinary features.
