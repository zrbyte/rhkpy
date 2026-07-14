# rhkpy characterization test suite (refactor safety net)

This suite pins the **current behavior** of rhkpy so the refactor on `devel`
can be verified to be 100% backward compatible. It is meant to be run
locally, against the `.sm4` measurement files in the (gitignored) `test/`
directory at the repo root.

## Running

```bash
# from the repo root, in an environment with rhkpy's dependencies
python -m pytest

# skip the slow test that starts a headless browser (genthumbs)
python -m pytest -m "not slow"
```

## What is pinned

- `tests/test_api_surface.py` — every public name reachable as `rhkpy.<name>`,
  with function/method signatures. Any rename, removal, signature change, or
  *addition* fails the test, so API changes are always deliberate.
- `tests/test_characterization.py` — for each `.sm4` fixture: the full
  structure of the loaded `rhkdata` object (instance attributes, xarray
  dims/coords/data_vars, metadata attrs) and SHA-256 hashes of every data
  array. Files that currently fail to load are pinned to fail with the same
  exception. The `spymdata` snapshot doubles as the cross-validation target
  for the planned reimplementation of the sm4 loader in `rhkpy/io/`.
- `tests/test_smoke.py` — end-to-end runs of the public entry points
  (`qplot` for every datatype, `navigation`, `genthumbs`, `peakfit`,
  `bgsubtract`, `mapsection`, ...) checking they execute and return the
  expected kind of object.

## Golden snapshots

The reference snapshots live in `tests/golden/` and are committed. Regenerate
them **only** when current behavior is known-good (e.g. after an intentional,
reviewed behavior change):

```bash
python tests/make_golden.py
```

Note: only default `rhkdata()` constructor arguments are characterized so
far; non-default options (`repetitions`, `alternate`, `loadraw`) are not yet
pinned.
