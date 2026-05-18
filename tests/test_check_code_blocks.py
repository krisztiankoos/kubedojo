from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_check_code_blocks():
    module_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "quality"
        / "check_code_blocks.py"
    )
    spec = importlib.util.spec_from_file_location(
        "quality_check_code_blocks_test", module_path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


check_code_blocks = _load_check_code_blocks()


def test_check_code_blocks_missing_explicit_path_returns_nonzero(
    tmp_path: Path, capsys
) -> None:
    missing = tmp_path / "does-not-exist.md"

    result = check_code_blocks.main([str(missing)])

    captured = capsys.readouterr()
    assert result == 1
    assert f"warning: {missing.resolve()} does not exist" in captured.err
    assert "No existing files were checked." in captured.err


def test_check_code_blocks_mixed_valid_and_missing_returns_nonzero(
    tmp_path: Path, capsys
) -> None:
    valid = tmp_path / "module.md"
    missing = tmp_path / "missing.md"
    valid.write_text(
        """# Demo

```python
print("hello")
```
""",
        encoding="utf-8",
    )

    result = check_code_blocks.main([str(valid), str(missing)])

    captured = capsys.readouterr()
    assert result == 1
    assert "OK" in captured.out
    assert f"warning: {missing.resolve()} does not exist" in captured.err
    assert "1 provided path(s) were missing." in captured.err
