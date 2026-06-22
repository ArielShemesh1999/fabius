"""Main script for running and evaluating benchmark instances using a Docker environment.

This script provides commands to run benchmark evaluations (SWE-bench and
Terminal-Bench),
with robust progress tracking and parallel processing capabilities.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import typer
import yaml
from datasets import load_dataset
from swebench.harness import run_evaluation

from .orchestrator import Orchestrator
from .swebench_environment import SWEBenchEnvironment
from .terminalbench_environment import TerminalBenchEnvironment

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = typer.Typer()


def clone_terminalbench_repo() -> Path:
    """Clone Terminal-Bench repo and checkout to specific commit.

    Returns:
      Path to the cloned repository
    """
    repo_dir = Path.home() / ".cache" / "terminal-bench-repo"
    target_commit = "91e10457b5410f16c44364da1a34cb6de8c488a5"

    if repo_dir.exists():
        logger.info(
            "Terminal-Bench repo exists, checking out to %s", target_commit
        )
        subprocess.run(
            ["git", "-C", str(repo_dir), "checkout", target_commit],
            check=True,
            capture_output=True,
        )
    else:
        logger.info("Cloning Terminal-Bench repository...")
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "git",
                "clone",
                "https://github.com/laude-institute/terminal-bench.git",
                str(repo_dir),
            ],
            check=True,
            capture_output=True,
        )
        logger.info("Checking out to commit %s", target_commit)
        subprocess.run(
            ["git", "-C", str(repo_dir), "checkout", target_commit],
            check=True,
            capture_output=True,
        )

    logger.info("Terminal-Bench repository ready at %s", repo_dir)
    return repo_dir


def load_terminalbench_tasks(
    task_ids: list[str] | None = None, n_tasks: int | None = None
) -> list[dict[str, Any]]:
    """Load Terminal-Bench tasks from cloned repository.

    Args:
      task_ids: Optional list of specific task IDs to load
      n_tasks: Optional number of tasks to load (applied after filtering to core)

    Returns:
      List of task dictionaries
    """
    # Clone/update repo
    repo_dir = clone_terminalbench_repo()
    tasks_dir = repo_dir / "tasks"

    # Load core task IDs from the core-v0 dataset
    core_dataset_path = repo_dir / "datasets" / "terminal-bench-core-v0.yaml"
    with open(core_dataset_path, encoding="utf-8") as f:
        core_config = yaml.safe_load(f)
    core_task_ids = set(core_config.get("task_ids", []))
    logger.info("Core dataset contains %d task IDs", len(core_task_ids))

    # Map task IDs to directories (handle .base suffix)
    task_id_to_dir = {}

    for tid in core_task_ids:
        if tid.endswith(".base"):
            base_name = tid.removesuffix(".base")
            matching_dir = tasks_dir / base_name
            if matching_dir.exists():
                task_id_to_dir[tid] = matching_dir
        else:
            matching_dir = tasks_dir / tid
            if matching_dir.exists():
                task_id_to_dir[tid] = matching_dir

    logger.info("Found %d core tasks in repository", len(task_id_to_dir))

    # Filter by specific task IDs if provided
    if task_ids is not None:
        task_id_to_dir = {
            k: v
            for k, v in task_id_to_dir.items()
            if k in task_ids or v.name in task_ids
        }
        logger.info("Filtered to %d matching task_ids", len(task_id_to_dir))

    # Convert to list and limit
    task_items = sorted(task_id_to_dir.items())
    if n_tasks is not None:
        task_items = task_items[:n_tasks]
        logger.info("Limited to first %d tasks", len(task_items))

    # Convert to task instances
    tasks = []
    for task_id, task_dir in task_items:
        try:
            # Load problem statement from task.yaml
            problem_statement = ""
            task_yaml = task_dir / "task.yaml"
            if task_yaml.exists():
                with open(task_yaml, encoding="utf-8") as f:
                    task_config = yaml.safe_load(f) or {}
                    problem_statement = task_config.get("instruction", "")

            tasks.append(
                {
                    "task_id": task_id,
                    "instance_id": task_id,
                    "problem_statement": problem_statement,
                    "repo": task_id,
                    "task_dir": str(task_dir),
                }
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error loading task %s: %s", task_id, e)

    logger.info("Loaded %d Terminal-Bench tasks", len(tasks))
    return tasks


def generate_run_id() -> str:
    """Generate a unique run ID with timestamp and short UUID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"{timestamp}_{short_uuid}"


