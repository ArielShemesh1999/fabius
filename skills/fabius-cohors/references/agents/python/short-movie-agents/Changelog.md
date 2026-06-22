# Changelog

## v0.3.2 - Upgrades

- Upgrade video model to veo-3.1-generate-001
- Pin dependencies
- Update README.md

## v0.3.1 - Refactor deployment and model updates

- Upgraded image generation model to `imagen-4.0-ultra-generate-001`.
- Set the location for video generation model to `us-central1`.
- Added `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` to the backend deployment in `Makefile`.
- Removed Terraform-based deployment, updated `README.md` and `Makefile` to reflect this change.

## v0.3.0 - Code updates based on agent-starter-pack 0.15.4

- Updated the codebase to align with the changes in `agent-starter-pack` version 0.15.4.

## v0.2.0 - Moved to a director workflow architecture

- Refactored the agent workflow from a sequential process to a director-based architecture for improved orchestration and flexibility.

## v0.1.0 - Initial version

- Initial release of the short movie generation agents.
- Implemented a sequential workflow for story generation, screenplay creation, storyboarding, and video production.
