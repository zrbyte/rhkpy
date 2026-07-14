"""Cross-validation of the built-in sm4 reader (rhkpy.io.sm4) against the
legacy vendored spym loader.

rhkpy.io.sm4 is a port of spym's sm4 reader; the vendored spym copy is kept
in the repository ONLY for these tests. Every .sm4 fixture is loaded with
both implementations and the resulting Datasets must be bit-identical
(structure, coordinates, attributes, and array contents).
"""

import numpy as np
import pytest

from conftest import normalize_path, sm4_fixture_names, sm4_fixture_paths
from snapshot_utils import dataset_snapshot, diff_snapshots


def _path(name):
	return str(dict((p.name, p) for p in sm4_fixture_paths())[name])


@pytest.mark.parametrize('sm4name', sm4_fixture_names())
def test_dataset_matches_legacy_spym(sm4name):
	import spym.io  # legacy vendored loader (repo root, not packaged)
	from rhkpy.io import load_spym

	path = _path(sm4name)
	legacy = spym.io.load(path)
	current = load_spym(path)

	assert (legacy is None) == (current is None), 'one loader failed where the other succeeded'
	if legacy is None:
		return

	diffs = diff_snapshots(
		dataset_snapshot(legacy, norm=normalize_path),
		dataset_snapshot(current, norm=normalize_path),
	)
	assert not diffs, (
		f'{sm4name}: rhkpy.io.sm4 output differs from legacy spym '
		f'({len(diffs)} difference(s) shown, capped at 50):\n' + '\n'.join(diffs)
	)


@pytest.mark.parametrize('sm4name', sm4_fixture_names()[:3])
def test_pages_match_legacy_spym(sm4name):
	"""Low-level check of the binary reader: page labels, data and attrs."""
	from spym.io import rhksm4 as legacy_rhksm4
	from rhkpy.io import sm4

	path = _path(sm4name)
	legacy = legacy_rhksm4.load(path)
	current = sm4.load(path)

	assert len(legacy._pages) == len(current._pages)
	for lp, cp in zip(legacy._pages, current._pages):
		assert lp.label == cp.label
		assert np.array_equal(lp.data, cp.data)
		assert set(lp.attrs) == set(cp.attrs)