def get_run_files(run_id: str, base_dir: str = ".") -> dict[str, Path]:
    """Get all file paths for a given run ID.

    Args:
      run_id: The unique identifier for the run.
      base_dir: The base directory where run files are stored.

    Returns:
      A dictionary mapping file types to their full paths.
    """
    base_path = Path(base_dir)
    return {
        "predictions": base_path / f"predictions_{run_id}.json",
        "trajectories": base_path / f"trajectories_{run_id}.json",
        "metadata": base_path / f"run_metadata_{run_id}.json",
    }


def save_progress(
    predictions_data: dict[str, Any],
    trajectories_data: dict[str, Any],
    run_metadata: dict[str, Any],
    run_id: str,
    base_dir: str = ".",
) -> None:
    """Save all progress data for a run.

    Args:
      predictions_data: A dictionary of prediction results.
      trajectories_data: A dictionary of trajectory data.
      run_metadata: A dictionary of metadata for the run.
      run_id: The unique identifier for the run.
      base_dir: The base directory where run files are stored.
    """
    try:
        files = get_run_files(run_id, base_dir)

        # Ensure directory exists
        os.makedirs(base_dir, exist_ok=True)

        # Data to save
        data_sets = [
            (files["predictions"], predictions_data),
            (files["trajectories"], trajectories_data),
            (files["metadata"], run_metadata),
        ]

        # Create backups and save each file
        for file_path, data in data_sets:
            file_path = str(file_path)  # Convert Path to string

            # Create backup if file exists
            if os.path.exists(file_path):
                backup_file = f"{file_path}.backup"
                os.rename(file_path, backup_file)

            try:
                # Save current data
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)

                # Remove backup after successful save
                backup_file = f"{file_path}.backup"
                if os.path.exists(backup_file):
                    os.remove(backup_file)

            except Exception:  # pylint: disable=broad-exception-caught
                # Restore backup if save failed
                backup_file = f"{file_path}.backup"
                if os.path.exists(backup_file):
                    os.rename(backup_file, file_path)
                raise

        logger.debug("Progress saved for run %s", run_id)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Failed to save progress for run %s: %s", run_id, e)
        raise


