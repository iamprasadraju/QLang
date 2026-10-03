# III. COMPUTATION

*Framework questions: {doc}`../../framework/03-computation`*

## How does computation proceed?

### What causes computation to happen?

Statements executed by the abstract machine: `main` is called, control flows
through calls, conditionals, loops, and `goto`, and each executed expression
produces its value and side effects. Nothing is lazy and nothing is reactive -
running the program means running an imperative instruction stream top to
bottom.

### What determines the next step?

The program counter, moved by structured control flow and by function calls
that push and return-pop frames; signals may arrive asynchronously but may only
call async-signal-safe functions without invoking undefined behavior.

### In what order are things evaluated?

Mostly unspecified. C11 replaces the old "sequence point" language with
*sequenced before*: the left operand of `&&`, `||`, `?:`, and `,` is sequenced
before the right, and side effects of a full expression must complete before
the next full expression, but operands of arithmetic operators are unsequenced
and function executions are only *indeterminately* sequenced with one another.

```c
#include <stdio.h>
static int n = 0;
static int next(void) { return ++n; }
int main(void) {
    int x = next() - next();   /* x is -1 or 1: two conforming orders exist */
    printf("x=%d n=%d\n", x, n);
    return 0;
}
```

### Can evaluation be delayed?

Only through control flow: `&&`, `||`, and `?:` evaluate the right side only
when needed, and an `if` guard prevents its block from running. There is no
lazy value, no thunk, no call-by-name, and no delayed expression object -
whenever execution reaches an expression, it is evaluated immediately.

### Can evaluation branch?

`if`/`else`, `switch` (an integer selector with no exhaustiveness checking),
the conditional operator, and `goto`; computed gotos exist as a GCC extension
only. Branching is the only selection mechanism the language has, which is why
state machines are written as switch loops rather than as dispatched values.

### Can evaluation backtrack?

Not natively - there is no trail, no undo log, no solver. Backtracking must be
hand-built: save state on the stack, restore it on failure, or `longjmp` back
to a decision point and try the next alternative.

### Can computation be recursive?

Yes, for functions, including mutual recursion, with each call consuming a
stack frame. The standard guarantees no tail-call optimization, so recursion
depth is bounded by the stack and a deep non-tail recursion can crash the
process; tail recursion is only optimized by the compiler when it happens to
be able to.

### Can computation be suspended and resumed?

No. ISO C has no coroutines, generators, fibers, or first-class continuations:
`setjmp` records a position and `longjmp` later *abandons* the current path to
re-enter it - the intervening frames are gone, not paused. Green threads and
asynchronous I/O must be built from platform APIs such as `ucontext`,
`pthread`, or OS-specific facilities.

### Is computation driven by control flow, rewriting, reduction, search, data dependencies, or something else?

Control flow, exclusively: an imperative stream over an abstract machine with
an explicit program counter. The only rewriting happens in the preprocessor
before the C language begins, and the only reduction happens inside the
compiler as constant folding - neither is part of program execution.

```c
int main(void) { int i = 0; i = i++ + 1; return i; }
```

```console
$ clang -Wall -c uns.c
uns.c:1:34: warning: multiple unsequenced modifications to 'i' [-Wunsequenced]
    1 | int main(void) { int i = 0; i = i++ + 1; return i; }
      |                               ~  ^
1 warning generated.
```

## How is behavior defined and composed?

### How do I define reusable behavior?

Declare a prototype (usually in a header) and define a function once: a named
body of statements with parameters received by value and a declared return
type. Reuse means calling it from another translation unit that included the
header.

### What is a function?

A named block of code with either external linkage (visible to the whole
program through the linker) or internal linkage (`static`, private to the
translation unit), invoked with arguments passed by value. It has no object
identity, no fields, and no captured environment - only its parameters, its
locals, and whatever globals it can see.

### Is behavior a value?

Partially: you can take the address of a function and store it in a function
pointer, and that pointer can be compared, copied, and called. The function
itself is not a value - you cannot copy or construct one, and there is no
closure value at all.

### Can behavior be passed around?

