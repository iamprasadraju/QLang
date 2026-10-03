# II. MEANING

*Framework questions: {doc}`../../framework/02-meaning`*

## What can a program represent?

### What kinds of things can programs represent?

Scalars (integers, floating point, pointers, enums, `_Bool`), aggregates
(arrays, structs, unions), and functions that can be called or have their
address taken. Everything is ultimately a flat image of bytes in memory - there
are no objects, no closures, no algebraic data types, and no values that own
other values.

### What are the fundamental values?

`char`, `short`, `int`, `long`, `long long`, `float`, `double`,
`long double`, `_Bool`, pointers to objects or functions, and integer constants
from enumerations. Widths are only partly fixed (`int` is at least 16 bits;
the standard `stdint.h` header supplies exact widths such as `int32_t` when
the platform has them), so code that assumes `sizeof(int) == 4` is already
non-portable.

### How are values combined?

With operators: arithmetic, comparison, logical, bitwise, assignment, and the
comma operator, all mediated by the usual arithmetic conversions and integer
promotions that widen operands to a common type. Structs and arrays combine by
copy (assignment copies whole aggregates) or by member/subscript access; there
is no user-defined operator overloading in C (that arrives only in C++).

### How are new kinds of values created?

Only by composing the fixed set of type constructors: `struct`, `union`,
`array of T`, `enum`, pointers, function types, and the qualifiers `const`,
`volatile`, `restrict`, and `_Atomic`. `typedef` creates a new *name* for an
existing type, not a new type, and no constructor is parameterized by a type.

### Can values represent alternatives?

Only by hand: pair an `enum` tag with a `union` and keep them consistent
yourself. The type system never ties the tag to the active member, so reading
the wrong arm is undefined behavior, not an error.

```c
enum shape_kind { CIRCLE, SQUARE };
struct shape {
    enum shape_kind kind;   /* the tag is just an int in disguise */
    union { double radius; double side; } u;   /* one storage, many meanings */
};
double area(const struct shape *s) {
    return s->kind == CIRCLE ? 3.14159 * s->u.radius * s->u.radius
                             : s->u.side * s->u.side;
}
```

### Can they represent absence?

By convention only: a null pointer, a sentinel return value such as `EOF` or
`(size_t)-1`, or a separate flag field. Nothing in a pointer type distinguishes
"points at an object" from "points at nothing", so dereferencing an absent
value compiles cleanly and fails silently at run time.

### Can they represent relationships?

Through pointers: struct fields that point at related objects, arrays of
pointers, pointers to pointers, and function pointers for behavior. Graphs,
cycles, and shared substructure are all natural; the flip side is that aliasing
is completely unrestricted and untracked.

### What can the language express as data?

Arbitrary byte-level layouts: structs with implementation-defined padding and
alignment (checkable with `_Static_assert` on `sizeof`/`_Alignof`), unions
overlaying different interpretations, bit-fields for packed flags, exact-width
integers for wire formats, arrays sized at run time (VLAs), and - from C23 -
`#embed` to splice a binary file straight into an initializer.

```c
#include <stdint.h>
struct flags { unsigned a : 1; unsigned b : 1; unsigned : 6; };  /* 1 byte + padding */
union bits  { unsigned u; float f; };                             /* 4 bytes, two names */
struct wire { uint32_t id; uint16_t kind; };
_Static_assert(sizeof(struct wire) == 8, "wire layout must be 8 bytes on every ABI");
```

### What cannot be expressed naturally?

