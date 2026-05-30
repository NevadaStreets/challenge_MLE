import os

import pytest

# The provided tests load the dataset via the relative path "../data/data.csv",
# which only resolves when the working directory is a direct child of the repo
# root. `make model-test` (and `make api-test`) invoke pytest from the repo
# root, so we switch into the `tests` directory for the duration of each test so
# that the relative path points at the bundled `data/data.csv` regardless of
# where pytest was launched from.
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(autouse=True)
def _chdir_to_tests_dir():
    original_cwd = os.getcwd()
    os.chdir(TESTS_DIR)
    try:
        yield
    finally:
        os.chdir(original_cwd)
