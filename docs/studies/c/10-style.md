# X. STYLE

*Framework questions: {doc}`../../framework/10-style`*

## What style of programming does the language make natural?

### What does this language make easy?

Straight-line, performance-critical code: exact control over layout and
allocation, bit manipulation, hardware access, and small tools that compile in
seconds. Data-oriented code with plain structs and loops over them is both
natural and fast, because it is what the machine executes anyway.

### What does it make awkward?

Anything that needs scaffolding: generic containers, long chains of error
checks that each return manually, Unicode text handling, deep domain models,
GUI code, and safe concurrency. Simulated object hierarchies and "framework"
code require enormous boilerplate for what other languages express in a line.

### What does idiomatic code look like?

Small structs with free functions taking pointers to them, `const` on every
pointer the function does not modify, one header per translation unit with a
shared name prefix, `static` by default, explicit error returns, and a single
cleanup path reached with `goto`:

```c
int copy_file(const char *src, const char *dst) {
    FILE *in = NULL, *out = NULL;
    int rc = -1;
    if (!(in  = fopen(src, "rb")))  goto done;
    if (!(out = fopen(dst, "wb")))  goto done;
    /* ... transfer ... */
    rc = 0;
done:
    if (in)  fclose(in);
    if (out) fclose(out);
    return rc;
}
```

That `goto cleanup` shape — one label, resources released in reverse order,
single exit value — is the C substitute for destructors and exceptions, and it
is the single most characteristic idiom in the language.

### What abstractions naturally emerge?

Opaque handles with create/destroy pairs, tables of function pointers acting
as interfaces or vtables, callback-plus-context APIs, tagged unions for
domains with alternatives, and macro-generated boilerplate — each one
hand-rolling what other languages provide as a keyword.

```c
struct tok;                        /* forward declaration: the type lives elsewhere */
struct parser_ops {
    int  (*start)(void *self);
    int  (*token)(void *self, struct tok *out);
    int  (*finish)(void *self);
    void (*destroy)(void *self);
};                                  /* a vtable the programmer maintains by hand */
```

### What patterns fight the language?

Deep inheritance trees built from embedded structs and casts, RAII emulated
without destructors, exception-style error frameworks layered on return codes,
macro DSLs that defeat debuggers and break on comma-containing arguments,
heavyweight generic libraries written as macro repetition, and any design that
hides allocation or copying behind innocent-looking calls.

### What way of thinking does the language encourage?

Procedural, imperative, data-oriented thinking with an explicit mental model
of memory: every value has an address and a lifetime, every call has a cost,
every error must be checked, and every resource must be paired. The programmer
is the type checker, the garbage collector, the ownership system, and the
concurrency auditor — the style is "think first, the compiler will not save
you".
