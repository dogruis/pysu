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
Usage: {sys.argv[0]} user-spec command [args]
   eg: {sys.argv[0]} dogruis bash
       {sys.argv[0]} nobody:root bash -c 'whoami && id'
       {sys.argv[0]} 1000:1 id

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
    try:
        if ":" in user_spec:
            user, group = user_spec.split(":")
        else:
            user = user_spec
            group = None
        
        # Lookup the user
        user_info = pwd.getpwnam(user)
        uid = user_info.pw_uid
        gid = user_info.pw_gid

        # Lookup the group if necessary
        if group:
            try:
                group_info = grp.getgrnam(group)
                gid = group_info.gr_gid
            except KeyError:
                exit_with_error(f"Group '{group}' not found")

        # Set user and group IDs
        os.setgid(gid)
        os.setuid(uid)
        
        # Set the HOME environment variable
        if 'HOME' not in os.environ:
            os.environ['HOME'] = user_info.pw_dir

    except KeyError as e:
        exit_with_error(f"User '{user}' not found")
    except OSError as e:
        exit_with_error(f"Failed to set user: {e}")


def main():
    if len(sys.argv) < 3:
        print(usage())
        sys.exit(1)

    # Handle help and version flags
    if sys.argv[1] in ['--help', '-h', '-?']:
        print(usage())
        sys.exit(0)

    if sys.argv[1] in ['--version', '-v']:
        print(version())
        sys.exit(0)

    user_spec = sys.argv[1]
    command = sys.argv[2:]

    # Setup user (switch to the requested user)
    setup_user(user_spec)

    # Execute the given command as the new user
    try:
        # Use execvp to run the command, passing the arguments
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        exit_with_error(f"Command failed: {e}")
    except FileNotFoundError:
        exit_with_error(f"Command '{command[0]}' not found")
    except Exception as e:
        exit_with_error(f"Error executing command: {e}")

if __name__ == "__main__":
    main()
