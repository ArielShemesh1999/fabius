"""
Agent entry point for the Nurse Rostering System.

This module provides flexible orchestration
   - Can handle varied requests
   - Delegates to RosteringWorkflow for generation tasks
   - Handles direct roster management (approve/reject)
"""

import logging

from nexshift_agent.sub_agents.coordinator import create_coordinator_agent

# Configure logging
logging.basicConfig(level=logging.INFO)


# This allows handling various requests and delegates to workflow for generation
root_agent = create_coordinator_agent()
