"""Terminal-Bench specific environment using docker-compose.

This module provides a minimal, docker-compose based environment for
Terminal-Bench
tasks, following the official Terminal-Bench workflow.
"""

import io
import logging
import os
import subprocess
import tarfile
from pathlib import Path

import docker

logger = logging.getLogger(__name__)


class TerminalBenchEnvironment:
    """Manages docker-compose based environment for Terminal-Bench tasks.

    Follows the official Terminal-Bench flow:
    1. docker compose up --build -d
    2. Execute commands
    3. docker compose down -v (complete cleanup)
    """

    def __init__(self, instance: dict[str, str]):
        """Initialize Terminal-Bench environment.

        Args:
          instance: Task instance containing task_dir path
        """
        self.instance = instance
        self.task_id = instance["task_id"]
        self.task_dir = Path(instance["task_dir"])
        self.compose_file = self.task_dir / "docker-compose.yaml"
        self.client = docker.from_env()
        self.container = None
        self.container_name = None

        if not self.compose_file.exists():
            raise FileNotFoundError(
                f"docker-compose.yaml not found in {self.task_dir}"
            )

        # Setup container
        self._setup_container()

    def _setup_container(self):
        """Setup container using docker-compose up --build -d."""
        logger.info("Starting Terminal-Bench task: %s", self.task_dir.name)

        # Set environment variables for docker-compose
        env = os.environ.copy()
        container_name = f"tbench_{self.task_dir.name}_client"
        image_name = f"tbench_{self.task_dir.name}_client"
        env.update(
            {
                "T_BENCH_TASK_DOCKER_CLIENT_IMAGE_NAME": image_name,
                "T_BENCH_TASK_DOCKER_CLIENT_CONTAINER_NAME": container_name,
                "T_BENCH_TASK_DOCKER_NAME_PREFIX": f"tbench_{self.task_dir.name}",
                "T_BENCH_TEST_DIR": "/tests",
                "T_BENCH_CONTAINER_LOGS_PATH": "/var/log/tbench",
                "T_BENCH_TASK_LOGS_PATH": "/tmp/terminalbench-logs",
            }
        )

        try:
            # Build and start containers using docker-compose
            subprocess.run(
                ["docker", "compose", "up", "--build", "-d"],
                cwd=str(self.task_dir),
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("Containers started successfully")

            # The client container name follows the pattern from docker-compose
            self.container_name = container_name

            # Get container object
            self.container = self.client.containers.get(self.container_name)
            logger.info("Connected to container: %s", self.container.short_id)

        except subprocess.CalledProcessError as e:
            logger.error(
                "Failed to start containers: %s\nStdout: %s\nStderr: %s",
                e,
                e.stdout,
                e.stderr,
            )
            raise RuntimeError(
                f"Failed to start Terminal-Bench environment: {e}"
            ) from e
        except subprocess.TimeoutExpired as e:
            logger.error("Docker compose up timed out after 300s")
            raise RuntimeError("Container setup timed out") from e
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Unexpected error during setup: %s", e)
            raise RuntimeError("Container setup timed out") from e

    def get_working_dir(self) -> str:
        """Get the working directory of the container."""
        if not self.container:
            raise RuntimeError("Container not initialized")

        self.container.reload()
        workdir = self.container.attrs.get("Config", {}).get("WorkingDir")
        return workdir if workdir else "/app"

    def copy_to(self, src_path: str, dest_path: str):
        """Copy a file from host to container."""
        if not self.container:
            raise RuntimeError("Container not initialized")

        # Create tar archive
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            tar.add(src_path, arcname=os.path.basename(dest_path))
        tar_stream.seek(0)

        # Put into container
        self.container.put_archive(os.path.dirname(dest_path), tar_stream)

    def execute(
        self, command: str, workdir: str | None = None, demux: bool = False
    ) -> tuple[int, str | tuple[str, str]]:
        """Execute a command in the container."""
        if not self.container:
            raise RuntimeError("Container not initialized")

        try:
            # Reload to check status
            self.container.reload()
            if self.container.status != "running":
                raise RuntimeError(
                    f"Container not running (status: {self.container.status})"
                )

            result = self.container.exec_run(
                ["/bin/bash", "-l", "-c", command],
                demux=demux,
                workdir=workdir,
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
            logger.error("Docker API error: %s", e)
            return 1, f"Docker API error: {e}"
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error executing command: %s", e)
            return 1, f"Execution error: {e}"

    def close(self):
        """Cleanup using docker-compose down."""
        if not self.task_dir or not self.compose_file.exists():
            logger.debug("No compose file to cleanup")
            return

        logger.info("Cleaning up Terminal-Bench environment: %s", self.task_id)

        try:
            result = subprocess.run(
                ["docker", "compose", "down", "-v"],  # -v removes volumes too
                cwd=str(self.task_dir),
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )

            if result.returncode == 0:
                logger.debug("Docker compose cleanup successful")
            else:
                logger.warning(
                    "docker-compose down returned %d: %s",
                    result.returncode,
                    result.stderr,
                )

        except subprocess.TimeoutExpired:
            logger.error("docker-compose down timed out")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error during docker-compose cleanup: %s", e)

        self.container = None
        self.container_name = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()
