# import asyncio
from functools import partial

# from uuid import uuid4
from google.adk.agents.workflow.base_node import START

# from google.adk.agents.workflow.join_node import JoinNode
from google.adk.agents.workflow.function_node import FunctionNode
from google.adk.agents.workflow.parallel_worker import ParallelWorker
from google.adk.agents.workflow.workflow_agent import WorkflowAgent

# from google.adk.agents.run_config import RunConfig
# from google.adk.sessions.in_memory_session_service import InMemorySessionService
# from google.adk.sessions.session import Session
# from google.adk.agents.invocation_context import InvocationContext
# from google.genai.types import Content, ModelContent, Part
# Local sub-agent and node imports
from .agent_nodes.publishing import generate_blog_post_agent
from .agent_nodes.research import (
    distill_agent,
    research_worker_agent,
)
from .function_nodes.publishing import (
    post_node,
    route_changer,
    shoutout_node,
    start_blog,
)
from .function_nodes.research import save_node, start_node

# --- 1. Workflow Definitions ---

# Research Workflow: A simple, linear chain. The `research_worker_agent`
# is marked with `parallel_worker=True` so the framework will automatically
# handle fanning out for each query and fanning in the results.
research_workflow = WorkflowAgent(
    name="research_workflow",
    edges=[
        (
            START,
            start_node,
            ParallelWorker(research_worker_agent),
            distill_agent,
            save_node,
        ),
    ],
)

# Blog Workflow
# Nodes for posting the main article
post_to_x = FunctionNode(partial(post_node, "X"), name="Post to X")
post_to_linkedin = FunctionNode(
    partial(post_node, "LINKEDIN"), name="Post to LinkedIn"
)
post_to_medium = FunctionNode(
    partial(post_node, "MEDIUM"), name="Post to Medium"
)

# Nodes for posting shoutouts
shoutout_to_x = FunctionNode(partial(shoutout_node, "X"), name="Shoutout to X")
shoutout_to_linkedin = FunctionNode(
    partial(shoutout_node, "LINKEDIN"), name="Shoutout to LinkedIn"
)
shoutout_to_medium = FunctionNode(
    partial(shoutout_node, "MEDIUM"), name="Shoutout to Medium"
)
shoutout_to_reddit = FunctionNode(
    partial(shoutout_node, "REDDIT"), name="Shoutout to Reddit"
)

blog_workflow = WorkflowAgent(
    name="blog_workflow",
    edges=[
        # 1. Start, write blog, then route by length
        (START, start_blog, generate_blog_post_agent, route_changer),
        # 2. Post to the primary platform based on the route from route_changer
        (route_changer, post_to_x, "X"),
        (route_changer, post_to_linkedin, "LINKEDIN"),
        (route_changer, post_to_medium, "MEDIUM"),
        # 3. From each primary post, trigger shoutouts based on the new objective rules.
        # If posted to X -> Shoutout to LinkedIn and Reddit
        (post_to_x, shoutout_to_linkedin, "SHOUTOUT_LINKEDIN"),
        (post_to_x, shoutout_to_reddit, "SHOUTOUT_REDDIT"),
        # If posted to LinkedIn -> Shoutout to X and Reddit
        (post_to_linkedin, shoutout_to_x, "SHOUTOUT_X"),
        (post_to_linkedin, shoutout_to_reddit, "SHOUTOUT_REDDIT"),
        # If posted to Medium -> Shoutout to X and LinkedIn
        (post_to_medium, shoutout_to_x, "SHOUTOUT_X"),
        (post_to_medium, shoutout_to_linkedin, "SHOUTOUT_LINKEDIN"),
    ],
)

root_agent = WorkflowAgent(
    name="root_agent",
    description="""
        Main workflow contucting the research and pubication phases of blog 
        publication and advertisement.
    """,
    rerun_on_resume=True,
    edges=[("START", research_workflow, blog_workflow)],
)
