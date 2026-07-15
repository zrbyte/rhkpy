"""Regenerate the golden-master snapshots in tests/golden/.

Run from the repo root (in an environment with rhkpy's dependencies):

	python tests/make_golden.py

This must ONLY be run when the current behavior of rhkpy is known to be
correct (e.g. before starting a refactoring, or after an intentional,
reviewed behavior change). The characterization tests compare against these
files; regenerating them redefines what "correct" means.
"""

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # for snapshot_utils / conftest helpers
sys.path.insert(0, str(HERE.parent))   # for the local rhkpy package

from conftest import GOLDEN_DIR, VARIANT_CASES, normalize_path, sm4_fixture_paths, variant_id  # noqa: E402
from snapshot_utils import api_surface_snapshot, exception_snapshot, rhkdata_snapshot  # noqa: E402


def snapshot_load(rhkdata_cls, path, **kwargs):
	"""Load ``path`` with rhkdata(**kwargs) and snapshot the result, treating
	load failures as characterized behavior."""
	try:
		data = rhkdata_cls(str(path), **kwargs)
		return {'load': 'ok', 'data': rhkdata_snapshot(data, norm=normalize_path)}
	except Exception as exc:  # noqa: BLE001 - load failures are characterized behavior
		return {'load': 'error', 'error': exception_snapshot(exc, norm=normalize_path)}


def write_json(path, data):
	path.parent.mkdir(parents=True, exist_ok=True)
	with open(path, 'w') as f:
		json.dump(data, f, indent=1, sort_keys=True)
		f.write('\n')


def main():
	import rhkpy

	# 1. public API surface
	surface = api_surface_snapshot(rhkpy)
	write_json(GOLDEN_DIR / 'api_surface.json', surface)
	print(f'api_surface.json: {len(surface)} public names')

	# 2. per-fixture data structure snapshots
	fixtures = sm4_fixture_paths()
	if not fixtures:
		sys.exit('No .sm4 files found in test/ - cannot generate golden data.')
	for path in fixtures:
		snap = snapshot_load(rhkpy.rhkdata, path)
		out = GOLDEN_DIR / 'fixtures' / (path.stem + '.json')
		write_json(out, snap)
		print(f'{out.name}: load={snap["load"]}')

	# 3. non-default rhkdata() argument variants
	by_name = {p.name: p for p in fixtures}
	for sm4name, kwargs in VARIANT_CASES:
		snap = snapshot_load(rhkpy.rhkdata, by_name[sm4name], **kwargs)
		out = GOLDEN_DIR / 'variants' / (variant_id(sm4name, kwargs) + '.json')
		write_json(out, snap)
		print(f'{out.name}: load={snap["load"]}')

	print(f'\nGolden snapshots written to {GOLDEN_DIR}')


if __name__ == '__main__':
	main()
