"""Shared fixtures for the rhkpy characterization test suite.

Test data: the .sm4 files in the (gitignored) ``test/`` directory at the repo
root. The suite is meant to be run locally, where that data is present.
"""

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TESTDATA_DIR = REPO_ROOT / 'test'
GOLDEN_DIR = pathlib.Path(__file__).resolve().parent / 'golden'

# make sure the local rhkpy (repo checkout) is imported, not an installed copy
sys.path.insert(0, str(REPO_ROOT))


def normalize_path(s):
	"""Replace the machine-specific test data path with a stable placeholder,
	so snapshots are comparable across machines/checkouts."""
	return s.replace(str(TESTDATA_DIR) + '/', '<TESTDATA>/').replace(str(TESTDATA_DIR), '<TESTDATA>')


def sm4_fixture_paths():
	if not TESTDATA_DIR.is_dir():
		return []
	return sorted(TESTDATA_DIR.glob('*.sm4'))


def sm4_fixture_names():
	return [p.name for p in sm4_fixture_paths()]


@pytest.fixture(scope='session')
def loaded_fixtures():
	"""Load every .sm4 fixture once per test session.

	Returns a dict: filename -> ('ok', rhkdata instance) or ('error', exception).
	Load failures are themselves characterized behavior, not test errors.
	"""
	import rhkpy
	result = {}
	for path in sm4_fixture_paths():
		try:
			result[path.name] = ('ok', rhkpy.rhkdata(str(path)))
		except Exception as exc:  # noqa: BLE001 - failures are recorded as behavior
			result[path.name] = ('error', exc)
	return result
