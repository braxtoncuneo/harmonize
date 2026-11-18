# Harmonize

Harmonize is an execution framework for GPUs that exposes their parallel
processing capabilities through **asynchronous (async) processing calls**.

It aims to improve program performance while decreasing your development
burden, especially **when your project requires complex processing tasks**.
In short, Harmonize is designed to help you **parallelize more of your
projects without requiring you to be an expert at writing GPU code** (such as
[CUDA](https://docs.nvidia.com/cuda/doc/index.html) or
[ROCm/HIP](https://www.amd.com/en/products/software/rocm.html)).

It is available both as a headers-only CUDA/HIP C++ library and as a Python
package.

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Install Harmonize
:link: installation
:link-type: doc
Set up the GPU toolkit and the Python package.
:::

:::{grid-item-card} Examples
:link: https://github.com/harmonize-software/harmonize/tree/main/examples
Example programs on GitHub.
:::


::::

## Our approach

### Why async?

[Asynchronous programming](https://doc.rust-lang.org/book/ch17-00-async-await.html)
represents a **looser contract between program and execution environment.**
Once a function is called, there is no guarantee of where or when that call is
actually evaluated. If the call is lazy, then the evaluation may not happen at
all.

This looser contract is useful, because it **allows an interface to represent
a wide variety of execution strategies** (such as reorganizing processing
order to run tasks more efficiently on a GPU) without breaking any promises.
By representing all program types as different asynchronous runtimes, they can
be used interchangeably as long as they fulfill the few promises made by the
runtime's interface.

### Harmonize fundamentals

The Harmonize workflow requires a two-step approach to running code:

1. **Define a program *specification*.** A program specification *specifies
   in advance* a collection of asynchronous functions that you'll need to
   execute within some program runtime. These functions contain the logic
   that needs to be accomplished on the GPU.

   Program specifications only reference runtime systems abstractly, so that
   execution can later be tuned for greater performance on specific
   environments.

2. **Use Harmonize to transform your *specification* into a program
   *specialization*.** Harmonize contains C++ templates (called *program
   types*) which automatically convert your program specifications into
   specialized versions for the environment you are actually going to run
   your code on.

```{mermaid}
flowchart LR
    A["<b>Program specification</b><br/>async functions you want to call;<br/>refers to runtimes abstractly"]
    B["<b>Program specialization</b><br/>what and when to execute<br/>for a specific environment"]
    A -->|"program types<br/>(provided by Harmonize)"| B
```

#### A note on program types

With the addition of a program type, transitioning a codebase to that program
type could be as little as a one-line change:

```diff
- using MyProgram = EventProgram<MyProgramSpec>;
+ using MyProgram = AsyncProgram<MyProgramSpec>;
```

Likewise, as long as the interface between the specification and the program
type does not change, program types may be updated without requiring changes
from application developers.

```{toctree}
:hidden:
:caption: Getting started

installation
```

