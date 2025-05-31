# Tests for Pyjuter

## Overview
Each directory here that has a `test.sh` script
is treated as a test. Each `testname/test.sh` is
meant to be run with `testname` as working
directory, and does the following:
* Runs a test
* Indicates the test result in its exit status
  (0 is success)
* Writes a log to stderr

The test driver, `run-tests.sh`, runs all of the
tests and outputs a line indicating the status
of each test. It also pipes the stderr of each
`testname/test.sh` to `testname/log`.

Care has been taken to write POSIX-compliant scripts.
All non-POSIX utilities used are from the Python
ecosystem.

## Dependencies
The tests use Pyjuter and some Jupyter utilies,
enumerated in `../requirements.txt`.

## Running the tests
To run all tests,

    ./run-tests.sh

If a test `testname` failed in a run of `run-tests.sh`,
you may want to view the log:

    cat testname/log

To run a single test `testname`:

    cd testname
    ./test.sh

