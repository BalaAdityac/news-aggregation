from __future__ import annotations

from pathlib import Path


_BACKEND_APP_PATH = Path(__file__).resolve().parent.parent / "Backend" / "app"

# Allow `import app.*` to resolve to the backend package from the repo root.
__path__ = [str(_BACKEND_APP_PATH)]
