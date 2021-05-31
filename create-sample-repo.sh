#!/bin/bash

set -Eueo pipefail

if ! command -v faketime > /dev/null; then
  echo "This script requires the faketime program"
  echo "See http://manpages.ubuntu.com/manpages/trusty/man1/faketime.1.html"
  exit 1
fi

# reset so we know we're starting from a clean slate
rm -rf sample-repo
mkdir sample-repo

function at {
  export GIT_COMMITTER_DATE="$1"
  export GIT_AUTHOR_DATE="$1"
}

( # cd into the sample repo in a subshell, to ensure we don't lose our working dir
  cd sample-repo
  git init

  # in an initial commit, create the following file structure:
  # foo/
  # ├─ bar.txt
  # ├─ baz.txt
  # qux/
  # ├─ quux.txt
  # ├─ garply/
  # │  ├─ waldo/
  # │  │  ├─ fred.txt
  # thud.txt

  git config --local user.name Me
  git config --local user.email me@spotify.com

  # COMMIT WITHOUT PARENTS
  at "2021-05-31 13:33:37"; git commit --allow-empty -m "Initial commit"

  # CREATE A FEW FILES
  mkdir foo
  echo "bar" > foo/bar.txt
  echo "baz" > foo/baz.txt

  mkdir -p qux/garply/waldo
  echo "quux" > qux/quux.txt
  echo "fred" > qux/garply/waldo/fred.txt

  echo "thud" > thud.txt
  git add foo qux thud.txt

  at "2021-05-31 13:37"; git commit -m "Create files"


  echo "zab" > foo/baz.txt
  git mv qux/quux.txt qux/garply/quux.txt
  git status
  git add foo

  at "2021-06-01 13:33:37"; git commit -m "Update stuff"

  git log
)
