# The QLang Framework

A good question should satisfy most of these:

- It makes sense before knowing the language's solution.
- It applies to radically different kinds of languages.
- The answer can be "the language does not provide this" without making the question meaningless.
- One question reveals multiple related mechanisms.
- The answer exposes design decisions and tradeoffs.
- The answer can be investigated experimentally.
- The answer connects to other questions.


Avoid questions that already assume a particular mechanism.


**Bad:**

- ✗ Does the language have classes?
- ✗ Does it have garbage collection?
- ✗ Does it have ownership?
- ✗ Does it have async/await?
- ✗ Is it statically typed?

**Better:**


- ✓ How are abstractions represented?
- ✓ How is the lifetime of a thing managed?
- ✓ How do multiple computations coexist?
- ✓ What does the language know before execution?

<!-- end:preamble -->

---

## I. INTENT

### Why does this language exist?

What we're asking:

> Why was this language created, and what does its design care about?

In simpler words:

> What problem was this language built to solve, and what did it give up to solve it?

Questions:

- [ ] What problem was it created to solve?
- [ ] What existed before it?
- [ ] What was considered insufficient?
- [ ] What does it prioritize?
- [ ] What does it sacrifice?
- [ ] Who is it designed for?
- [ ] What kinds of programs does it make natural?
- [ ] What kinds of programs does it make difficult?
- [ ] What languages or ideas influenced it?

Covered topics:

```text
history
design goals
design philosophy
influences
target users
target domains
tradeoffs
language evolution
```

<!-- end:intent -->

---

## II. MEANING

### What can a program represent?

What we're asking:

> What kinds of things can I create, describe, and manipulate in this language?

In simpler words:

> What kinds of data and values exist?


Questions:

- [ ] What kinds of things can programs represent?
- [ ] What are the fundamental values?
- [ ] How are values combined?
- [ ] How are new kinds of values created?
- [ ] Can values represent alternatives?
- [ ] Can they represent absence?
- [ ] Can they represent relationships?
- [ ] What can the language express as data?
- [ ] What cannot be expressed naturally?

Covered topics:

```text
primitive types
compound types
arrays
tuples
records
structs
classes
enums
unions
sum types
product types
option/maybe
functions as values
generics
dependent types
refinement types
```


### What does source code mean?

What we're asking:

> When I write a piece of code, what does the language say that code means?

In simpler words:

> How does written code acquire meaning?

Questions:

- [ ] What constructs does the language recognize?
- [ ] How is syntax mapped to meaning?
- [ ] What is the semantic model?
- [ ] What does an expression mean?
- [ ] What is a statement?
- [ ] What does a declaration mean?
- [ ] What does a program mean?
- [ ] Is meaning defined by evaluation, transformation, proof, relation, effects, or something else?

Covered topics:

```text
syntax
grammar
expressions
statements
declarations
semantics
evaluation
denotational semantics
operational semantics
reduction
elaboration
```

### What does a name refer to?

What we're asking:

> When I give something a name, what exactly does that name stand for?

In simpler words:

> How does a name connect to something in the program?

Questions:

- [ ] What can be named?
- [ ] What does a name denote?
- [ ] How are bindings created?
- [ ] Where is a name visible?
- [ ] How are names resolved?
- [ ] Can two names refer to the same thing?
- [ ] Can names be rebound?
- [ ] Can names be captured?
- [ ] What happens when scopes overlap?
- [ ] Are there multiple namespaces?

Covered topics:

```text
names
bindings
scope
lexical scope
dynamic scope
environments
shadowing
closures
references
aliasing
namespaces
symbol resolution
```

<!-- end:meaning -->

## III. COMPUTATION

### How does computation proceed?

What we're asking:

> Once a program starts running, what determines what happens next?

In simpler words:

> How does the program move from one computation to another?

Questions:

- [ ] What causes computation to happen?
- [ ] What determines the next step?
- [ ] In what order are things evaluated?
- [ ] Can evaluation be delayed?
- [ ] Can evaluation branch?
- [ ] Can evaluation backtrack?
- [ ] Can computation be recursive?
- [ ] Can computation be suspended and resumed?
- [ ] Is computation driven by control flow, rewriting, reduction, search, data dependencies, or something else?

