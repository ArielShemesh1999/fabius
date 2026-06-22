"""Orchestrator for the benchmark agent."""

import json
import logging
import os
import posixpath
import shlex
import sys
import tempfile
import textwrap
import time
import traceback
import uuid
from pathlib import Path

from google.adk import runners
from google.adk.agents import RunConfig, llm_agent
from google.adk.models.google_llm import Gemini
from google.adk.planners import built_in_planner
from google.adk.sessions.session import Session
from google.genai import types

from . import swebench_environment, terminalbench_environment

logger = logging.getLogger(__name__)
SYSTEM_INSTRUCTIONS = "You are a software engineering agent solving a issue reported by a user. You are working in the background and do not have the ability to discuss with the user. Make your best attempt at implementing a solution, and call the `submit` tool when done."
TIMEOUT_EXIT_CODE = 124
MEMORY_LIMIT_EXIT_CODE = 137
MAX_VERIFICATION_TURN_COUNT = 40
MAX_STATE_SIZE_BYTES = 1024


class Orchestrator:
    """Orchestrator for the benchmark agent."""

    def __init__(
        self,
        env: swebench_environment.SWEBenchEnvironment
        | terminalbench_environment.TerminalBenchEnvironment,
        benchmark_type: str = "swebench",
    ):
        """Initialize orchestrator with an environment.

        Args:
          env: Either SWEBenchEnvironment (swebench) or TerminalBenchEnvironment
            (terminalbench)
          benchmark_type: Type of benchmark ("swebench" or "terminalbench")
        """
        self.env = env
        self.benchmark_type = benchmark_type
        self.patch = None
        self.trajectory = []  # Store complete agent trajectory
        self.last_edit_backup = None
        if self.benchmark_type == "terminalbench":
            self.working_dir = self.env.get_working_dir()
        else:
            self.working_dir = "/testbed"
        self.num_submit_calls = 0
        self.turn_count = 0

    def read_file(
        self,
        file_path: str,
        start_line: int = 1,
        end_line: int = 0,
    ) -> str:
        # pylint: disable=line-too-long
        """Get the content of a file by reading a given range of lines.

        If possible, try to use this tool to only reach the lines that are relevant to the task.

        Note: this tool does not work for files outside the repo. For example `/dev/null` or `/bin/bash will not work. It can return FileNotFoundError if a file does not exist, please use the bash tool to browse the list of files available in the repo first.

        Args:
          file_path: The path of the file to read relative to the project directory.
          start_line: The 1-indexed line number to start reading from.
          end_line: The inclusive 1-indexed line number to end reading at. By default, it will read 500 lines from the start line. Set to -1 to read the entire file. Use the feature of the whole file sparingly as it may lead to very large responses.

        Returns:
          A string containing the read file content, or an error message.
        """
        # pylint: enable=line-too-long
        start_line = int(start_line)
        end_line = int(end_line)

        # Use 'cat' to read the file content
        exit_code, file_content = self.env.execute(
            f"cat {shlex.quote(file_path)}"
        )

        if exit_code != 0:
            logger.error("Error: file %s not found or not readable.", file_path)
            return f"Error: file {file_path} not found or not readable."

        end_msg = ""
        file_content_lines = file_content.splitlines()

        file_content_lines = [
            f"{line_idx + 1}\t{line}"
            for line_idx, line in enumerate(file_content_lines)
        ]

        if end_line == -1:
            end_line = len(file_content_lines)
        elif end_line == 0:
            end_line = start_line + 500 - 1

        if start_line < 1:
            return f"Error: Start line {start_line} must be 1-indexed."

        if start_line > len(file_content_lines):
            return (
                f"Error: Start line {start_line} must be less than or equal to"
                " the total number of lines in the file:"
                f" {len(file_content_lines)}."
            )

        end_line = min(end_line, len(file_content_lines))

        preamble = (
            f"Showing the content of file {file_path} from line {start_line} to"
            f" line {end_line}. Lines are annotated with line numbers followed "
            f"by **one extra** tab. There are {len(file_content_lines)}"
            "  lines in total in this file:\n"
        )

        if start_line > 1:
            preamble += f"\n... lines 1-{start_line - 1} above omitted ...\n"

        content_to_show = "\n".join(
            file_content_lines[start_line - 1 : end_line]
        )

        lines_after_omitted = len(file_content_lines) - end_line
        if lines_after_omitted > 0:
            end_msg = (
                f"\n... lines {end_line + 1}-{len(file_content_lines)} below"
                " omitted ..."
            )

        output = preamble + content_to_show + end_msg

        return output

    def create_file(self, file_path: str, content: str) -> str:
        # pylint: disable=line-too-long
        """Create a new file. If the directory does not exist, it will be created.

        Args:
          file_path: The path of the new file (relative to the project directory).
          content: The content of the file to create.

        Returns:
          A message indicating whether the file was created successfully.
        """
        # pylint: enable=line-too-long
        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8"
            ) as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name

            # Ensure parent directory exists in container.
            dir_name = os.path.dirname(file_path)
            if dir_name:
                self.env.execute(f"mkdir -p {shlex.quote(dir_name)}")

            self.env.copy_to(
                tmp_file_path, os.path.join(self.working_dir, file_path)
            )

            return f"File {file_path} created successfully."
        except Exception as e:  # pylint: disable=broad-exception-caught
            return f"Error creating file {file_path}: {e}"
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    def edit_file(self, file_path: str, diff: str) -> str:
        # pylint: disable=line-too-long
        """Edit a file in the codebase. Use this to make any edits to the codebase. Do not use this tool to create new files. Use the create_file tool for that.

        Args:
          file_path: The path of the file (relative to the project directory)to edit.
          diff: Output a search-replace style diff.
            (1) Each SEARCH/REPLACE block starts with: <<<<<<< SEARCH
            (2) Followed by a contiguous chunk of lines to search for in the existing source code
            (3) This is followed by a dividing line: =======
            (4) Then followed by the lines to replace into the source code.
            (5) The end of the replace block: >>>>>>> REPLACE
            (6) Keep *SEARCH/REPLACE* blocks concise. Include just the changing lines, and a few surrounding lines if needed to make a unique match. The tool will return an error if there are multiple matches.
            (7) To make multiple edits to the same file, stack a series of concise *SEARCH/REPLACE* blocks.
            (8) Do not include long runs of unchanging lines in *SEARCH/REPLACE* blocks. Break large *SEARCH/REPLACE* blocks into a series of smaller blocks that each change a small portion of the file.
            (9) The search parts in different *SEARCH/REPLACE* blocks should not overlap.
            (10) Do not put any code lines outside of *SEARCH/REPLACE* blocks.

            Example:
            <<<<<<< SEARCH
              hello!
            =======
              hello world!
            >>>>>>> REPLACE
            <<<<<<< SEARCH
              another line to search for
            =======
              another line to replace
            >>>>>>> REPLACE

        Note: This tool automatically backs up the file before editing. You can use undo_last_edit to revert, but only the most recent edit per file is backed up.

        Returns:
            A message indicating whether the edit was applied successfully.
        """
        # pylint: enable=line-too-long
        try:
            # Basic validation (mirroring internal version's structure)
            if not (
                "<<<<<<< SEARCH" in diff
                and "=======" in diff
                and ">>>>>>> REPLACE" in diff
            ):
                return "Error: Invalid diff format. Missing SEARCH/REPLACE markers."

            # Read the file content
            exit_code, file_content = self.env.execute(
                f"cat {shlex.quote(file_path)}"
            )
            if exit_code != 0:
                return f"Error: File {file_path} not found or not readable."

            # Backup the original file content before applying edits
            if self.last_edit_backup is None:
                self.last_edit_backup = {}
            self.last_edit_backup[file_path] = file_content

            original_file_content = file_content
            blocks = diff.split("<<<<<<< SEARCH")
            for block in blocks:
                if "=======" not in block or ">>>>>>> REPLACE" not in block:
                    continue

                search_part, replace_part = block.split("=======")
                search_block = search_part
                replace_block = replace_part.split(">>>>>>> REPLACE")[0]

                # Check if search block exists and is unique
                if file_content.count(search_block) == 0:
                    return f"Error: Search string not found in {file_path}."
                if file_content.count(search_block) > 1:
                    return (
                        f"Error: Ambiguous search string in {file_path}. Please provide"
                        " more context."
                    )

                # Apply the edit
                file_content = file_content.replace(search_block, replace_block)

            # Check if any changes were made
            if original_file_content == file_content:
                return (
                    "Error: No changes were made to the file. "
                    "Please check your diff and try again."
                )

            output = self.create_file(file_path, file_content)
            # Check if the file was created successfully
            if "created successfully." not in output:
                raise ValueError(output)

            result = f"Successfully edited file {file_path}."

        except Exception as e:  # pylint: disable=broad-exception-caught
            result = f"Error applying diff: {e}"
            logger.error(result)

        return result

    def undo_last_edit(self, file_path: str) -> str:
        # pylint: disable=line-too-long
        """Undo the last edit to a file made by the edit_file tool.

        This tool only revert the last changes made by the edit_file tool and does not affect edits made by other means (e.g., shell commands).
        The tool can only undo the last edit to the file. You cannot go back to more than one previous edit.

        Args:
          file_path: The path of the file (relative to the project directory) to undo the last edit to.

        Returns:
            A message indicating whether the undo was successful.
        """
        # pylint: enable=line-too-long
        if not self.last_edit_backup or file_path not in self.last_edit_backup:
            return (
                f"Error: Unable to undo the last edit to file: {file_path}\nThe file"
                " is not found, or the file has not been edited, or the file has"
                " been reverted previously."
            )

        last_edit_state = self.last_edit_backup.pop(file_path)
        self.create_file(file_path, last_edit_state)

        return f"Successfully reverted the last edit to file: {file_path}."

    def run_shell_command(
        self,
        cmd: str,
    ) -> str:
        # pylint: disable=line-too-long
        """Run any shell commands using /bin/sh.

        Use this tool to run any shell commands, for example:
        1. Grep a file and view specific lines.
        2. View the list of files in the repo.
        3. Run tests to see if your changes work.
        4. Use piping to chain multiple commands.

        Note: Shell states are not preserved. Everytime you run this tool, you will be in the root directory of the repository.
        Note: Output is automatically truncated to 500 lines. Revise your command to limit output if needed (e.g., use grep with specific patterns, or pipe to head/tail).

        Args:
            cmd: The shell command to run.

        Returns:
            The output of the command as a string.
        """
        # pylint: enable=line-too-long
        timeout_seconds = 120
        max_lines = 500

        # Use 'timeout' command to enforce the timeout
        cmd_with_timeout = (
            f"timeout {timeout_seconds}s /bin/sh -c {shlex.quote(cmd)}"
        )

        exit_code, output = self.env.execute(cmd_with_timeout, demux=True)

        if exit_code == TIMEOUT_EXIT_CODE:
            return (
                f"Error: The command timed out after {timeout_seconds} seconds."
            )
        elif exit_code == MEMORY_LIMIT_EXIT_CODE:
            return "Error: The command exceeded the memory limit"

        stdout, stderr = output
        formatted_output = ""
        is_output_truncated = False

        if stdout:
            stdout, is_out_truncated = self._maybe_truncate_output(
                stdout, max_lines
            )
            formatted_output += f"Stdout:\n{stdout}\n"
            is_output_truncated |= is_out_truncated
        if stderr:
            stderr, is_err_truncated = self._maybe_truncate_output(
                stderr, max_lines
            )
            formatted_output += f"Stderr:\n{stderr}\n"
            is_output_truncated |= is_err_truncated

        output_preamble = f"Command exited with status {exit_code}\n"

        if exit_code != 0:
            logger.error(cmd)
            logger.error("Error: Command failed with exit code %d.", exit_code)

        if is_output_truncated:
            output_preamble += (
                "There are truncated output. Revise your command line to"
                " limit the output.\n\n"
            )

        result = output_preamble + formatted_output
        return result

    def _maybe_truncate_output(
        self,
        output: str,
        max_lines: int = 50,
        max_characters_per_line: int = 320,  # Roughly 80 tokens.
    ) -> tuple[str, bool]:
        """Truncate the output by omitting the middle lines.

        ```output
        line 1
        line 2
        (... omitted xxx lines ...)
        line 3
        line 4
        ```

        Args:
        output: The output to truncate.
        max_lines: The maximum number of lines to keep.
        max_characters_per_line: The maximum number of characters to keep per line.

        Returns:
        A tuple of (truncated_output, is_truncated).
        """
        if max_lines <= 0:
            return output, False

        lines = output.splitlines(keepends=True)
        lines = [
            self._truncate_text(line, max_characters_per_line) for line in lines
        ]
        num_lines = len(lines)

        if num_lines <= max_lines:
            return "".join(lines), False

        half_max_lines = max_lines // 2
        omitted_lines = num_lines - max_lines

        truncated_output = (
            f"(Output too large with {num_lines} lines. Only show the first and last"
            f" {half_max_lines} lines)\n"
            + "".join(lines[:half_max_lines])
            + f"\n(... truncated {omitted_lines} lines ...)\n"
            + "".join(lines[-(max_lines - half_max_lines) :])
        )

        return truncated_output, True

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncates text in the middle and only keep max_length characters."""
        if len(text) <= max_length:
            return text

        num_truncated_chars = len(text) - max_length
        ellipsis = (
            f"(...line too long, truncated {num_truncated_chars} characters...)"
        )

        # Distribute these characters between the prefix and the suffix.
        # If max_length is odd, the prefix gets the extra character.
        len_prefix = (max_length + 1) // 2
        len_suffix = max_length // 2

        prefix = text[:len_prefix]
        suffix = text[len(text) - len_suffix :]

        return f"{prefix}{ellipsis}{suffix}"

    def _run_tests_internal(self) -> tuple[bool, str]:
        """Internal method to run tests for terminalbench (not exposed to agent).

        Returns:
            Tuple of (success: bool, results: str)
        """
        # Get the task directory from the environment
        task_dir = getattr(self.env, "task_dir", None)
        if not task_dir:
            return False, "Task directory not available in environment"

        task_dir = Path(task_dir)
        if not task_dir.exists():
            return False, f"Task directory not found: {task_dir}"

        # Check for run-tests.sh in task root
        run_tests_script = task_dir / "run-tests.sh"
        if not run_tests_script.exists():
            return False, f"run-tests.sh not found in {task_dir}"

        # Copy test files into the container AFTER agent execution
        tests_dir = task_dir / "tests"
        if not tests_dir.exists():
            return False, f"Tests directory not found: {tests_dir}"

        # Create /tests directory in container
        self.env.execute("mkdir -p /tests")

        # Copy ALL files from tests directory into the container
        # (not just shell scripts - includes test_outputs.py and other test files)
        for test_file in tests_dir.iterdir():
            if test_file.is_file():
                try:
                    self.env.copy_to(str(test_file), f"/tests/{test_file.name}")
                    # Make shell scripts executable
                    if test_file.suffix == ".sh":
                        self.env.execute(f"chmod +x /tests/{test_file.name}")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    return (
                        False,
                        f"Failed to copy test file {test_file.name}: {e}",
                    )

        # Copy run-tests.sh to the container
        try:
            run_tests_path_in_container = posixpath.join(
                self.working_dir, "run-tests.sh"
            )
            self.env.copy_to(str(run_tests_script), run_tests_path_in_container)
            self.env.execute(f"chmod +x {run_tests_path_in_container}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            return False, f"Failed to copy run-tests.sh: {e}"

        # Run run-tests.sh with TEST_DIR environment variable set
        full_command = (
            f"export TEST_DIR=/tests && bash {run_tests_path_in_container}"
        )

        exit_code, output = self.env.execute(full_command)
        all_passed = exit_code == 0

        results = f"Test script: run-tests.sh\nPassed: {all_passed}\nOutput:\n{output}\n"

        return all_passed, results

    def _is_test_file(self, file_path: str) -> bool:
        """Whether a file in a Bolt repository is a test file."""
        file_path = Path(file_path)
        return (
            any(part in ("test", "tests") for part in file_path.parts)
            or file_path.name.endswith("_test.py")
            or file_path.name.startswith("test_")
        )

    def submit(self) -> str:
        # pylint: disable=line-too-long
        """Submits the current solution and ends the interaction.

        Don\'t submit unless you are confident that the solution is correct. For
        example after adding tests then executing them.

        Returns:
            A string indicating submission status.
        """
        # pylint: enable=line-too-long
        # For terminalbench, run tests internally (not shown to agent)
        if self.benchmark_type == "terminalbench":
            # Run the test scripts internally
            _, test_results = self._run_tests_internal()
            self.patch = test_results  # Store test results for evaluation
            # Don't show test results to agent, just confirm submission
            result = "Submitted successfully."
        else:
            # For swebench, generate git diff
            command = "git ls-files -z --others  --exclude-standard | xargs -0 git add -N && git diff --text HEAD"
            exit_code, output = self.env.execute(command)
            if exit_code != 0:
                result = f"Error: Failed to submit. Output:\\n{output}"
            else:
                # Check for meaningful edits
                changed_files_cmd = "git status --porcelain | awk '{print $2}'"
                _, changed_files_out = self.env.execute(changed_files_cmd)
                changed_files = changed_files_out.splitlines()

                num_edited_code_files = 0
                for file_path in changed_files:
                    if self._is_test_file(file_path):
                        continue

                    file_name = os.path.basename(file_path)
                    if (
                        file_name.endswith(".toml")
                        or file_name.endswith(".ini")
                        or file_name == "setup.py"
                    ):
                        continue

                    num_edited_code_files += 1

                if num_edited_code_files == 0:
                    return (
                        "Observation: No meaningful existing code files were edited."
                        " Remember that the repository is guaranteed to have issues and"
                        " you MUST fix them."
                    )

                self.num_submit_calls += 1

                if (
                    self.num_submit_calls == 1
                    and self.turn_count < MAX_VERIFICATION_TURN_COUNT
                ):
                    verification_prompt = textwrap.dedent(
                        f"""
                        You are trying to submit your work, but before that, please carefully verify that you have performed the following steps as described in your instructions:

                        1. You have **thoroughly** tested your solution by creating two comprehensive tests covering different edge cases. If you only tested the main functionality so far, you should create another test with more comprehensive test cases. Do **NOT** split existing tests into two seperate tests to satisfy this requirement. You have to create new tests from scratch if needed.

                        2. Regression tests: You have run any **existing** related tests in the repository besides your newly created tests to make sure your changes do not regress or break anything.
                            - **Very important:** Make sure you also run a broader set of existing tests, not just the ones in the same test files you edited.
                            - If there is a regression, be rigourous and fix it. Also update existing tests if necessary.
                            - You should **NEVER** give up fixing the issue if the regression is related to your changes.

                        Make sure you have completed all the above steps before submitting your work. If you have completed all the above steps, call the submit tool again. Otherwise, go back and perform the missing steps.

                        Remember, You should use as many tool calls as possiblle, ideally more than 100 steps of tool calls, you only used {self.turn_count} tool calls so far."""
                    )
                    return verification_prompt

                self.patch = output
                result = f"Submitted successfully.\nTurns Taken: {self.turn_count}\nFiles Edited: {num_edited_code_files}"

        return result

    @classmethod
    def _remove_inline_data_binary(cls, session_arg: Session) -> Session:
        """Removes inline data binary in the session events content parts."""
        for event_item in session_arg.events:
            if event_item.content:
                for part in event_item.content.parts:
                    if part.inline_data and part.inline_data.data:
                        part.inline_data.data = b"Inline data removed."

        # Clear large values from the state as well.
        if session_arg.state:
            for key in list(session_arg.state):
                if sys.getsizeof(session_arg.state[key]) > MAX_STATE_SIZE_BYTES:
                    session_arg.state[key] = "removed"

        return session_arg

    async def run(
        self, max_turns: int = 120, model_name: str = "gemini-2.5-flash"
    ) -> tuple[str | None, list]:
        """Runs the agent to solve the benchmark task.

        Args:
            max_turns: The maximum number of turns to allow the agent to run.
            model_name: The name of the Gemini model to use.

        Returns:
            tuple: (patch, trajectory) where trajectory contains all tool calls and
            responses
        """
        start_time = time.time()

        # Initialize trajectory metadata
        self.trajectory = [
            {
                "type": "metadata",
                "timestamp": start_time,
                "instance_id": self.env.instance.get("instance_id", "unknown"),
                "repo": self.env.instance.get("repo", "unknown"),
                "max_turns": max_turns,
                "problem_statement": self.env.instance.get(
                    "problem_statement", ""
                ),
            }
        ]
        task_specification = (
            textwrap.dedent(
                f"""\
            I need you to solve the following issue in {self.env.instance["repo"]}:
            <issue>
            {{PROBLEM_STATEMENT}}
            </issue>
        """
            )
            .strip()
            .format(PROBLEM_STATEMENT=self.env.instance["problem_statement"])
        )

        agent = llm_agent.LlmAgent(
            name="benchmark_agent",
            model=Gemini(
                model=model_name,
                retry_options=types.HttpRetryOptions(
                    attempts=10,
                    exp_base=2,
                    initial_delay=1,
                    http_status_codes=[
                        429,
                        499,
                        500,
                        503,
                        504,
                    ],  # Retry on these HTTP errors
                ),
            ),
            planner=built_in_planner.BuiltInPlanner(
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True, thinking_budget=-1
                )
            ),
            instruction=SYSTEM_INSTRUCTIONS,
            tools=[
                self.read_file,
                self.create_file,
                self.edit_file,
                self.run_shell_command,
                self.undo_last_edit,
                self.submit,
            ],
        )

        runner = runners.InMemoryRunner(agent=agent)
        logger.info("Running agent with %d turns.", max_turns)
        config = RunConfig(max_llm_calls=max_turns)
        session_id = str(uuid.uuid4())
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id="user",
            session_id=session_id,
        )

        self.turn_count = 0
        try:
            async for event in runner.run_async(
                user_id="user",
                session_id=session_id,
                run_config=config,
                new_message=types.Content(
                    role="user", parts=[types.Part(text=task_specification)]
                ),
            ):
                if getattr(event.content, "role", None) == "model":
                    self.turn_count += 1
                # Check if we should terminate due to successful submission
                if self.patch and self.patch.strip():
                    break
        except Exception:  # pylint: disable=broad-exception-caught
            logger.error(traceback.format_exc())

        current_session = await runner.session_service.get_session(
            app_name=runner.app_name,
            user_id="user",
            session_id=session_id,
        )

        current_session = self._remove_inline_data_binary(current_session)
        self.trajectory.extend(
            json.loads(current_session.model_dump_json())["events"]
        )

        end_time = time.time()
        await runner.close()
        self.trajectory.append(
            {
                "timestamp": end_time,
                "duration": end_time - start_time,
                "total_turns": self.turn_count,
                "patch_generated": self.patch is not None,
            }
        )

        return self.patch, self.trajectory
