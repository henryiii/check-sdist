#!/usr/bin/env python3

# /// script
# dependencies = ["pyyaml"]
# ///
from __future__ import annotations

import json

import yaml

starter = """
$schema: http://json-schema.org/draft-07/schema#
$id: https://json.schemastore.org/partial-check-sdist.json
additionalProperties: false
description: check-sdist's settings.
type: object
properties:
  sdist-only:
    description: Files that only are in the SDist. Gitignore style lines.
    type: array
    items:
      type: string
  git-only:
    description: Files that are only in Git (or whatever mode you use). Gitignore style lines.
    type: array
    items:
      type: string
  default-ignore:
    description: Ignore some common files
    default: true
    type: boolean
  recurse-submodules:
    description: Look in all submodules too.
    default: true
    type: boolean
  mode:
    description: What to use as baseline
    default: git
    enum:
      - git
      - all
  build-backend:
    description: What to expect as build-backend, in order to look for exclude lists
    default: auto
    enum:
      - auto
      - none
      - flit_core.buildapi
      - hatchling.build
      - scikit_build_core.build
      - pdm.backend.api
      - poetry.core.masonry.api
      - maturin
"""

schema = yaml.safe_load(starter)
print(json.dumps(schema, indent=2))
