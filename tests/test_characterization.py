"""Golden-master characterization tests.

Each .sm4 fixture in test/ is loaded with rhkpy.rhkdata() and the resulting
object structure (instance attributes, xarray dims/coords/data_vars, metadata
attrs, and content hashes of every array) is compared against the committed
snapshot in tests/golden/fixtures/. Files that fail to load are checked to
fail with the same exception as before.

If a test fails after an INTENTIONAL behavior change, regenerate the goldens
with ``python tests/make_golden.py`` and review the diff.
"""

import json

import pytest

from conftest import GOLDEN_DIR, normalize_path, sm4_fixture_names
from snapshot_utils import diff_snapshots, exception_snapshot, rhkdata_snapshot


def _golden_path(name):
	return GOLDEN_DIR / 'fixtures' / (name.rsplit('.', 1)[0] + '.json')


@pytest.mark.parametrize('sm4name', sm4_fixture_names())
def test_fixture_matches_golden(sm4name, loaded_fixtures):
	golden_file = _golden_path(sm4name)
	if not golden_file.is_file():
		pytest.fail(f'No golden snapshot for {sm4name}. Run: python tests/make_golden.py')
	with open(golden_file) as f:
		golden = json.load(f)

	status, payload = loaded_fixtures[sm4name]
	if status == 'ok':
		current = {'load': 'ok', 'data': rhkdata_snapshot(payload, norm=normalize_path)}
	else:
		current = {'load': 'error', 'error': exception_snapshot(payload, norm=normalize_path)}

	diffs = diff_snapshots(golden, current)
	assert not diffs, (
		f'{sm4name}: behavior changed vs golden snapshot '
		f'({len(diffs)} difference(s) shown, capped at 50):\n' + '\n'.join(diffs)
	)
