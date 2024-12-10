import subprocess
import os
import pytest
import tempfile
import shutil
import time


# Parameterize the test for different architectures or configurations
@pytest.mark.parametrize("pysu_binary, dockerfile, expected_process_count", [
    ("./pysu-amd64", "Dockerfile.test-alpine", 2),
    ("./pysu-i386", "Dockerfile.test-debian", 2),
])
def test_pysu_docker(pysu_binary, dockerfile, expected_process_count):
    """Test that the Docker container runs the pysu binary and executes successfully."""
    
    # Step 1: Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tempdir:
        # Step 2: Prepare the Dockerfile and pysu binary
        dockerfile_path = os.path.join(tempdir, "Dockerfile")
        pysu_binary_path = os.path.join(tempdir, "pysu")
        
        # Copy Dockerfile and pysu binary to the temp directory
        shutil.copy(dockerfile, dockerfile_path)
        shutil.copy(pysu_binary, pysu_binary_path)

        # Step 3: Build the Docker image using the Dockerfile and pysu binary
        image_tag = f"pysu-test-{pysu_binary.split('-')[1]}"  # Derive tag based on binary name
        build_cmd = [
            "docker", "build", "-t", image_tag, tempdir
        ]
        subprocess.run(build_cmd, check=True)

        # Step 4: Run the Docker container with the pysu binary to test its behavior
        container_name = f"pysu-test-container-{pysu_binary.split('-')[1]}"
        run_cmd = [
            "docker", "run", "-d", "--name", container_name, image_tag,
            "pysu", "root", "sleep", "1000"
        ]
        subprocess.run(run_cmd, check=True)

        # Allow the container to start and run for a moment
        time.sleep(1)

        # Check the number of processes in the container (should be only 2: header + sleep)
        top_cmd = ["docker", "top", container_name]
        top_result = subprocess.run(top_cmd, capture_output=True, text=True, check=True)
        process_count = len(top_result.stdout.strip().splitlines())
        assert process_count == expected_process_count, f"Expected {expected_process_count} processes, found {process_count}"

        # Clean up the Docker container and image after the test
        subprocess.run(["docker", "rm", "-f", container_name], check=True)
        subprocess.run(["docker", "rmi", "-f", image_tag], check=True)
        
