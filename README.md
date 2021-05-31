# Raw Dump Sample Generator

In order to make it easier to understand and explain the input format for the raw git crawler, we
want to build a sample repository with some representative sample actions in the log, and a corresponding
set of dump files.

There is an [RFC for the format](https://docs.google.com/document/d/1ltvyC14Kt4-_iWGqv1Bpc5PWQAWFynAY7n6cLqGxHJE/edit#) which showcases the simpler cases. For a fuller description, run the scripts in this repo to generate the sample repository and its dump file.

## Setting up your environment

The Python script depends on some Python packages, which can be installed with `pip`:

```
pip install -r requirements.txt
```

(The requirements file also installs some developer tooling, like `black` and `flake8`.)

## Running the scripts

Couldn't be simpler:

```
./create-sample-repo.sh
./create-dump.py
```
