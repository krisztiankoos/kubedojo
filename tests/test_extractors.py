from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.quality.extractors import extract_module_markdown


def test_extract_module_markdown_unwraps_prose_prefixed_fenced_module() -> None:
    result = extract_module_markdown(
        """Here is the rewritten module:

```markdown
---
title: Demo
---

Body.
```
"""
    )

    assert result.unwrapped_code_fence is True
    assert result.text == "---\ntitle: Demo\n---\n\nBody.\n"
