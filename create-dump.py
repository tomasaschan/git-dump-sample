#!/bin/env python

import datetime
import json
import sys

import dateutil.parser
from pygit2 import (
    Repository,
    GIT_DIFF_REVERSE,
    GIT_DELTA_ADDED,
    GIT_DELTA_DELETED,
    GIT_DELTA_MODIFIED,
    GIT_DELTA_RENAMED,
)

sample_repo = Repository("./sample-repo/.git")

emitted_objects = set()
blobs_to_emit = set()


def name_email(signature):
    return f"{signature.name} <{signature.email}>"


def timestamp(unix_time, offset):
    return datetime.datetime.fromtimestamp(
        unix_time, tz=datetime.timezone(datetime.timedelta(minutes=offset))
    )


def signature_timestamp(signature):
    return (
        timestamp(signature.time, signature.offset).isoformat().replace("+00:00", "Z")
    )


def blob(b):
    if b.id in emitted_objects or b.id not in blobs_to_emit:
        return

    emitted_objects.add(b.id)

    yield f"blob {b.id} {json.dumps(b.data.decode('utf-8'))}"


def tree(t):
    if t.id in emitted_objects:
        return

    emitted_objects.add(t.id)
    for item in t:
        yield f"tree {t.id} {item.type_str} {item.id}"

        if item.type_str == "tree":
            yield from tree(item)

        if item.type_str == "blob":
            yield from blob(item)


def diff(commit):
    diff = (
        commit.tree.diff_to_tree(commit.parents[0].tree, GIT_DIFF_REVERSE)
        if commit.parents
        else commit.tree.diff_to_tree(flags=GIT_DIFF_REVERSE)
    )

    diff.find_similar()

    for patch in diff:
        if patch.delta.status == GIT_DELTA_ADDED:
            yield f"commit {commit.id} filecreate {patch.delta.new_file.path} {patch.delta.new_file.id}"
            blobs_to_emit.add(patch.delta.new_file.id)
        elif patch.delta.status == GIT_DELTA_DELETED:
            yield f"commit {commit.id} fileremove {patch.delta.old_file.path}"
        elif patch.delta.status == GIT_DELTA_MODIFIED:
            yield f"commit {commit.id} filemodify {patch.delta.new_file.path} {patch.delta.new_file.id}"
            blobs_to_emit.add(patch.delta.new_file.id)
        elif patch.delta.status == GIT_DELTA_RENAMED:
            yield f"commit {commit.id} filerename {patch.delta.old_file.path} {patch.delta.new_file.path} {patch.delta.new_file.id}"
            if patch.delta.old_file.id != patch.delta.new_file.id:
                blobs_to_emit.add(patch.delta.new_file.id)
        else:
            raise NotImplementedError(f"unsupported delta status: {patch.delta.status}")


def commit(commit):
    def _commit():
        if commit.id in emitted_objects:
            return

        emitted_objects.add(commit.id)

        yield f'commit {commit.id} author "{name_email(commit.author)}" {signature_timestamp(commit.author)}'
        yield f'commit {commit.id} committer "{name_email(commit.committer)}" {signature_timestamp(commit.committer)}'
        yield f"commit {commit.id} message {json.dumps(commit.message.strip())}"
        yield f"commit {commit.id} {' '.join(('parents', *(str(id) for id in commit.parent_ids)))}"
        yield f"commit {commit.id} tree {commit.tree_id}"

        yield from diff(commit)

        yield from tree(commit.tree)

    return sorted(_commit())


def dump(since=None):
    for c in sample_repo.walk(sample_repo.head.target):
        if since and since <= datetime.datetime.fromtimestamp(c.commit_time):
            for line in commit(c):
                print(line)


if __name__ == "__main__":
    since = None
    if sys.argv[1:]:
        since = dateutil.parser.parse(sys.argv[1])

    dump(since)
