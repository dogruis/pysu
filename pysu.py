import pwd
import sys
import os
import subprocess
import runtime

VERSION = "1.0.0"  # Define the version of the script

def get_user_info(user_spec):
    """
    Get user information from user specifier. Accepts both user names
    and numeric user IDs (UIDs).
    """
    try:
        if user_spec.isdigit():
            # If user_spec is numeric (UID), look up by UID
            uid = int(user_spec)
            user_info = pwd.getpwuid(uid)
        else:
            # Otherwise, look up by username
            user_info = pwd.getpwnam(user_spec)
        return user_info
    except KeyError:
        print(f"User '{user_spec}' not found")
        sys.exit(1)

def run_command(command):
    """
    Run a command with subprocess and return the output.
    """
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode(), result.stderr.decode()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def version():
    """
    Returns the version of the script.
    """
    return f"pysu version {VERSION} (Python {sys.version_info[0]}.{sys.version_info[1]})"

def usage():
    """
    Returns the usage string for the script.
    """
    self = os.path.basename(sys.argv[0])
    return f"""
Usage: {self} user-spec command [args]
   eg: {self} tianon bash
       {self} nobody:root bash -c 'whoami && id'
       {self} 1000:1 id

{self} version: {version()}
{self} license: Apache-2.0 (full text at https://github.com/tianon/gosu)
"""

def exit_with_message(code, message):
    """
    Print the message to stderr and exit with the given exit code.
    """
    sys.stderr.write(message + '\n')
    sys.exit(code)

def main():
    # Check for --help, -h, --version, -v flags
    if len(sys.argv) < 2:
        print(usage())
        sys.exit(1)

    if sys.argv[1] in ['--help', '-h', '-?']:
        print(usage())
        sys.exit(0)

    if sys.argv[1] in ['--version', '-v']:
        print(version())
        sys.exit(0)

    # Get the user specifier (e.g., "0" or "root")
    user_spec = sys.argv[1]
    
    # Fetch user information (either by username or UID)
    user_info = get_user_info(user_spec)
    user_name = user_info.pw_name
    user_uid = user_info.pw_uid
    user_gid = user_info.pw_gid
    user_home = user_info.pw_dir

    print(f"User Info: {user_name} (UID: {user_uid}, GID: {user_gid}, Home: {user_home})")
    
    # Set environment variables as needed
    os.setgid(user_gid)
    os.setuid(user_uid)
    os.environ['HOME'] = user_home

    # After switching user, execute the command passed as argument
    command = sys.argv[2:]  # All arguments after the user specifier are the command to execute
    if not command:
        print("No command provided to execute.")
        sys.exit(1)

    # Execute the user command with the updated UID/GID
    stdout, stderr = run_command(command)
    if stdout:
        print(f"Output: {stdout}")
    if stderr:
        print(f"Error: {stderr}")

if __name__ == "__main__":
    main()