Covered topics:

```text
evaluation order
control flow
conditionals
loops
recursion
pattern matching
lazy evaluation
eager evaluation
backtracking
generators
coroutines
continuations
```

### How is behavior defined and composed?

What we're asking:

> How do I define reusable behavior, and how do I combine pieces of behavior?

In simpler words:

> How do I make something happen and reuse that behavior elsewhere?

Questions:

- [ ] How do I define reusable behavior?
- [ ] What is a function?
- [ ] Is behavior a value?
- [ ] Can behavior be passed around?
- [ ] Can behavior be returned?
- [ ] Can behavior capture context?
- [ ] How is behavior combined with other behavior?
- [ ] What are the basic units of composition?

Covered topics:

```text
functions
procedures
methods
closures
lambdas
function pointers
higher-order functions
callbacks
objects
predicates
relations
composition
```

### How are abstractions formed?

What we're asking:

> How do I take an idea and turn it into something reusable, general, and composable?

In simpler words:

> How do I avoid repeating ideas and control what other parts of the program can see?

Questions:

- [ ] How do I avoid repeating an idea?
- [ ] How can an idea be generalized?
- [ ] What can be parameterized?
- [ ] What can be hidden?
- [ ] What can be exposed?
- [ ] What can depend on another abstraction?
- [ ] How can abstractions be composed?
- [ ] At what level can abstraction happen?

Covered topics:

```text
functions
modules
classes
interfaces
traits
generics
templates
typeclasses
macros
abstract data types
encapsulation
information hiding
metaprogramming
```

<!-- end:computation -->

## IV. TIME, STATE, AND RESOURCES

### What can change?

What we're asking:

> What can change during execution, and who is allowed to change it?

In simpler words:

> How does the language deal with state and mutation?

Questions:

- [ ] What is mutable?
- [ ] What is immutable?
- [ ] What is state?
- [ ] Where does state live?
- [ ] Who may change it?
- [ ] Who observes the change?
- [ ] Can change be isolated?
- [ ] Can the compiler reason about change?
- [ ] What happens when multiple computations change the same thing?

Covered topics:

```text
state
mutation
immutability
assignment
mutable variables
mutable objects
aliasing
references
shared state
isolation
persistent data
```

### What is the lifetime of a thing?

What we're asking:

> When something is created, how long does it exist, and who controls when it stops existing?

In simpler words:

> Who is responsible for the existence of a thing?

Questions:

- [ ] When is something created?
- [ ] Where does it live?
- [ ] Who is responsible for it?
- [ ] Who can access it?
- [ ] When does it stop existing?
- [ ] Can its lifetime be extended?
- [ ] Can multiple things refer to it?
- [ ] What happens when it becomes invalid?
- [ ] Who releases its resources?

Covered topics:

```text
stack
heap
allocation
deallocation
pointers
references
ownership
borrowing
lifetimes
garbage collection
reference counting
move semantics
RAII
resource management
memory layout
alignment
```

### What happens when computation does not proceed normally?

What we're asking:

> How does the language represent situations where computation does not produce its normal result?

In simpler words:

> What happens when something is missing, fails, goes wrong, or has multiple possible outcomes?

Questions:

- [ ] How is absence represented?
- [ ] How does failure happen?
- [ ] How does failure propagate?
- [ ] How are exceptional situations represented?
- [ ] Can computation have multiple possible outcomes?
- [ ] Can it backtrack?
- [ ] Can failure be recovered from?
- [ ] Can the programmer be forced to handle failure?

Covered topics:

```text
absence
Option
Maybe
Result
Either
error codes
exceptions
panic
assertions
contracts
failure propagation
backtracking
nondeterminism
```

<!-- end:state -->

## V. WORLD

### How does a program interact with the outside world?

What we're asking:

> How does a program affect or observe things outside its own computation?

In simpler words:

> How does the program talk to the real world?


Questions:

- [ ] How does it perform I/O?
- [ ] How does it access files?
- [ ] Networks?
- [ ] Processes?
- [ ] Hardware?
- [ ] Time?
- [ ] Randomness?
- [ ] Operating-system functionality?
- [ ] Foreign code?
- [ ] External resources?


