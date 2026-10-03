# IX. EXECUTION

*Framework questions: {doc}`../../framework/09-execution`*

## How does source become execution?

### How is source parsed?

Through the phases of translation (C11 5.1.1.2): trigraph replacement
(removed in C23), line splicing of backslash-newline, escape decoding in
strings, splitting into preprocessing tokens, execution of directives, and only
then tokenization and parsing into a syntax tree. The preprocessor output is a
different program from the one you wrote, and the parser never sees the
original lines.

```c
int x = 1 \
    + 2;
const char *g = "hello, " \
                "world";
```

```console
$ clang -E phase.c | grep -v '^#' | grep -v '^$'
int x = 1 + 2;
const char *g = "hello, " "world";
$ clang -Xclang -dump-tokens -fsyntax-only phase.c 2>&1 | grep -E "plus|'2'|string_literal"
plus '+'	 [LeadingSpace]	Loc=<phase.c:2:5>
numeric_constant '2'	 [LeadingSpace]	Loc=<phase.c:2:7>
string_literal '"hello, "'	 [LeadingSpace]	Loc=<phase.c:3:17>
string_literal '"world"'	 [LeadingSpace]	Loc=<phase.c:4:17>
```

Note the locations: the preprocessor printed each statement as a single line,
yet the tokens still carry their positions in the physical file - `+` and `2`
on line 2 (the splice continuation), the strings on lines 3 and 4.
Diagnostics will point at `phase.c`, even though the program the parser
received has been reflowed onto different lines.

### How is meaning checked?

During semantic analysis against the declarations in scope: every expression's
type is checked, constraint violations are diagnosed (a diagnostic is required
for them), and then the standard's famous gap applies - a program that is
*well-formed but undefined* requires no diagnostic at all. The compiler
guarantees well-typedness, never correctness.

### What is elaborated?

Very little: implicit conversions (integer promotions, array-to-pointer decay,
function-to-pointer decay, lvalue conversion), default zero-initialization of
static storage, and the default argument promotions for variadic calls. No
wrappers are inserted, no traits resolved, no generics monomorphized - the
source maps almost one-to-one onto the machine's operations.

### What is inferred?

Almost nothing. K&R definitions let the compiler infer parameter types from
the argument list (a legacy feature, now deprecated), C23's `auto` takes an
initializer's type, and `sizeof`/`typeof` derive declarations from types; the
only other "inference" is the optimizer assuming you never invoked undefined
behavior.

```console
$ clang -std=c17 -Wall -c knr.c
knr.c:1:8: warning: a function definition without a prototype is deprecated in all versions of C and is not supported in C23 [-Wdeprecated-non-prototype]
    1 | double power(base, e)
      |        ^
1 warning generated.
```

### What code is generated?

Native machine code, ahead of time: the compiler lowers the tree to its own
IR (Clang to LLVM IR, GCC to GENERIC/GIMPLE), optimizes, emits assembly, and
the assembler produces an object file with a symbol table that a linker turns
into an executable. The ISO standard specifies only that the result must
behave like the abstract machine; it says nothing about how.

```console
$ clang -E hello.c -o hello.i
$ clang -S hello.i -o hello.s
$ clang -c hello.s -o hello.o
$ clang hello.o -o hello && ./hello
hi
$ wc -c hello.i hello.s hello.o hello
   25969 hello.i
     942 hello.s
     728 hello.o
   33432 hello
   61071 total
```

The 26 KB of preprocessed header text becomes a 728-byte object file and then
a 33 KB dynamically linked executable - most of it the C runtime and the
program's own code, none of it the standard library's source.

```asm
_main:                                  ; @main
	.cfi_startproc
; %bb.0:
	sub	sp, sp, #32
	stp	x29, x30, [sp, #16]             ; 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 16
	.cfi_offset w30, -8
	.cfi_offset w29, -16
	mov	w8, #0                          ; =0x0
```

### What is evaluated at compile time?

Preprocessor conditionals and arithmetic, constant expressions (enumeration
values, static array sizes, initializers, `_Static_assert`), constant folding,
inlining, and - in C23 - `constexpr` calls with constant arguments. The
constant `3 * 4` below is already the immediate `12` in unoptimized output:

```asm
_f:                                     ; int f(void) { return 3 * 4 + g(); }
	.cfi_startproc
; %bb.0:
	stp	x29, x30, [sp, #-16]!           ; 16-byte Folded Spill
	mov	x29, sp
	bl	_g
	add	w0, w0, #12                     ; 3 * 4 was folded at compile time
	ldp	x29, x30, [sp], #16             ; 16-byte Folded Reload
	ret
```

### What gets erased?

Comments and preprocessor artifacts (the preprocessor's output *is* the program
the compiler parses), typedef names and type qualifiers (`const`, `restrict`)
which exist only inside the compiler, `static` functions the optimizer
inlined or discarded, and - unless `-g` was passed - essentially all type
information. What remains in the binary is addresses, instructions, and
strings.

```c
typedef unsigned long ulong_t;
static int helper(int x) { return x + 1; }
int main(void) { return helper(0); }
```

```console
$ clang -O0 -S erase.c -o erase0.s && grep -c helper erase0.s
3
$ clang -O2 -S erase.c -o erase2.s && grep -c helper erase2.s
0
$ grep -cE 'typedef|restrict|const' erase2.s
0
```

At `-O0` the `helper` function is emitted as a real symbol; at `-O2` it is
inlined into its only caller and the symbol disappears entirely, along with
every trace of the source-level qualifiers.
