#!/usr/bin/env python3
"""
Deployment script for Cookie Delivery Agent to Vertex AI Agent Engine.

This script deploys the cookie_scheduler_agent to Google Cloud Vertex AI Agent Engine
using the Vertex AI Python SDK.
"""

import logging
import os
import sys

import vertexai
from dotenv import load_dotenv, set_key
from vertexai import agent_engines

from cookie_scheduler_agent.agent import root_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def deploy_cookie_agent():
    """Deploy the cookie delivery agent to Vertex AI Agent Engine."""

    try:
        logger.info("🍪 Starting deployment of Cookie Delivery Agent...")

        # Get configuration from environment variables
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        staging_bucket_env = os.getenv("STAGING_BUCKET")

        if not project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT environment variable is required"
            )

        # Set up staging bucket - use env var or create default
        if staging_bucket_env:
            staging_bucket = (
                f"gs://{staging_bucket_env}"
                if not staging_bucket_env.startswith("gs://")
                else staging_bucket_env
            )
        else:
            staging_bucket = f"gs://{project_id}_staging_bucket"
            logger.info(f"Using default staging bucket: {staging_bucket}")

        logger.info(f"Deploying to project: {project_id}, location: {location}")

        # Initialize Vertex AI with staging bucket as required for agent engine deployment
        vertexai.init(
            project=project_id, location=location, staging_bucket=staging_bucket
        )
        logger.info("Vertex AI initialized")

        logger.info("Creating Agent Engine deployment...")

        # Deploy the agent using Vertex AI Agent Engine
        # Based on the agent starter pack examples, we need to wrap our agent
        # in an AgentEngine configuration

        logger.info("Preparing agent for deployment...")

        # Create the agent engine deployment using correct parameters
        logger.info(f"Using staging bucket: {staging_bucket}")

        # using requirements file for dependencies
        requirements = "requirements.txt"

        remote_agent = agent_engines.create(
            agent_engine=root_agent,
            requirements=requirements,
            display_name="Cookie Delivery Agent",
            description="Automated cookie delivery scheduling and confirmation system",
            min_instances=0,
            max_instances=1,
            # Include the entire cookie_scheduler_agent package with all dependencies
            extra_packages=["./cookie_scheduler_agent"],
        )

        logger.info("Agent deployment initiated successfully!")
        logger.info(f"Resource Name: {remote_agent.resource_name}")

        # Wait for deployment to complete (this might take several minutes)
        logger.info("Waiting for deployment to complete...")
        logger.info(
            "   This may take several minutes as containers are built and started..."
        )

        return remote_agent

    except ImportError as e:
        logger.error(f"Import Error!!!!: {e}")
        logger.error(
            "Make sure google-adk is installed and the agent module is in the Python path"
        )
        raise

    except Exception as e:
        logger.error(f"Deployment failed (sad) : {e}")
        raise


def main():
    """Main deployment function."""

    # Check required environment variables
    required_env_vars = [
        "GOOGLE_CLOUD_PROJECT",
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these in your .env file or environment")
        return False

    try:
        # Deploy the agent
        deployed_agent = deploy_cookie_agent()

        logger.info("Deployment completed successfully!")
        logger.info(f"Agent Resource ID: {deployed_agent.resource_name}")
        logger.info("Updating Agent Resource ID in .env file")
        # Update the .env file with the new Agent Resource ID
        set_key(".env", "AGENT_RESOURCE_ID", deployed_agent.resource_name)

        return True

    except Exception as e:
        logger.error(f"Deployment failed (sad) : {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