Yes, as a function pointer argument whose type must match the parameter's
prototype exactly - mismatched signatures are diagnosed. The standard library's
`qsort` is the canonical example: it takes a comparison callback, and because
its callback receives no user context, comparison state must live in globals
or thread-local storage.

```c
#include <stdlib.h>
static int cmp(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);          /* three-way compare without branches */
}
/* int v[4] = {3,1,4,1}; qsort(v, 4, sizeof v[0], cmp); */
```

### Can behavior be returned?

Only as a function pointer: a function may return a pointer to another
function, and since functions have static storage duration the pointee stays
valid. Returning a *closure* or a pointer to a block-local function is not
possible in ISO C.

### Can behavior capture context?

Not automatically; every callback API therefore carries context by hand - a
`void *user`/`void *ctx` parameter, a struct of state, or module-level
`static` variables. This single limitation shapes the entire C callback
ecosystem, from POSIX `pthread_create` to UI toolkits.

```c
struct counter { int calls; };
typedef void (*handler)(void *ctx, int event);

static void on_event(void *ctx, int event) {         /* context arrives as data */
    ((struct counter *)ctx)->calls++;                /* the "capture", written out */
}
/* register(on_event, &local_counter); */
```

### How is behavior combined with other behavior?

By sequencing calls, wrapping them in conditionals and loops, dispatching
through function-pointer tables, and letting macros expand to call sequences;
there is no composition operator, no pipeline, and no way to wrap a function
with another without writing the forwarding code yourself.

### What are the basic units of composition?

The function (shared through headers) and the translation unit (shared through
the linker). Data composes via structs and arrays; behavior composes only
through calls and indirect calls.

## How are abstractions formed?

### How do I avoid repeating an idea?

Three tools, each with a price: a `static` helper function (typed, inlinable,
costs a call), a `#define` macro (no call, but textual and untyped), and a
`typedef` (repeats only a name). Header files repeat declarations rather than
implementations.

### How can an idea be generalized?

Not with parametric polymorphism - C has none. Generalize by writing a macro
over token lists, by passing `void *` plus a documented convention, by
hand-writing one function per type, or by using `_Generic` to select among
typed implementations; none of these gives you a checked, instantiated generic
function.

### What can be parameterized?

Function arguments (values and pointers), macro arguments (token sequences),
array bounds (including run-time VLA bounds), and compile-time constants used
in enumerations and `_Static_assert`. Types cannot be parameters - the only
way to write "generic" code is to parameterize over tokens or over `void *`.

### What can be hidden?

File-scope entities marked `static` (functions and objects with internal
linkage), struct definitions that appear only in the implementation file, and
macros you `#undef` after use. An opaque struct is the standard idiom: the
header forward-declares the tag, the caller can only hold pointers to it.

```c
/* widget.h - the interface exposes a name, not a layout */
struct widget;                       /* incomplete type: no size, no members */
struct widget *widget_create(void);
void widget_destroy(struct widget *w);

/* widget.c - only this translation unit sees the definition */
struct widget { int id; char *name; struct widget *next; };
```

### What can be exposed?

Whatever the header contains: prototypes, public `struct` layouts, `typedef`s,
`enum` constants, configuration macros, and `extern` object declarations. The
header file *is* the interface - there is no separate interface construct, no
export list, and no visibility modifier other than `static` versus external
linkage.

### What can depend on another abstraction?

Anything a visible declaration permits: headers include other headers,
functions call any declared function, and macros expand other macros. Because
dependency is textual inclusion, the compiler never sees a dependency graph -
only the flattened result of the `#include` splicing.

### How can abstractions be composed?

By calling functions, embedding structs inside structs, storing pointers to
them, linking translation units together, and parameterizing behavior through
function pointers. Composition is always explicit code; the language offers no
operator for lifting, wrapping, or deriving one abstraction from another.

### At what level can abstraction happen?

Two levels in C11/C17: the preprocessor, which works on tokens before parsing
and is C's real metaprogramming layer, and the language itself, which
abstracts through functions, types, and linkage. C23 adds a small third level:
`constexpr` functions computed by the compiler before execution.