Covered topics:

```text
I/O
files
stdin/stdout
networking
system calls
processes
environment
hardware
FFI
foreign functions
effects
effect systems
resources
```

### How do multiple computations coexist?

What we're asking:

> How can independent computations execute and interact with one another?

In simpler words:

> How does the language deal with concurrency and communication between computations?

Questions:

- [ ] Can computations execute simultaneously?
- [ ] What can they share?
- [ ] How do they communicate?
- [ ] How is shared state handled?
- [ ] How is synchronization handled?
- [ ] Can races occur?
- [ ] Can the language detect or prevent them?
- [ ] Who schedules execution?
- [ ] How are distributed computations represented?

Covered topics:

```text
processes
threads
shared memory
locks
mutexes
atomics
message passing
channels
actors
tasks
async/await
futures
coroutines
transactions
distributed computation
```

<!-- end:world -->

## VI. KNOWLEDGE AND GUARANTEES

### What does the language know before the program runs?

What we're asking:

> Which things can the language figure out, check, or reject before executing the program?

In simpler words:

> What can the compiler or checker discover ahead of time?

Questions:

- [ ] What can be determined statically?
- [ ] What must wait until runtime?
- [ ] What can the compiler infer?
- [ ] What can it reject?
- [ ] What relationships can be expressed in the type system?
- [ ] Can types depend on values?
- [ ] Can the language express invariants?
- [ ] Can programs be partially evaluated?
- [ ] Can properties be proved?

Covered topics:

```text
static analysis
type checking
type inference
static typing
generic constraints
subtyping
exhaustiveness checking
const evaluation
compile-time evaluation
compile-time computation
dependent types
refinement types
effect checking
ownership checking
borrow checking
proof checking
formal verification
```

### What does the language guarantee?

What we're asking:

> What properties does the language enforce strongly enough that I can rely on them?

In simpler words:

> What mistakes can the language stop me from making?

Questions:

- [ ] What errors are prevented?
- [ ] What errors are detected?
- [ ] What remains the programmer's responsibility?
- [ ] What properties can be guaranteed?
- [ ] What properties can only be tested?
- [ ] What can the compiler prove?
- [ ] What programs are impossible to express safely?
- [ ] Where can the guarantees be bypassed?

Covered topics:

```text
type safety
memory safety
null safety
race freedom
exhaustiveness
immutability guarantees
purity
termination
contracts
invariants
proofs
soundness
unsafe escape hatches
```

<!-- end:guarantees -->

## VII. PROGRAMS ABOUT PROGRAMS

### What can a program know or do about other programs?

What we're asking:

> Can the language treat programs, code, or types as things that can themselves be inspected, manipulated, generated, or reasoned about?

In simpler words:

> Can programs work with programs?

Questions:

- [ ] Can code inspect code?
- [ ] Can code generate code?
- [ ] Can syntax be manipulated?
- [ ] Can programs execute during compilation?
- [ ] Can programs inspect types?
- [ ] Can the language extend itself?
- [ ] Can the programmer introduce new syntax?
- [ ] Can proof or metadata about programs be represented?

Covered topics:

```text
macros
reflection
code generation
compile-time programming
metaprogramming
syntax transformation
ASTs
DSLs
staging
proof terms
quotation
```


<!-- end:programs -->

## VIII. SCALE

### How are programs organized and composed at scale?

What we're asking:

> How can a small program grow into a large program without becoming unmanageable?

In simpler words:

> How does the language help me organize a big codebase?

Questions:

- [ ] How are pieces of a program separated?
- [ ] How are names shared?
- [ ] How is visibility controlled?
- [ ] How are dependencies represented?
- [ ] How are interfaces defined?
- [ ] How are libraries created?
- [ ] How are versions handled?
- [ ] How does a program grow without becoming unmanageable?

Covered topics:

```text
modules
packages
namespaces
imports
exports
visibility
libraries
interfaces
dependency systems
package managers
versioning
build systems
linking
```

<!-- end:scale -->

## IX. EXECUTION

### How does source become execution?

What we're asking:

