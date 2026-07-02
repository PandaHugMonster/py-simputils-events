#!/usr/bin/env just --justfile
export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')

update:
    uv sync

upgrade:
    uv sync --upgrade

check:
    uv run pytest