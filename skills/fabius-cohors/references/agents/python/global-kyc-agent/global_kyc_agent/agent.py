import sys

from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.agents.base_agent import BaseAgentState
from google.adk.agents.parallel_agent import (
    _create_branch_ctx_for_sub_agent,
    _merge_agent_run,
    _merge_agent_run_pre_3_11,
)
from google.adk.agents.sequential_agent import SequentialAgentState
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.utils.context_utils import Aclosing

from .prompt import GLOBAL_KYC_INSTRUCTION
from .shared_libraries.config import config

# Import Sub-Agents
from .sub_agents.uk_kyc.agent import uk_kyc_agent
from .sub_agents.usa_kyc.agent import usa_kyc_agent


class SubAgentEvent(Event):
    """Event wrapper that hides final response status.

    This is used to prevent parent agents from breaking their execution loop
    prematurely when a subagent finishes.
    """

    def is_final_response(self) -> bool:
        return False


# Workaround Patches
original_seq_run_async_impl = SequentialAgent._run_async_impl


async def workaround_seq_run_async_impl(self, ctx):
    if not self.sub_agents:
        return

    agent_state = self._load_agent_state(ctx, SequentialAgentState)
    start_index = self._get_start_index(agent_state)

    pause_invocation = False
    resuming_sub_agent = agent_state is not None

    for i in range(start_index, len(self.sub_agents)):
        sub_agent = self.sub_agents[i]
        if not resuming_sub_agent:
            if ctx.is_resumable:
                agent_state = SequentialAgentState(
                    current_sub_agent=sub_agent.name
                )
                ctx.set_agent_state(self.name, agent_state=agent_state)
                yield self._create_agent_state_event(ctx)

        sub_ctx = ctx.model_copy(update={"agent": sub_agent})
        async with Aclosing(sub_agent.run_async(sub_ctx)) as agen:
            async for event in agen:
                # Wrap event if NOT the last subagent
                if i < len(self.sub_agents) - 1:
                    if event.author != self.name:
                        wrapped_event = SubAgentEvent(
                            author=event.author,
                            content=event.content,
                            timestamp=event.timestamp,
                            actions=event.actions,
                            invocation_id=event.invocation_id,
                            # id=event.id,
                            branch=event.branch,
                        )
                        yield wrapped_event
                    else:
                        yield event
                else:
                    # Last subagent, yield unwrapped
                    yield event

                if ctx.should_pause_invocation(event):
                    pause_invocation = True

        if pause_invocation:
            return

        resuming_sub_agent = False

    if ctx.is_resumable:
        ctx.set_agent_state(self.name, end_of_agent=True)
        yield self._create_agent_state_event(ctx)


SequentialAgent._run_async_impl = workaround_seq_run_async_impl

original_parallel_run_async_impl = ParallelAgent._run_async_impl


def _create_final_event(last_event, accumulated_state_delta, author_name):
    dump = last_event.model_dump()
    dump["id"] = ""  # Force new ID
    final_event = Event(**dump)
    if final_event.actions:
        final_event.actions.state_delta = accumulated_state_delta
    else:
        final_event.actions = EventActions(state_delta=accumulated_state_delta)
    final_event.author = author_name
    return final_event


def _prepare_parallel_runs(agent, ctx):
    agent_runs = []
    for sub_agent in agent.sub_agents:
        sub_agent_ctx = _create_branch_ctx_for_sub_agent(agent, sub_agent, ctx)
        sub_agent_ctx.agent = sub_agent
        if not sub_agent_ctx.end_of_agents.get(sub_agent.name):
            agent_runs.append(sub_agent.run_async(sub_agent_ctx))
    return agent_runs


async def workaround_parallel_run_async_impl(self, ctx):
    if not self.sub_agents:
        return

    agent_state = self._load_agent_state(ctx, BaseAgentState)
    if ctx.is_resumable and agent_state is None:
        ctx.set_agent_state(self.name, agent_state=BaseAgentState())
        yield self._create_agent_state_event(ctx)

    agent_runs = _prepare_parallel_runs(self, ctx)

    pause_invocation = False
    try:
        merge_func = (
            _merge_agent_run
            if sys.version_info >= (3, 11)
            else _merge_agent_run_pre_3_11
        )

        last_event = None
        accumulated_state_delta = {}
        async with Aclosing(merge_func(agent_runs)) as agen:
            async for event in agen:
                last_event = event

                # Accumulate state delta
                if event.actions and event.actions.state_delta:
                    accumulated_state_delta.update(event.actions.state_delta)

                # Always wrap subagent events in ParallelAgent
                if event.author != self.name:
                    wrapped_event = SubAgentEvent(
                        author=event.author,
                        content=event.content,
                        timestamp=event.timestamp,
                        actions=event.actions,
                        invocation_id=event.invocation_id,
                        # id=event.id,
                        branch=event.branch,
                    )
                    yield wrapped_event
                else:
                    yield event

                if ctx.should_pause_invocation(event):
                    pause_invocation = True

        if pause_invocation:
            return

        # Yield a final response event if last_event was final
        if last_event and last_event.is_final_response():
            yield _create_final_event(
                last_event, accumulated_state_delta, self.name
            )

        if ctx.is_resumable and all(
            ctx.end_of_agents.get(sub_agent.name)
            for sub_agent in self.sub_agents
        ):
            ctx.set_agent_state(self.name, end_of_agent=True)
            yield self._create_agent_state_event(ctx)

    finally:
        for sub_agent_run in agent_runs:
            await sub_agent_run.aclose()


ParallelAgent._run_async_impl = workaround_parallel_run_async_impl

# ==========================================
# GLOBAL ROUTER AGENT
# ==========================================
root_agent = Agent(
    name="global_kyc_agent",
    model=config.gemini_model,
    description="Global KYC Agent that routes requests appropriately based on the geographical location of the company (UK vs USA).",
    instruction=GLOBAL_KYC_INSTRUCTION,
    sub_agents=[uk_kyc_agent, usa_kyc_agent],
)
