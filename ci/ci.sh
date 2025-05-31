#!/bin/sh

### Automation of Continous Integration tasks ###
# This script is an effort to keep Pyjuter's CI 
# independent of the CI platform. That enables the CI
# to be run anywhere -- local development machines,
# alternative repository hosts, etc.

_activate () {
    # Activate the virtual environment for CI
    . venv/bin/activate
}

setup () {
    # Set up a virtual environment for CI
    python3 -m venv venv
    venv/bin/pip install -r requirements.txt
}

tests () {
    # Pyjuter's test suite
    cd tests
    ./run-tests.sh
}

typecheck () {
    # Static type-checking
    mypy
}

docs () {
    mkdir -p site
    cd site

    # Generate API docs
    pdoc pyjuter -o api-docs
}

case "$1" in
setup)
    # Tasks that don't need the venv
    set -x
    $1
    set +x
    ;;
tests|typecheck|docs)
    # Tasks that need the venv
    _activate
    set -x
    $1
    set +x
    ;;
"")
    echo "Please specify a task name"
    false
    ;;
*)
    echo "Invalid task: ${1}"
    false
    ;;
esac
