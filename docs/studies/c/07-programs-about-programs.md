# VII. PROGRAMS ABOUT PROGRAMS

*Framework questions: {doc}`../../framework/07-programs-about-programs`*

## What can a program know or do about other programs?

### Can code inspect code?

No. There is no reflection: a running program cannot enumerate its own
functions, fields, annotations, or call graph, and there is no runtime type
information. A C program can inspect *data* that happens to be source text -
debuggers, parsers, and `grep` exist - but that is reading files, not
introspection.

### Can code generate code?

Yes, but by staging outside the language: a `#include` pulls in a generated
file, macros emit token sequences, and generator tools (`lex`, `yacc`/
`bison`, SWIG, protobuf-c) run as separate build steps that print ordinary C
which the compiler then treats as hand-written.

```c
#define DEF_ID(name, type) type name(type x) { return x; }
DEF_ID(id_int, int)          /* the macro is a tiny code generator */
DEF_ID(id_long, long)
```

```console
$ clang -E codegen.c | grep -v '^#' | grep -v '^$'
int id_int(int x) { return x; }
long id_long(long x) { return x; }
```

### Can syntax be manipulated?

Only at the token level, before parsing: `#` stringifies, `##` concatenates,
`#include` splices whole files, and `#if`/`#else` selects between token
streams. Because the preprocessor has no notion of grammar, it cannot respect
scopes or types - it is a text tool applied to a language it cannot parse.

```c
#define STR(x)    #x
#define XSTR(x)   STR(x)
#define JOIN(a,b) a##b
enum { JOIN(my_, code) = 7 };   /* declares my_code */
/* STR(1 + 2) is the string "1 + 2"; XSTR expands first, then stringifies */
```

### Can programs execute during compilation?

Partly. The preprocessor evaluates `#if` arithmetic (undefined identifiers
count as 0), constant expressions are computed for enumerations, array bounds,
and `_Static_assert`, and C23 adds `constexpr` functions the compiler calls
during translation. Arbitrary code execution at compile time does not exist:
there is no embedded interpreter and no way to run I/O from a declaration.

```c
#define VERSION 3
#if VERSION >= 2 && VERSION < 4
    /* chosen by arithmetic performed before the C language is even parsed */
#endif
#if UNDEFINED_MACRO      /* evaluates to 0 rather than an error */
    /* never compiled */
#endif
```

```console
$ clang -std=c23 -c constexpr.c
constexpr.c:1:1: error: 'constexpr' can only be used in variable declarations
    1 | constexpr int square(int n) { return n * n; }
      | ^
constexpr.c:2:16: error: static assertion expression is not an integral constant expression
    2 | _Static_assert(square(11) == 121, "computed before main exists");
      |                ^~~~~~~~~~~~~~~~~
```

This is what "emerging" looks like in practice: C23 specifies `constexpr`
functions, but the installed toolchain here (Clang 17) still rejects them, so
compile-time function execution is a feature you must probe for, not assume.

### Can programs inspect types?

At compile time and shallowly: `sizeof`, `_Alignof`, `_Generic` (select one of
several expressions by the type of an operand), and `typeof`/`__typeof__`
(build a declaration from an expression's type, standardized as `typeof` in
C23). None of them can enumerate a struct's members, produce a type name at
run time, or walk a type graph - there is no RTTI.

```c
#define type_name(x) _Generic((x), \
    int:    "int",                 \
    long:   "long",                \
    double: "double",              \
    char *: "char *",              \
    default: "other")
/* type_name(42) expands to "int" - chosen while compiling, erased afterwards */
```

### Can the language extend itself?

Only by textual macro expansion, which runs before the language does. Macros
can invent surface shapes (`FOREACH(x, list)`) and rewrite existing tokens,
but every expansion must still parse as standard C, and the extensions are
unhygienic: they capture names, break on commas in arguments, and produce
error messages quoted from the expanded text rather than your source.

### Can the programmer introduce new syntax?

No. Keywords are reserved and the grammar is fixed by the standard; only the
implementation may add words (C23 adopted `typeof`, `nullptr`, `auto` as a
specifier, `constexpr`), and compilers may accept extensions (`statement
expressions`, nested functions in GCC). User code gets macros, which reshape
tokens without ever becoming syntax.

```c
#include <stdio.h>
#define FOREACH(x, xs) for (size_t i = 0; (x) = (xs)[i], i < n; i++)
/* usable, but unhygienic: `i` and `n` are captured from the surrounding scope */
```

### Can proof or metadata about programs be represented?

As attributes and assertions, not as proofs: C11 provides `_Noreturn`,
`alignas`, and `_Static_assert`; C23 standardizes attribute syntax
(`[[nodiscard]]`, `[[deprecated]]`, `[[maybe_unused]]`, `[[fallthrough]]`,
plus implementation names such as `[[gnu::...]]`). Documentation, static
analyzer annotations (SAL, `_Nonnull`), and comments carry metadata for tools
only - no proof terms, no contracts checked by the compiler, no dependent
indexing of any kind.
