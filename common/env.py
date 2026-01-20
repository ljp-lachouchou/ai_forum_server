from pathlib import Path

from dotenv import load_dotenv

_ENV_LOADED = False


def load_env() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    root = Path(__file__).resolve().parents[1]
    candidate_paths = [
        root / ".env",
        root / "backend" / ".env",
    ]
    for path in candidate_paths:
        if path.exists():
            load_dotenv(dotenv_path=path, override=True)
            _ENV_LOADED = True
            return

    load_dotenv(override=True)
    _ENV_LOADED = True