Sum types, parametric containers, closures, references with lifetimes,
non-null pointers, and any invariant over values ("this length matches that
array"). Strings are just `char` arrays with a NUL-termination convention, so
their length, encoding, and ownership are all conventions too.

## What does source code mean?

### What constructs does the language recognize?

A translation unit built from declarations (objects, functions, `typedef`s,
tags, enumerators), statements (expression, compound, `if`, `switch`, loops,
`goto`, `break`, `continue`, `return`), and expressions - plus a separate,
earlier layer of preprocessing directives (`#include`, `#define`, `#if`)
recognized only while producing tokens.

### How is syntax mapped to meaning?

The grammar of C11 Annex C parses tokens into declarations/statements/
expressions, with disambiguation rules such as "an identifier that was
`typedef`-ed names a type", then the constraint rules of each clause are
checked and violations are diagnosed. Note that declarations are read
declarator-first (`int *p[3]` is an array of pointers), which is a parsing
convention, not a semantic one.

### What is the semantic model?

The abstract machine of C11 5.1.2.3: a program is a sequence of executions of
functions manipulating a stored sequence of bytes, and only the observable
side effects (I/O, volatile accesses) constrain the result. Where the standard
does not fix an order, the outcome is *unspecified*; where the standard's rules
are broken, the behavior is *undefined* and no result is prescribed at all.

### What does an expression mean?

A value (possibly `void`) together with whatever side effects its operands
perform, with evaluation ordered only where the standard says so. An expression
whose operands read and write the same scalar without sequencing is undefined
behavior, as is an expression that reads an object outside its lifetime or
through a pointer of the wrong effective type.

```c
int i = 0;
i = 5;            /* i is an lvalue: it designates an object, so assignment writes into it */
i + 1;            /* a value, not an lvalue: there is no object to assign to */
(int)i = 5;       /* constraint violation: the cast result is not an lvalue */
i = i++ + 1;      /* undefined: unsequenced read and write of the same object */
```

### What is a statement?

A unit of control flow in the abstract machine: it executes in order, possibly
transfers control, and completes without producing a value. A compound
statement also opens a block scope in which declarations become visible.

### What does a declaration mean?

It introduces identifiers with a type, a storage class, a scope, and possibly
linkage; if it also causes storage to be reserved, it is a *definition*. A
file-scope `int counter;` without an initializer is a *tentative definition*:
it may be completed by another declaration elsewhere in the same translation
unit, and if nothing else defines it, the compiler must still allocate it.

### What does a program mean?

For a hosted implementation: run startup, execute `main`, run `atexit`
handlers, and produce exactly the observable behavior the standard prescribes.
If the program contains undefined behavior, the standard assigns it no meaning
- the question "what does this program do?" has no conforming answer.

### Is meaning defined by evaluation, transformation, proof, relation, effects, or something else?

Operational effects over the abstract machine, constrained by a *sequenced
before* relation between evaluations: semantics are stated as required behavior
and observable output, not as a denotation, a rewriting rule, or a proof
obligation. There is no formal semantics document and no static analysis
requirement - only "diagnose these constraints, otherwise behave as
specified".

## What does a name refer to?

### What can be named?

Objects, functions, `typedef` names, `struct`/`union`/`enum` tags, members,
enumerators, statement labels, and - in a separate, earlier phase - macros.
Each category lives in one of four language namespaces, plus the preprocessor's
own macro namespace.

### What does a name denote?

An identifier for an object denotes the *storage* of that object, and for a
function denotes its code; the name itself has no value until it is used in an
expression, where lvalue conversion turns it into the stored value. A `typedef`
name denotes a type, which exists only in the compiler's type checker.

### How are bindings created?

By declarations: a block-scope declaration binds when its declaration is
reached (a VLA declaration binds when it executes), a file-scope declaration
binds for the whole translation unit, and `extern` binds to a definition with
matching linkage in this or another translation unit. Macros bind during
preprocessing, before any C declaration exists.

### Where is a name visible?

From its declaration to the end of the innermost enclosing scope; file-scope
names are visible to the end of the translation unit. External linkage makes a
name *linkable* from other translation units, but that is linkage, not scope -
you still must declare it there.

### How are names resolved?

Lexically, innermost declaration first, with tags, members, and labels resolved
in their own namespaces so a struct tag can share a spelling with a variable.
Macros resolve first: a `#define name ...` rewrites every later token spelling
of `name`, which is why library macro names leak into your code.

### Can two names refer to the same thing?

Yes: two pointers can hold the same address, `typedef`s can alias one type,
and `extern` declarations in several translation units all denote one object.
Aliasing has no restrictions; only a `restrict`-qualified pointer carries a
promise that others do not alias it within a block.

### Can names be rebound?

No - an identifier's binding is fixed by its declaration for its entire scope.
Only the object it denotes can be assigned a new value; there is no operation
that makes an existing name mean something else, and no renaming.

### Can names be captured?

Not by the language: a C function never closes over the environment where it
was written. Capture is emulated with an explicit `void *` context parameter,
with `static` state, or - in GCC only - with nested functions, an extension
that builds a trampoline on an executable stack.

```c
struct ctx { int limit; };                       /* the "captured environment" */
static void *ctx_ptr = & (struct ctx){ 100 };    /* passed explicitly, not captured */
static int within(void *v, int x) {              /* the qsort callback shape */
    return x < ((const struct ctx *)v)->limit;
}
```

### What happens when scopes overlap?

The inner declaration shadows the outer one from its point of declaration to
the end of the inner block; there is no warning requirement, so shadowing a
parameter or a global is a common source of confusion. Jumping with `goto`
*into* a block that skips a VLA or variably modified declaration is undefined
behavior.

```c
int x = 1;
void f(void) {
    int x = 2;              /* shadows file-scope x */
    { int x = 3;            /* shadows again */
      /* printf here sees 3 */ }
    /* printf here sees 2 */
}
```

### Are there multiple namespaces?

Yes - four: ordinary identifiers (variables, functions, `typedef`s,
enumerators), tags (`struct`/`union`/`enum`), members (one namespace per
aggregate), and labels (one per function); the preprocessor adds a fifth
non-language namespace for macros. This is why POSIX can have both
`struct stat` and `int stat(const char *restrict, struct stat *restrict)` in
the same scope.

```c
#include <sys/stat.h>
int stat(const char *path, struct stat *st);   /* ordinary namespace */
struct stat info;                              /* tag namespace: no conflict */
/* the same separation lets you write: */
struct wrap { int x; };
int wrap(int x) { return x; }                  /* tag and variable coexist */
```