def load_progress(
    run_id: str, base_dir: str = "."
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load existing progress for a run ID.

    Args:
      run_id: The unique identifier for the run.
      base_dir: The base directory where run files are stored.

    Returns:
      A tuple containing three dictionaries:
        - predictions: Loaded prediction data.
        - trajectories: Loaded trajectory data.
        - metadata: Loaded run metadata.
    """
    files = get_run_files(run_id, base_dir)
    predictions_data = {}
    trajectories_data = {}
    metadata = {}

    # Load each file with backup fallback
    for data_type, (file_path, data_dict) in [
        ("predictions", (files["predictions"], predictions_data)),
        ("trajectories", (files["trajectories"], trajectories_data)),
        ("metadata", (files["metadata"], metadata)),
    ]:
        file_path = str(file_path)  # Convert Path to string

        if os.path.exists(file_path):
            try:
                with open(file_path, encoding="utf-8") as f:
                    loaded_data = json.load(f)
                data_dict.update(loaded_data)
                logger.debug(
                    "Loaded %d entries from %s file",
                    len(loaded_data),
                    data_type,
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(
                    "Failed to load %s file %s: %s", data_type, file_path, e
                )
                # Try backup file
                backup_file = f"{file_path}.backup"
                if os.path.exists(backup_file):
                    logger.info("Trying backup file %s", backup_file)
                    try:
                        with open(backup_file, encoding="utf-8") as f:
                            loaded_data = json.load(f)
                        data_dict.update(loaded_data)
                        logger.info(
                            "Loaded %d entries from backup %s file",
                            len(loaded_data),
                            data_type,
                        )
                    except Exception as backup_e:  # pylint: disable=broad-exception-caught
                        logger.error(
                            "Failed to load backup %s file: %s",
                            data_type,
                            backup_e,
                        )

    if predictions_data:
        logger.info(
            "Loaded run %s: %d predictions, %d trajectories",
            run_id,
            len(predictions_data),
            len(trajectories_data),
        )

    return predictions_data, trajectories_data, metadata


def process_instance(
    instance: dict[str, Any],
    max_turns: int,
    model_name: str,
    benchmark_type: str = "swebench",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Process a single benchmark instance.

    Args:
      instance: The instance dictionary to process.
      max_turns: The maximum number of turns for the agent.
      model_name: The name of the model to use.
      benchmark_type: The type of benchmark ('swebench' or 'terminalbench').

    Returns:
      A tuple containing the prediction and trajectory results.
    """
    instance_id = instance.get("instance_id") or instance.get(
        "task_id", "unknown"
    )
    start_time = time.time()
    logger.info("Processing instance: %s", instance_id)

    try:
        # Use context manager for automatic cleanup
        for i in range(5):
            # Use appropriate environment class
            if benchmark_type == "terminalbench":
                env = TerminalBenchEnvironment(instance)
            else:
                env = SWEBenchEnvironment(instance)

            with env:
                orchestrator = Orchestrator(env, benchmark_type=benchmark_type)

                # Normal agent execution
                patch, trajectory = asyncio.run(
                    orchestrator.run(max_turns=max_turns, model_name=model_name)
                )

                if patch and patch.strip():
                    break
                logger.info("Empty patch, retrying... (%d/3)", i + 1)
                time.sleep(60)

        elapsed_time = time.time() - start_time
        logger.info("Completed %s in %.2fs", instance_id, elapsed_time)

        prediction_result = {
            "model_name_or_path": model_name,
            "instance_id": instance_id,
            "model_patch": patch,
            "processing_time": elapsed_time,
            "status": "success",
        }

        trajectory_result = {
            "instance_id": instance_id,
            "trajectory": trajectory,
            "processing_time": elapsed_time,
            "status": "success",
        }

        return prediction_result, trajectory_result

    except Exception as e:  # pylint: disable=broad-exception-caught
        elapsed_time = time.time() - start_time
        logger.error(
            "Failed to process %s after %.2fs: %s", instance_id, elapsed_time, e
        )

        prediction_result = {
            "model_name_or_path": model_name,
            "instance_id": instance_id,
            "model_patch": None,
            "processing_time": elapsed_time,
            "status": "failed",
            "error": str(e),
        }

        trajectory_result = {
            "instance_id": instance_id,
            "trajectory": [],
            "processing_time": elapsed_time,
            "status": "failed",
            "error": str(e),
        }

        return prediction_result, trajectory_result


@app.command()
def run(
    instance_id_or_count: str = typer.Option(
        "astropy__astropy-12907",
        help=(
            "The SWE-bench instance ID to run, or the number of instances to"
            " run."
        ),
    ),
    model_name: str = typer.Option(
        "gemini-2.5-flash", help="The name of the model to use."
    ),
    dataset: str = typer.Option(
        "princeton-nlp/SWE-bench_Verified",
        help=(
            "The dataset to use. Options: 'princeton-nlp/SWE-bench_Verified' or"
            " 'terminalbench'"
        ),
    ),
    max_turns: int = typer.Option(
        300, help="The maximum number of turns for the agent."
    ),
    evaluate: bool = typer.Option(
        False, "--evaluate", help="Run evaluation after generating the patch."
    ),
    max_workers: int = typer.Option(
        1,
        "--max-workers",
        help="The maximum number of workers to use for parallel processing.",
    ),
    full_dataset: bool = typer.Option(
        False,
        "--full-dataset",
        help="Run on the full dataset instead of a subset.",
    ),
    resume: bool = typer.Option(
        True, "--resume/--no-resume", help="Resume from existing progress."
    ),
    save_frequency: int = typer.Option(
        10, "--save-freq", help="Save progress every N completed instances."
    ),
    run_id: str = typer.Option(
        None,
        "--run-id",
        help="Run ID for organizing results. Auto-generated if not provided.",
    ),
    base_dir: str = typer.Option(
        ".", "--base-dir", help="Base directory for saving results."
    ),
) -> None:
    """Run benchmark instances and generate patches with robust progress tracking.

    Args:
      instance_id_or_count: A specific instance/task ID to run, or the number of
        instances/tasks to process.
      model_name: The name of the model to use.
      dataset: The dataset to use. Options: 'princeton-nlp/SWE-bench_Verified' or
        'terminalbench'
      max_turns: The maximum number of turns for the agent.
      evaluate: Run evaluation after generating the patch.
      max_workers: The maximum number of workers to use for parallel processing.
      full_dataset: Run on the full dataset instead of a subset.
      resume: Resume from existing progress.
      save_frequency: Save progress every N completed instances.
      run_id: Run ID for organizing results. Auto-generated if not provided.
      base_dir: Base directory for saving results.
    """
    start_time = time.time()

    # Determine benchmark type
    benchmark_type = (
        "terminalbench" if dataset == "terminalbench" else "swebench"
    )

    # Generate run ID if not provided
    if run_id is None:
        run_id = generate_run_id()
        logger.info("Generated run ID: %s", run_id)
    else:
        logger.info("Using provided run ID: %s", run_id)

    # Create run metadata
    run_metadata = {
        "run_id": run_id,
        "start_time": start_time,
        "dataset": dataset,
        "benchmark_type": benchmark_type,
        "model_name": model_name,
        "max_turns": max_turns,
        "max_workers": max_workers,
        "full_dataset": full_dataset,
        "save_frequency": save_frequency,
    }

    logger.info(
        "Starting benchmark run with dataset: %s (type: %s)",
        dataset,
        benchmark_type,
    )

    # Load dataset
    if benchmark_type == "terminalbench":
        # For terminalbench, load tasks from the tasks directory
        logger.info("Loading Terminal-Bench tasks...")

        # Determine which tasks to load
        task_ids = None
        n_tasks_to_load = None

        if not full_dataset:
            try:
                n_tasks_to_load = int(instance_id_or_count)
            except ValueError:
                # Specific task ID provided
                task_ids = [instance_id_or_count]

        benchmark_dataset = load_terminalbench_tasks(
            task_ids=task_ids,
            n_tasks=n_tasks_to_load if not full_dataset else None,
        )

        if not benchmark_dataset:
            logger.error("No Terminal-Bench tasks loaded")
            raise typer.Exit(code=1)

        total_instances = len(benchmark_dataset)
        logger.info("Loaded %d Terminal-Bench tasks", total_instances)
    else:
        # Load SWE-bench dataset
        benchmark_dataset = load_dataset(dataset, split="test")
        total_instances = len(benchmark_dataset)
        logger.info("Dataset loaded with %d total instances", total_instances)

    # Determine instances to run
    instances_to_run = []

    if benchmark_type == "terminalbench":
        # For terminalbench, tasks are already filtered during loading
        instances_to_run = benchmark_dataset
        logger.info("Running %d Terminal-Bench tasks", len(instances_to_run))
    # For SWE-bench
    elif full_dataset:
        instances_to_run = list(benchmark_dataset)
        logger.info("Running FULL dataset (%d instances)", total_instances)
    else:
        try:
            n = int(instance_id_or_count)
            instances_to_run = list(
                benchmark_dataset.select(range(min(n, total_instances)))
            )
            logger.info("Running the first %d instances", len(instances_to_run))
        except ValueError as exc:
            instance = next(
                (
                    i
                    for i in benchmark_dataset
                    if i["instance_id"] == instance_id_or_count
                ),
                None,
            )
            if instance is None:
                logger.error(
                    "Instance %s not found in the dataset",
                    instance_id_or_count,
                )
                raise typer.Exit(code=1) from exc
            instances_to_run.append(instance)
            logger.info("Running single instance: %s", instance_id_or_count)

    # Load existing progress
    predictions_data, trajectories_data, existing_metadata = (
        load_progress(run_id, base_dir) if resume else ({}, {}, {})
    )

    # Update metadata
    run_metadata.update(existing_metadata)

    # Filter out already completed instances
    if resume and predictions_data:
        completed_ids = set(predictions_data.keys())
        id_key = (
            "task_id" if benchmark_type == "terminalbench" else "instance_id"
        )
        instances_to_run = [
            i for i in instances_to_run if i.get(id_key) not in completed_ids
        ]
        logger.info(
            "Resuming run %s: %d already completed, %d remaining",
            run_id,
            len(completed_ids),
            len(instances_to_run),
        )

    if not instances_to_run:
        logger.info("All instances already completed!")
        return

    # Process instances with progress tracking
    completed_count = len(predictions_data)
    total_to_process = len(instances_to_run)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                process_instance,
                instance,
                max_turns,
                model_name,
                benchmark_type,
            ): instance
            for instance in instances_to_run
        }

        for future in as_completed(futures):
            try:
                prediction_result, trajectory_result = future.result()
                if prediction_result and trajectory_result:
                    instance_id = prediction_result["instance_id"]
                    predictions_data[instance_id] = prediction_result
                    trajectories_data[instance_id] = trajectory_result
                    completed_count += 1

                    # Progress logging
                    elapsed = time.time() - start_time
                    total_instances_in_run = (
                        total_to_process
                        + len(predictions_data)
                        - completed_count
                    )
                    progress_pct = (
                        (completed_count / total_instances_in_run) * 100
                        if total_instances_in_run > 0
                        else 100
                    )
                    avg_time = (
                        elapsed / completed_count if completed_count > 0 else 0
                    )
                    eta = avg_time * (
                        total_to_process
                        - (
                            completed_count
                            - len(predictions_data)
                            + completed_count
                        )
                    )

                    logger.info(
                        "Progress: %d/%d (%.1f%%) - ETA: %.1fmin",
                        completed_count,
                        total_instances_in_run,
                        progress_pct,
                        eta / 60,
                    )

                    # Periodic saves
                    if completed_count % save_frequency == 0:
                        run_metadata["last_save_time"] = time.time()
                        save_progress(
                            predictions_data,
                            trajectories_data,
                            run_metadata,
                            run_id,
                            base_dir,
                        )
                        logger.info("Progress saved for run %s", run_id)

            except Exception as exc:  # pylint: disable=broad-exception-caught
                instance_id = futures[future]["instance_id"]
                logger.error(
                    "Instance %s generated an exception: %s", instance_id, exc
                )

    # Final save
    run_metadata["completion_time"] = time.time()
    run_metadata["total_completed"] = len(predictions_data)
    save_progress(
        predictions_data, trajectories_data, run_metadata, run_id, base_dir
    )

    total_time = time.time() - start_time
    success_count = sum(
        1 for r in predictions_data.values() if r.get("status") == "success"
    )
    logger.info(
        "Completed run %s in %.1fmin. Success: %d/%d",
        run_id,
        total_time / 60,
        success_count,
        len(predictions_data),
    )

    # Show file locations
    files = get_run_files(run_id, base_dir)
    logger.info("Results saved:")
    logger.info("  Predictions: %s", files["predictions"])
    logger.info("  Trajectories: %s", files["trajectories"])
    logger.info("  Metadata: %s", files["metadata"])

    if evaluate:
        if benchmark_type == "terminalbench":
            # For terminalbench, evaluation happens inline during submission
            logger.info(
                "Terminal-Bench evaluation completed inline during agent runs"
            )

            # Parse test results from patches and compute accuracy
            # A task passes only if all test scripts pass (no "Passed: False")
            successful_count = 0
            for _, prediction in predictions_data.items():
                patch = prediction.get("model_patch", "")
                # Task is successful only if it has results and NO test failed
                if (
                    patch
                    and "Passed: False" not in patch
                    and "Passed: True" in patch
                ):
                    successful_count += 1

            accuracy = (
                successful_count / len(predictions_data)
                if predictions_data
                else 0
            )
            logger.info(
                "Terminal-Bench Accuracy: %.2f%% (%d/%d tasks passed)",
                accuracy * 100,
                successful_count,
                len(predictions_data),
            )
        else:
            # For SWE-bench, run standard evaluation
            logger.info("Running evaluation...")
            eval_args = {
                "predictions_path": str(files["predictions"]),
                "dataset_name": dataset,
                "max_workers": max_workers,
                "run_id": run_id,
                "split": "test",
                "instance_ids": None,
                "force_rebuild": False,
                "cache_level": "env",
                "clean": True,
                "open_file_limit": 4096,
                "timeout": 1800,
                "namespace": "swebench",
                "rewrite_reports": False,
                "modal": False,
                "instance_image_tag": "latest",
                "env_image_tag": "latest",
                "report_dir": ".",
            }
            run_evaluation.main(**eval_args)
            logger.info("Evaluation complete.")


if __name__ == "__main__":
    app()
