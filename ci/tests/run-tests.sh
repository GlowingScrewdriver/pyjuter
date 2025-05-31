#!/bin/sh

# Sorry, non-POSIX folks (looking at you, Windows). It's
# just way too messy writing simple test drivers in Python.
#
# So, POSIX shell it is.

report () {
    [ "$2" = "0" ] \
        && status="success" \
        || status="failure"

    echo "$1: $status"
}

run_tests () {
    for entry in *; do
        if [ -d $entry ] && [ -f $entry/test.sh ]; then
            cd $entry
            sh -e ./test.sh > log
            report $entry $?
            cd ..
        fi
    done
}

run_tests
