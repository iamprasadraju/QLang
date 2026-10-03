# I. INTENT

*Framework questions: {doc}`../../framework/01-intent`*

## Why does this language exist?

### What problem was it created to solve?

C was created at Bell Labs between 1972 and 1973 so that the UNIX operating
system could be rewritten in something better than PDP-11 assembly while still
controlling the machine: byte-addressable pointers, explicit memory layout, and
a runtime small enough to sit underneath an operating system. Ritchie's own
account, "The Development of the C Language", frames the goal as keeping the
expressiveness of a high-level language without losing direct access to the
hardware.

### What existed before it?

UNIX was first written in PDP-7 assembly; then came BCPL (Martin Richards,
1967), which Thompson stripped down into B for the PDP-7 and later PDP-11.
B was a typeless language in which every value was one machine word and arrays
were indexed in words rather than bytes.

### What was considered insufficient?

B's word-typed model could not use the PDP-11's byte addressing or floating
point, and its interpreter was slow for system code; assembly was portable only
by rewriting everything per machine. C was the fix: a real type system (types
that change how values are represented), native code generation, and a grammar
close enough to the machine that pointer arithmetic mapped onto a single
instruction.

### What does it prioritize?

Portability with predictable cost: a tiny standard library, no garbage
collector, no virtual machine, no hidden allocation, and semantics that map
onto whatever hardware the compiler targets. A conforming program written once
should compile and behave the same on any conforming implementation, which is
exactly what made UNIX portable.

### What does it sacrifice?

Safety and abstraction. There is no bounds checking, no overflow checking, no
lifetime tracking, no exceptions, no namespaces, no reflection, and no type
system mechanism for nullability, ownership, or invariants — every one of those
is delegated to the programmer and to convention.

### Who is it designed for?

Systems programmers: people writing operating systems, compilers, runtimes,
device drivers, embedded firmware, and performance-critical infrastructure who
need to know precisely what the generated code will do. It assumes a competent,
careful author rather than protecting a casual one.

### What kinds of programs does it make natural?

Anything that mirrors the machine: kernels and bootloaders, interpreters and
virtual machines, compilers, embedded and real-time control, parsers, numeric
simulators, command-line tools, and libraries meant to be called from other
languages. Small single-file utilities compile and run in milliseconds.

### What kinds of programs does it make difficult?

Large application domains that benefit from a runtime: GUIs, business logic
with deep domain models, safe concurrent or distributed systems, and anything
needing generic containers, reflective frameworks, or garbage-collected object
graphs — all must be rebuilt by hand, which is why such code in C grows
fragile quickly.

### What languages or ideas influenced it?

BCPL and B are the direct ancestors (C kept their operator vocabulary and their
"everything is a machine word" attitude, then rejected it), and Ritchie cited
debts to ALGOL 68 for structure and member access and to Pascal-family type
systems for record types and typedef; the PDP-11 assembly model shaped pointers
and layout, and UNIX's portability goal shaped the standard library. C in turn
became the ancestor of C++, Objective-C, Java, C#, Go, Rust, and Zig.

```c
/* K&R (pre-ANSI) definition, the style C had when it left Bell Labs */
double power(base, e)      /* parameters named in the header ... */
double base;               /* ... types declared separately below */
int e;
{
    return e > 0 ? base * power(base, e - 1) : 1.0;
}
```
