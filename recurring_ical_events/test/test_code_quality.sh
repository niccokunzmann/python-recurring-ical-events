#!/bin/sh

set -e

cd "`dirname \"$0\"`"
cd ..

EXIT=0

if grep -n -H 'print(' recurring_ical_events/*.py; then
    echo "FAIL: print should not be used in production code."
    EXIT=1
fi

cd test

if grep -n -H -E '^[^#]*(today\(|now\()' *.py; then
    echo "FAIL: now() and today() must not be used in test code."
    EXIT=2
fi

echo "exit $EXIT"
exit "$EXIT"
