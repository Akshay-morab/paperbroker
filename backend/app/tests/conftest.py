"""Point tests at a throwaway DB before anything imports the app."""

import pathlib
import tempfile
import os

_tmp = tempfile.mkdtemp(prefix="pb-test-")
os.environ.setdefault("PB_DB_PATH", str(pathlib.Path(_tmp) / "test.db"))
