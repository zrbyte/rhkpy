"""Public API surface pinning.

Compares every public name exported by ``import rhkpy`` (functions, classes
and their method signatures, re-exported modules) against the committed
snapshot. Any rename, removal, or signature change of the public API breaks
this test - which is the point: the refactor must be 100% backward compatible.

Additions of NEW public names also fail here; that is intentional, so that
extending the API is always a deliberate, reviewed act (regenerate goldens
with ``python tests/make_golden.py``).
"""

import json

from conftest import GOLDEN_DIR
from snapshot_utils import api_surface_snapshot, diff_snapshots


def test_api_surface_matches_golden():
	golden_file = GOLDEN_DIR / 'api_surface.json'
	assert golden_file.is_file(), 'No golden API snapshot. Run: python tests/make_golden.py'
	with open(golden_file) as f:
		golden = json.load(f)

	import rhkpy
	current = api_surface_snapshot(rhkpy)

	diffs = diff_snapshots(golden, current)
	assert not diffs, (
		f'Public API surface changed ({len(diffs)} difference(s) shown, capped at 50):\n'
		+ '\n'.join(diffs)
	)
