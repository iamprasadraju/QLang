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

```


What does source code mean?