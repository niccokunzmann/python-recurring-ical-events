#!/bin/bash
#
# Srcipt to clean up branches that are no longer in use.
#
# Due to gitlab mirroring back and forth, the branches are not
# being deleted but put back in place again.
#

set -e

cd "`dirname \"$0\"`"

remotes=""
branches=""

for remote in `git remote`; do
    echo -n "Choose branches from remote $remote? (Y/n) "
    read
    if [ -z "$REPLY" ] || [ "$REPLY" == "y" ] || [ "$REPLY" == "Y" ]; then
        echo "Using remote $remote."
        remotes="$remotes $remote"
    fi
done

for branch in `git branch -r | grep -oE '[^/]+$' | sort | uniq | grep -vE 'master'`; do
    echo -n "Delete branch $branch? (y/N) "
    read
    if [ "$REPLY" == "y" ] || [ "$REPLY" == "Y" ]; then
        echo "Remembering $branch for deletion."
        branches="$branches $branch"
    else
        echo "Keeping $branch."
    fi
done

echo "Selected remotes to delete branches from: $remotes."
echo "Selected branches to delete: $branches"
echo -n "Start deleting? (Control+C to stop) "
read

for branch in $branches; do
    echo " ---------- deleting $branch ---------- "
    git branch -d "$branch" || true
    for remote in $remotes; do
        git push --delete "$remote" "$branch" || true
    done
done