> How does code written by a programmer eventually become behavior executed by a machine or runtime?

In simpler words:

> What happens between writing the code and the computer actually running it?

Questions:

- [ ] How is source parsed?
- [ ] How is meaning checked?
- [ ] What is elaborated?
- [ ] What is inferred?
- [ ] What code is generated?
- [ ] What is evaluated at compile time?
- [ ] What gets erased?

Covered topics:

```text
lexing
parsing
AST
semantic analysis
elaboration
type checking
IR
optimization
code generation
bytecode
virtual machines
interpreters
JIT
AOT
native code
linking
runtime
```

<!-- end:execution -->

## X. STYLE

### What style of programming does the language make natural?

What we're asking:

> What ways of thinking and structuring programs does the language encourage?

In simpler words:

> What kind of code feels natural in this language?


Questions:

- [ ] What does this language make easy?
- [ ] What does it make awkward?
- [ ] What does idiomatic code look like?
- [ ] What abstractions naturally emerge?
- [ ] What patterns fight the language?
- [ ] What way of thinking does the language encourage?

Covered topics:

```text
imperative programming
procedural programming
functional programming
object-oriented programming
logic programming
declarative programming
generic programming
data-oriented programming
concurrent programming
event-driven programming
```

<!-- end:style -->

## XI. UNIQUENESS

### What is fundamentally unusual about this language?

What we're asking:

> After answering the universal questions, what does this language do that deserves special attention?

In simpler words:

> What is this language's unusual answer to a programming problem?

Questions:

- [ ] What does this language do differently?
- [ ] What problem does that difference solve?
- [ ] Why is the ordinary solution insufficient?
- [ ] What does this mechanism enable?
- [ ] What does it cost?
- [ ] What concepts depend on it?
- [ ] What would be difficult without it?

Covered topics:

```text
unique language features
unusual semantics
unusual type systems
unusual memory models
unusual execution models
unusual abstractions
language-specific metaprogramming
language-specific guarantees
```

<!-- end:uniqueness -->

---

## THE FINAL MENTAL MODEL

After investigating everything, explain the language without listing its features.

Answer:

- Why does it exist?
- What can programs represent?
- What does source code mean?
- What does a name refer to?
- How does computation proceed?
- How is behavior defined and composed?
- How are abstractions formed?
- What can change?
- What is the lifetime of a thing?
- How does failure work?
- How does the program interact with the world?
- How do multiple computations coexist?
- What does the language know before execution?
- What does it guarantee?
- What can programs do about programs?
- How do programs scale?
- How does source become execution?
- What style does it make natural?
- What makes it unusual?

If you can answer these clearly, you should have a structural mental model of the language rather than a memorized feature list.

### The Learning Loop

For each question:

```text
ASK
 ↓
UNDERSTAND THE QUESTION
 ↓
FIND THE LANGUAGE'S ANSWER
 ↓
BUILD A SMALL EXPERIMENT
 ↓
BREAK IT
 ↓
OBSERVE
 ↓
EXPLAIN
 ↓
IDENTIFY TRADEOFFS
 ↓
CONNECT TO OTHER QUESTIONS
```

The repository preserves this process: each language directory is an experimental answer to the same universal questions.

### What Does NOT Belong in the Universal Map?

These are useful things to learn, but they should not become primary universal questions:

- Does it have classes?
- Does it have pointers?
- Does it have garbage collection?
- Does it have generics?
- Does it have async/await?
- Does it have operator overloading?
- Does it have decorators?
- Does it have inheritance?
- Does it have pattern matching?

These are mechanisms.

The map should ask about the problem from which those mechanisms emerge.

### The Self-Correction Rule

The map is never finished.

When studying a new language, something may happen: the language does something that the current map cannot explain. Do not force it into an existing category.

Ask:

> What question did we fail to ask?

Then improve the map.

```text
Universal Questions
        ↓
    New Language
        ↓
 Unexpected Concept
        ↓
"What question explains this?"
        ↓
 Improve Map
        ↓
    Next Language
```

The ultimate purpose of the project is therefore not merely to produce a checklist.

It is to discover:

> What are the fundamental questions of programming languages?