#!/bin/sh -e

{
    # Construct a notebook
    cd in/
    python3 -m pyjuter p2j \
        -input main.py \
        -inline lib=lib.py \
        -output ../out.ipynb
    cd ..

    # Execute the notebook
    jupyter-execute out.ipynb --output out_exec.ipynb
} 2>&1

# Check if it worked
grep -n "It works" out_exec.ipynb
