"""Install this checkout's declared build requirements in the active Python environment."""

import subprocess
import sys
from pathlib import Path

import tomllib


def install(root):
    with (root / 'pyproject.toml').open('rb') as stream:
        requirements = tomllib.load(stream)['build-system']['requires']
    if not isinstance(requirements, list) or not requirements or any(
        not isinstance(value, str) or not value.strip() for value in requirements
    ):
        raise ValueError('build-system.requires must be a nonempty list of requirement strings')
    # Pass each requirement as one argument, including markers; never use a shell.
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--', *requirements], check=True)


if __name__ == '__main__':
    install(Path(__file__).resolve().parents[1])
