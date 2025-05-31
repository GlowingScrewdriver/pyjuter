# The Design of Pyjuter

## Rationale and Intended Usage
While Jupyter Notebooks offer some conveniences over plain
Python, they can make some aspects of project maintenance
harder; for instance, version control and packaging.

Pyjuter's main purpose is to allow conversion between _Python
source trees_ (or simply _Python sources_) and _Jupyter
Notebooks_ (or simple _Notebooks_). The envisioned user
flow is something like this:

1. An existing Python source tree is converted to a Notebook,
   using Pyjuter.
2. The Notebook is used for development, and changes may be
   made to it.
3. The Notebook is converted back to a source tree and
   merged with the original Python sources.

There are some conditions that Pyjuter tries to fulfil:

* Long code sequences in the Python sources are split into
  multiple cells in the Notebook, in step (1)
* The resulting source tree from (3) should accurately
  reflect changes made in (2). That is, if a single line
  is changed in the Notebook, only that line is changed
  in the source tree.
* Modifications to the code between conversions should
  be minimal.

The following sections detail the aspects of Pyjuter's
design that make this possible.

## Chunks
A good Jupyter Notebook will have code split into cells of
manageable size. Pyjuter achieves this effect by splitting
code into _chunks_ and using one Notebook cell for each
chunk.

The rule used to achieve this rather simple: a split
should be introduced between two top-level statements that
are split by more than 1 blank line. For instance, this
code sequence in Python source:
```python
def fn ():
    pass

FLAG = 0


def proc ():
    pass
```
would be split into two chunks: one holding `fn` and
`FLAG`, and the other holding `proc`. In a Notebook,
each of these chunks would become a code cell.

## Import Shims
In Python sources, files access each others' contents
by means of the import system. Consider the following
Python source files, both in the same directory:

_main.py_:
```python
import lib
lib.func ()
```
_lib.py_:
```python
def func ():
    print ("Pyjuter works")
```

On running `main.py`, with its parent directory as
the working directory, one would expect:
```
$ ls
main.py lib.py
$ python3 ./main.py
Pyjuter works
```

Now, we consider the issue of constructing a
Notebook from these files. Structurally, a Notebook
is a single program; the concept of a module does
not exist within Notebooks. A bit of hackery is
needed to make the above example work in a
Notebook.

To achieve this, _import shims_ are used for each
cell (here I say "shim" to mean a piece of code
that is injected into the cell's code), in addition
to one cell containing supporting code at the beginning
of the notebook. Additionally, a module name is
associated with each cell. What the shims do is to
collect the names defined by the code in a cell
and use them to populate an object, which is
then discovered and used as a module by Python's
import system.

You can see the shim definitions in
[pyjuter.shims](../src/pyjuter/shims.py). For
application (during Notebook construction) and
stripping (during Notebook loading) logic, refer
to `Chunk.from_ipynb` and `Chunk.as_nb_cell` in
[pyjuter.module](../src/pyjuter/module.py).
