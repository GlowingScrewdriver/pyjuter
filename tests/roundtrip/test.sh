#!/bin/sh -e

{
   # Build a Jupyter notebook from the Python source tree
   cd in/
   python3 -m pyjuter p2j \
       -input main.py \
       -inline lib1=lib1.py lib2=lib2.py another_lib=another_lib.py \
       -output ../out.ipynb
   cd ..

   # Convert the notebook to a source tree
   mkdir -p out
   cd out
   python3 -m pyjuter j2p -input ../out.ipynb
   cd ..
} 2>&1

# Compare the original and new source trees
diff -r -c in out
