# QLang Framework V0.1

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

- [✗] Does the language have classes? 
- [✗] Does it have garbage collection? 
- [✗] Does it have ownership? 
- [✗] Does it have async/await? 
- [✗] Is it statically typed?

**Better:**


- [✓] How are abstractions represented? 
- [✓] How is the lifetime of a thing managed? 
- [✓] How do multiple computations coexist? 
- [✓] What does the language know before execution?
<br>

---

## I\. INTENT

### Why does this language exist?

Qusetions:

- [ ] What problem was it created to solve?
- [ ] What existed before it?
- [ ] What was considered insufficient?
- [ ] What does it prioritize?
- [ ] What does it sacrifice?
- [ ] Who is it designed for?
- [ ] What kinds of programs does it make natural?
- [ ] What kinds of programs does it make difficult?
- [ ] What languages or ideas influenced it?

In simpler words:

> Why was this language created, and what does its design care about?

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

---

## II\. MEANING

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
<br>



## III\. COMPUTATION

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

>How do I avoid repeating ideas and control what other parts of the program can see?

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

## IV\. TIME, STATE, AND RESOURCES

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