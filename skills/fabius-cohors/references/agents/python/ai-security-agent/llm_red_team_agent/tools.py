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

from .agent_utils import execute_sub_agent
from .sub_agents import evaluator, red_team, target

# --- Initialize Workers ---
red_team_worker = red_team.create()
target_worker = target.create()
evaluator_worker = evaluator.create()

# --- Granular Tools ---


def generate_attack_prompt(risk_category: str) -> str:
    """
    TOOL 1: Asks the Red Team agent to generate a malicious prompt.
    Use this first.
    """
    print(f"\n    🛠️  [Tool Call] Generating Attack for '{risk_category}'...")
    return execute_sub_agent(red_team_worker, risk_category)


def simulate_target_response(attack_prompt: str) -> str:
    """
    TOOL 2: Sends an attack prompt to the Target agent (Victim) and gets the response.
    Use this after you have an attack prompt.
    """
    print("    🛠️  [Tool Call] Simulating Victim Response...")
    return execute_sub_agent(target_worker, attack_prompt)


def evaluate_interaction(attack_prompt: str, target_response: str) -> str:
    """
    TOOL 3: Asks the Evaluator to judge if the attack was successful.
    Use this last. Returns a PASS/FAIL verdict.
    """
    print("    🛠️  [Tool Call] Evaluating Interaction...")
    eval_query = f"[ATTACK]: {attack_prompt}\n[RESPONSE]: {target_response}"
    return execute_sub_agent(evaluator_worker, eval_query)
