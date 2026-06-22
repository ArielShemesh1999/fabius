"""SWE-bench specific environment using Docker.

This module defines the `SWEBenchEnvironment` class, which manages a Docker
container for executing commands within a SWE-bench environment.
"""

import io
import logging
import os
import tarfile
import time

import docker

logger = logging.getLogger(__name__)


def get_swebench_image_name(instance: dict[str, str]) -> str:
    """Get the SWE-bench Docker image name for a benchmark instance.

    Args:
      instance: The instance dictionary containing task information

    Returns:
      The Docker image name to use
    """
    iid = instance["instance_id"]
    id_docker_compatible = iid.replace("__", "_1776_")
    return f"docker.io/swebench/sweb.eval.x86_64.{id_docker_compatible}:latest".lower()


class SWEBenchEnvironment:
    """Manages a Docker container for executing commands within a SWE-bench environment.

    This class handles pulling the necessary Docker image, starting and stopping
    a container, and executing commands within that container.
    """

    def __init__(
        self,
        instance: dict[str, str],
        pull_timeout: int = 300,
        start_timeout: int = 60,
    ):
        self.client = docker.from_env()
        self.instance = instance
        self.image_name = get_swebench_image_name(instance)
        self.container = None
        self.pull_timeout = pull_timeout
        self.start_timeout = start_timeout

        self._setup_container()

    def _setup_container(self):
        """Setup Docker container with proper error handling."""
        try:
            # Pull image with timeout for SWE-bench
            logger.info("Pulling Docker image: %s", self.image_name)
            start_time = time.time()

            try:
                self.client.images.pull(self.image_name)
                pull_time = time.time() - start_time
                logger.info("Image pulled in %.2fs", pull_time)
            except docker.errors.APIError as e:
                logger.warning(
                    "Failed to pull image %s: %s. Assuming local image.",
                    self.image_name,
                    e,
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Unexpected error pulling image: %s", e)
                raise

            # Start container with resource limits
            logger.info("Starting container...")
            start_time = time.time()

            self.container = self.client.containers.run(
                self.image_name,
                detach=True,
                tty=True,
                command="tail -f /dev/null",
                mem_limit="4g",  # Memory limit
                memswap_limit="4g",  # Disable swap
                remove=False,  # Don't auto-remove so we can debug if needed
            )

            # Give container a moment to initialize
            time.sleep(2)

            start_time_elapsed = time.time() - start_time
            logger.info(
                "Container started in %.2fs: %s",
                start_time_elapsed,
                self.container.short_id,
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to setup container for %s: %s",
                self.instance.get("instance_id", "unknown"),
                e,
            )
            self._cleanup_failed_container()
            raise

    def _cleanup_failed_container(self):
        """Clean up container if setup failed."""
        if self.container:
            try:
                self.container.stop(timeout=10)
                self.container.remove()
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to cleanup failed container: %s", e)

    def copy_to(self, src_path: str, dest_path: str):
        """Copy a file from the host to a destination in the container."""
        if not self.container:
            raise RuntimeError("Container not initialized")

        # Create a tar archive in memory
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            tar.add(src_path, arcname=os.path.basename(dest_path))
        tar_stream.seek(0)

        # Put the archive into the container
        self.container.put_archive(os.path.dirname(dest_path), tar_stream)

    def execute(
        self, command: str, demux: bool = False
    ) -> tuple[int, str | tuple[str, str]]:
        """Execute a command in the container with timeout and error handling.

        Args:
        command: The command to execute.
        demux: If True, returns (exit_code, (stdout, stderr)). If False, returns
            (exit_code, combined_output).

        Returns:
        A tuple of (exit_code, output).
        """
        if not self.container:
            raise RuntimeError("Container not initialized")

        try:
            # Check if container is still running
            self.container.reload()
            if self.container.status != "running":
                raise RuntimeError(
                    f"Container is not running (status: {self.container.status})"
                )

            result = self.container.exec_run(
                ["/bin/bash", "-l", "-c", command], demux=demux
            )

            exit_code = result.exit_code
            if demux:
                stdout = result.output[0]
                stderr = result.output[1]
                if stdout is not None:
                    stdout = stdout.decode("utf-8", errors="replace")
                else:
                    stdout = ""
                if stderr is not None:
                    stderr = stderr.decode("utf-8", errors="replace")
                else:
                    stderr = ""
                output = (stdout, stderr)
            else:
                output = result.output.decode("utf-8", errors="replace")

            return exit_code, output

        except docker.errors.APIError as e:
            logger.error("Docker API error executing command: %s", e)
            return 1, f"Docker API error: {e}"
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error executing command '%.50s...': %s", command, e)
            return 1, f"Execution error: {e}"

    def close(self):
        """Stop and remove the container with proper cleanup."""
        if not self.container:
            logger.debug("No container to close")
            return

        container_id = self.container.short_id
        logger.info("Stopping container %s...", container_id)

        try:
            # Try graceful stop first
            self.container.stop(timeout=30)
            logger.debug("Container %s stopped gracefully", container_id)
        except docker.errors.APIError as e:
            logger.warning("Failed to stop container gracefully: %s", e)
            try:
                # Force kill if graceful stop failed
                self.container.kill()
                logger.debug("Container %s force killed", container_id)
            except Exception as kill_e:  # pylint: disable=broad-exception-caught
                logger.error("Failed to kill container: %s", kill_e)

        try:
            # Remove container
            self.container.remove()
            logger.debug("Container %s removed", container_id)
        except docker.errors.APIError as e:
            logger.warning("Failed to remove container %s: %s", container_id, e)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Unexpected error removing container: %s", e)

        self.container = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()
