import json
import os
import tempfile
from pathlib import Path

from pytest_xray.exceptions import XrayError


class FilePublisher:
    """Atomically export a complete Xray report, preserving any existing file on failure."""

    def __init__(self, filepath: str) -> None:
        self.filepath = Path(os.path.expandvars(filepath)).expanduser().resolve()

    def publish(self, data: dict) -> str:
        temporary = None
        cleanup_detail = ''
        try:
            try:
                content = json.dumps(data, indent=2, allow_nan=False)
                self.filepath.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(
                    mode='w', encoding='utf-8', dir=self.filepath.parent, delete=False
                ) as file:
                    temporary = Path(file.name)
                    file.write(content + '\n')
                os.replace(temporary, self.filepath)
                temporary = None
            finally:
                if temporary is not None:
                    try:
                        temporary.unlink(missing_ok=True)
                    except OSError as cleanup_error:
                        cleanup_detail = f'; could not remove temporary report {temporary}: {cleanup_error}'
        except (OSError, TypeError, ValueError) as exc:
            raise XrayError(f'Cannot export Xray results to file: {exc}{cleanup_detail}') from exc
        return str(self.filepath)
