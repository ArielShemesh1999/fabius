# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Interactive ADK entry point; full benchmarks run via swe_benchmark_agent.main."""

from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="swe_benchmark_agent",
    model="gemini-2.5-flash",
    description=(
        "Sample software engineering agent for SWE-bench and TerminalBench "
        "benchmarks; use the CLI module for Docker-backed benchmark runs."
    ),
    instruction="""You are the SWE Benchmark Agent sample from Google ADK.

This chat entry point is for exploration. Full SWE-bench and TerminalBench
evaluations run in isolated Docker environments via the CLI, for example:

  uv run python -m swe_benchmark_agent.main --help

Answer questions briefly. For benchmarks, mention that users need Google Cloud
(Vertex), Docker, and the commands documented in the project README.
""",
)
