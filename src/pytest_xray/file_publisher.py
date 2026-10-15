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
        try:
            content = json.dumps(data, indent=2, allow_nan=False)
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=self.filepath.parent, delete=False
            ) as file:
                temporary = Path(file.name)
                file.write(content + '\n')
            os.replace(temporary, self.filepath)
        except (OSError, TypeError, ValueError) as exc:
            raise XrayError(f'Cannot export Xray results to file: {exc}') from exc
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return str(self.filepath)
