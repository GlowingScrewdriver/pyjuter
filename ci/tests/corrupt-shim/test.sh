#!/bin/sh -e

do_corrupt () {
    # Mess around with shims in the files
    python3 - << SCRIPT
from mess_up_nb import *
load_nb ("safe.ipynb")

#mess_up_import_helper ()
#store_nb ("out/bad-helper.ipynb")

mess_up_shim ("pre")
store_nb ("out/bad-pre-shim.ipynb")

mess_up_shim ("post")
store_nb ("out/bad-post-shim.ipynb")
SCRIPT
}

{
    # Construct a notebook
    cd in/
    python3 -m pyjuter p2j \
        -input main.py \
        -inline lib=lib.py \
        -output ../safe.ipynb
    cd ..

    # Corrupt the notebook in a variety of ways
    mkdir -p out
    do_corrupt

    # Each of the following conversions should fail
    cd out
    for nb in bad-*.ipynb; do
        python3 -m pyjuter j2p -input $nb 2>&1 \
            | grep "shim is corrupt" \
            || fails="$fails $nb"
    done
    cd ..
} 2>&1

# Check if it worked
if [ "$fails" = "" ]; then
    true
else
    echo "The following conversion shouldn't have worked:"
    echo $fails
    false
fi
