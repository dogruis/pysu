import subprocess
import pytest

@pytest.mark.parametrize("uid, gid, command, expected_output", [
    (1000, 1000, ["id", "-u"], "1000"),
    (1000, 1000, ["id", "-g"], "1000"),
    (1000, 1000, ["id", "-un"], "nobody"),  # Example for user
    (1000, 1000, ["id", "-gn"], "nogroup"),  # Example for group
])
def test_pysu_as_non_root(uid, gid, command, expected_output):
    """Test the pysu script with different UIDs and GIDs."""
    result = subprocess.run(
        ["python3", "/app/pygosu.py", str(uid), str(gid)] + command,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == expected_output
    assert result.returncode == 0
