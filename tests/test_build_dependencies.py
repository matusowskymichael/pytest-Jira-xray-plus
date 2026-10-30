"""Build setup must follow the manifest without executing shell syntax or hiding failure."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'install_build_dependencies.py'
SPEC = importlib.util.spec_from_file_location('install_build_dependencies', SCRIPT)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


def test_manifest_update_and_markers_are_forwarded_as_single_arguments(tmp_path):
    (tmp_path / 'pyproject.toml').write_text(
        '[build-system]\nrequires = ["setuptools==99.0.0", "wheel; python_version >= \'3.12\'"]\n'
    )
    with patch.object(installer.subprocess, 'run') as run:
        installer.install(tmp_path)
    run.assert_called_once_with(
        [sys.executable, '-m', 'pip', 'install', '--', 'setuptools==99.0.0', "wheel; python_version >= '3.12'"],
        check=True,
    )


@pytest.mark.parametrize('value', ['"setuptools"', '[]', '[1]', '[""]', '[" "]'])
def test_invalid_requirements_fail_before_install(tmp_path, value):
    (tmp_path / 'pyproject.toml').write_text(f'[build-system]\nrequires = {value}\n')
    with patch.object(installer.subprocess, 'run') as run, pytest.raises(ValueError):
        installer.install(tmp_path)
    run.assert_not_called()


def test_pip_failure_propagates(tmp_path):
    (tmp_path / 'pyproject.toml').write_text('[build-system]\nrequires = ["setuptools==99.0.0"]\n')
    with (
        patch.object(installer.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'pip')),
        pytest.raises(subprocess.CalledProcessError),
    ):
        installer.install(tmp_path)


def test_cli_locates_manifest_from_another_directory(tmp_path):
    # The fake pip runs in a child process; no package index or environment mutation.
    (tmp_path / 'pip.py').write_text('import sys\nprint(repr(sys.argv[1:]))\n')
    import os

    result = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=tmp_path,
        env=dict(os.environ, PYTHONPATH=str(tmp_path)), capture_output=True, text=True, check=True,
    )
    import tomllib

    requirements = tomllib.loads((SCRIPT.parents[1] / 'pyproject.toml').read_text())['build-system']['requires']
    assert repr(['install', '--', *requirements]) in result.stdout
