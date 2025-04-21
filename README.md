# Pyjuter
Convert between Python and Jupyter Notebooks with ease

For detailed reference documentation, see the
[generated API docs](https://glowingscrewdriver.github.io/pyjuter)

## Example usage:
This example

1. Loads a python file (ensure that you have [`conversion.py`](pyjuter/conversion.py)
   in your current directory).
2. Converts it to a Jupyter Notebook (and saves it to
   `out.ipynb`)
3. Loads the resulting Jupyter Notebook.
4. Converts the notebook back to Python source (and saves it
   to `out.py`)
5. Compares the resulting Python code with the original, _byte for byte_.

```python
from pyjuter.conversion import Module

## Test it on pyjuter's source itself by taking
## a Python file on a round trip to Jupyter and back

# Load a Python script
with open ("conversion.py") as f:
    py_src_1 = f.read ()
module_1 = Module.from_py (py_src_1)

# Convert it to a Jupyter Notebook and save it
ipynb_src = module_1.to_ipynb ()
with open ("out.ipynb", "w") as f:
    f.write (ipynb_src)

# Load the Jupyter Notebook
module_2 = Module.from_ipynb (ipynb_src)

# Save it as a Python script
py_src_2 = module_2.to_py ()
with open ("out.py", "w") as f:
    f.write (py_src_2)

print ("Test result: f{py_src_1 == py_src_2}")
```

## Caveats
* Support only for code cells -- no output, Markdown, etc.
