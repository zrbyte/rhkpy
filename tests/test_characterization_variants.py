"""Golden-master characterization of non-default rhkdata() arguments.

The default-argument goldens (test_characterization.py) do not exercise the
``loadraw``, ``alternate`` and ``repetitions`` code paths. The variant cases
in ``conftest.VARIANT_CASES`` pin those too - including cases that currently
raise: whatever the behavior is today, it is the contract.
"""

import json

import pytest

from conftest import GOLDEN_DIR, TESTDATA_DIR, VARIANT_CASES, normalize_path, variant_id
from make_golden import snapshot_load
from snapshot_utils import diff_snapshots


@pytest.mark.parametrize(
	'sm4name, kwargs', VARIANT_CASES,
	ids=[variant_id(n, k) for n, k in VARIANT_CASES],
)
def test_variant_matches_golden(sm4name, kwargs):
	golden_file = GOLDEN_DIR / 'variants' / (variant_id(sm4name, kwargs) + '.json')
	if not golden_file.is_file():
		pytest.fail(f'No golden snapshot for this variant. Run: python tests/make_golden.py')
	with open(golden_file) as f:
		golden = json.load(f)

	import rhkpy
	current = snapshot_load(rhkpy.rhkdata, TESTDATA_DIR / sm4name, **kwargs)

	diffs = diff_snapshots(golden, current)
	assert not diffs, (
		f'{sm4name} with {kwargs}: behavior changed vs golden snapshot '
		f'({len(diffs)} difference(s) shown, capped at 50):\n' + '\n'.join(diffs)
	)
