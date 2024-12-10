#!/usr/bin/env python3

import os
import sys
import stat
import pwd
import grp
import subprocess
import platform


def version():
    """Return version information including Python, OS, and system architecture."""
    python_version = sys.version.split()[0]
    os_name = os.name
    system_architecture = platform.machine()

    return f"Python {python_version} on {os_name} ({system_architecture})"


def usage():
    """Return usage information."""
    return f"""
Usage: pysu.py user-spec command [args]
   eg: pysu.py dogruis bash
       pysu.py nobody:root bash -c 'whoami && id'
       pysu.py 1000:1 id

pysu version: {version()}
pysu license: MIT (full text at https://github.com/dogruis/pysu)
"""


def validate_binary():
    """Ensure the script is not setuid or setgid."""
    st = os.stat(__file__)
    if st.st_mode & (stat.S_ISUID | stat.S_ISGID):
        sys.exit(
            f"Error: {sys.argv[0]} appears to be installed with the 'setuid' or 'setgid' bit set, "
            "which is insecure and unsupported. Use 'sudo' or 'su' instead."
        )


def setup_user(user_spec):
    """
    Changes the groups, gid, and uid for the specified user.

    Parameters:
    - user_spec: str : The user specification (username or UID).
    """

    # Get the current UID and GID as defaults
    default_uid = os.getuid()
    default_gid = os.getgid()
    default_home = "/"

    # Resolve the user information
    try:
        if user_spec.isdigit():
            user_info = pwd.getpwuid(int(user_spec))
        else:
            user_info = pwd.getpwnam(user_spec)
    except KeyError:
        # If user is not found, use the defaults
        user_info = type('', (), {
            'pw_uid': default_uid,
            'pw_gid': default_gid,
            'pw_dir': default_home
        })()

    # Get supplementary group IDs
    try:
        group_ids = [g.gr_gid for g in grp.getgrall() if user_info.pw_name in g.gr_mem]
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve group information: {e}")

    print("Group IDs to set:", group_ids)
    # Change groups
    try:
        os.setgroups(group_ids)
    except PermissionError as e:
        raise RuntimeError(f"Failed to set groups: {e}")

    # Change GID
    try:
        os.setgid(user_info.pw_gid)
    except PermissionError as e:
        raise RuntimeError(f"Failed to set GID: {e}")

    # Change UID
    try:
        os.setuid(user_info.pw_uid)
    except PermissionError as e:
        raise RuntimeError(f"Failed to set UID: {e}")

    # Set HOME environment variable if not already set
    if not os.getenv("HOME"):
        os.environ["HOME"] = user_info.pw_dir


def main():
    validate_binary()

    # Parse arguments
    if len(sys.argv) < 3:
        sys.exit(usage())

    user_spec = sys.argv[1]
    command = sys.argv[2:]

    setup_user(user_spec)

    # Execute the given command
    try:
        subprocess.run(command)
    except FileNotFoundError:
        sys.exit(f"Error: Command not found: {command[0]}")
    except Exception as e:
        sys.exit(f"Error: Failed to execute '{command[0]}': {e}")


if __name__ == "__main__":
    main()
