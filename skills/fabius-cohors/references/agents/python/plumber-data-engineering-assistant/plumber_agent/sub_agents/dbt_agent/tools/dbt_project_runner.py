"""
This module provides functionality to run dbt projects locally using
subprocess calls to the dbt CLI.
"""

import logging
import subprocess

logger = logging.getLogger("plumber-agent")


def run_dbt_project(dbt_project_path: str) -> dict[str, str | int | None]:
    """
    Runs dbt commands to debug and execute a dbt project located at the specified path.

    This function performs the following steps:
      - Runs `dbt debug` to check the project and profile configuration.
      - Runs `dbt run` to execute the dbt models.
      - Captures and returns the result, including status, return code, and output logs.

    Args:
        dbt_project_path (str): Local filesystem path to the root directory of
          the dbt project. This directory should contain both the
          `dbt_project.yml` and profiles.

    Returns:
        dict: A dictionary containing:
            - "status" (str): "success" if `dbt run` completes successfully,
                              "error" if a CalledProcessError is raised,
                              or "failure" for any other exception.
            - "return_code" (int or None): The return code of the `dbt run` process,
                                          or None if an unexpected error occurred.
            - "output" (str): The standard output from `dbt run` if successful,
                              or standard error if an error occurred,
                              or the exception message on failure.
    """
    try:
        subprocess.run(
            [
                "dbt",
                "debug",
                "--project-dir",
                dbt_project_path,
                "--profiles-dir",
                dbt_project_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        dbt_run_status = subprocess.run(
            [
                "dbt",
                "run",
                "--project-dir",
                dbt_project_path,
                "--profiles-dir",
                dbt_project_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        return {
            "status": "success",
            "return_code": dbt_run_status.returncode,
            "output": dbt_run_status.stdout,
        }
    except subprocess.CalledProcessError as cmd_err:
        logger.error("An error occurred: %s", cmd_err, exc_info=True)
        return {
            "status": "error",
            "return_code": cmd_err.returncode,
            "output": cmd_err.stderr,
        }
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred: %s", err, exc_info=True)
        return {"status": "failure", "return_code": None, "output": str(err)}
