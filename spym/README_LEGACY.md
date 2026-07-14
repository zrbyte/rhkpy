# Legacy vendored spym — testing only

This is a vendored copy of the [spym project](https://github.com/rescipy-project/spym)
(MIT license, Mirco Panighel). **rhkpy no longer uses it at runtime**: the sm4
reader was ported to `rhkpy/io/sm4.py` (refactor phase 4).

This copy is kept in the repository solely as the reference implementation for
the cross-validation tests in `tests/test_sm4_loader.py`, which verify that
`rhkpy.io.sm4` produces bit-identical output. It is deliberately excluded from
packaging (see `pyproject.toml`) and must not be imported from `rhkpy/`.
