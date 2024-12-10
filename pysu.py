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


import os
import sys
import pwd
import grp

def setup_user(user_spec):
    """Switch to the specified user, group, and update groups."""
    if ":" in user_spec:
        user, group = user_spec.split(":")
    else:
        user, group = user_spec, None

    # Resolve user and group IDs
    try:
        pw = pwd.getpwnam(user) if not user.isdigit() else pwd.getpwuid(int(user))
        uid = pw.pw_uid
    except KeyError:
        sys.exit(f"Error: Invalid user '{user}'")

    gid = pw.pw_gid
    if group:
        try:
            gr = grp.getgrnam(group) if not group.isdigit() else grp.getgrgid(int(group))
            gid = gr.gr_gid
        except KeyError:
            sys.exit(f"Error: Invalid group '{group}'")

    # Set the user, group, and additional groups
    try:
        # Update supplementary groups, ensuring the group IDs are integers
        group_ids = [int(gid) for gid in pw.pw_gecos.split(',')]  # Convert groups to integers
        group_ids.append(gid)  # Add the primary group ID to the list of groups
        os.setgroups(group_ids)  # Set the group list to be integers

        # Set the primary group and UID
        os.setgid(gid)
        os.setuid(uid)

        # Set the HOME environment variable if not set
        if not os.getenv("HOME"):
            os.environ["HOME"] = pw.pw_dir

    except OSError as e:
        sys.exit(f"Error: Failed to switch to '{user_spec}': {e}")


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
