#!/bin/sh

# Sorry, non-POSIX folks (looking at you, Windows). It's
# just way too messy writing simple test drivers in Python.
#
# So, POSIX shell it is.

run_tests () {
    fails=""
    for entry in *; do
        if [ -d $entry ] && [ -f $entry/test.sh ]; then
            cd $entry
            # Run the test and capture its status
            if sh -e ./test.sh > log; then
                status="success"
            else
                status="failure"
                fails="$fails $entry"
            fi
            echo "$entry: $status"
            cd ..
        fi
    done

    # Report failing tests
    if [ "$fails" != "" ]; then
        echo "Failing tests: $fails"
        false
    fi
}

run_tests
