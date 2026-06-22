# orchestration

**163 orchestration agents** from [the author/orchestration](https://github.com/the author/orchestration) (claude-flow) — a multi-agent swarm-coordination framework. 108 core agents + 55 plugin agents across 32 plugins. Knowledge-only: agent definitions extracted, framework code / build artifacts / v3 duplicates stripped (see `LICENSE`).

## Core agents (`agents/`)

| Agent | Description | File |
|---|---|---|
| **Migration Summary** | Complete migration plan for converting command-based system to intelligent agent-based system | [`agents/MIGRATION_SUMMARY.md`](./agents/MIGRATION_SUMMARY.md) |
| **base-template-generator** | Use this agent when you need to create foundational templates, boilerplate code, or starter configurations for new projects, components, or features. This ag... | [`agents/base-template-generator.md`](./agents/base-template-generator.md) |
| **database-specialist** | Database design and optimization specialist | [`agents/database-specialist.md`](./agents/database-specialist.md) |
| **project-coordinator** | Coordinates multi-agent workflows for this project | [`agents/project-coordinator.md`](./agents/project-coordinator.md) |
| **python-specialist** | Python development specialist | [`agents/python-specialist.md`](./agents/python-specialist.md) |
| **security-auditor** | Security audit and hardening specialist | [`agents/security-auditor.md`](./agents/security-auditor.md) |
| **typescript-specialist** | TypeScript development specialist | [`agents/typescript-specialist.md`](./agents/typescript-specialist.md) |
| **byzantine-coordinator** | Coordinates Byzantine fault-tolerant consensus protocols with malicious actor detection | [`agents/consensus/byzantine-coordinator.md`](./agents/consensus/byzantine-coordinator.md) |
| **crdt-synchronizer** | Implements Conflict-free Replicated Data Types for eventually consistent state synchronization | [`agents/consensus/crdt-synchronizer.md`](./agents/consensus/crdt-synchronizer.md) |
| **gossip-coordinator** | Coordinates gossip-based consensus protocols for scalable eventually consistent systems | [`agents/consensus/gossip-coordinator.md`](./agents/consensus/gossip-coordinator.md) |
| **performance-benchmarker** | Implements comprehensive performance benchmarking for distributed consensus protocols | [`agents/consensus/performance-benchmarker.md`](./agents/consensus/performance-benchmarker.md) |
| **quorum-manager** | Implements dynamic quorum adjustment and intelligent membership management | [`agents/consensus/quorum-manager.md`](./agents/consensus/quorum-manager.md) |
| **raft-manager** | Manages Raft consensus algorithm with leader election and log replication | [`agents/consensus/raft-manager.md`](./agents/consensus/raft-manager.md) |
| **security-manager** | Implements comprehensive security mechanisms for distributed consensus protocols | [`agents/consensus/security-manager.md`](./agents/consensus/security-manager.md) |
| **adaptive-coordinator** | \| | [`agents/swarm/adaptive-coordinator.md`](./agents/swarm/adaptive-coordinator.md) |
| **hierarchical-coordinator** | Queen-led hierarchical swarm coordination with specialized worker delegation | [`agents/swarm/hierarchical-coordinator.md`](./agents/swarm/hierarchical-coordinator.md) |
| **mesh-coordinator** | Peer-to-peer mesh network swarm with distributed decision making and fault tolerance | [`agents/swarm/mesh-coordinator.md`](./agents/swarm/mesh-coordinator.md) |
| **api-docs** | Expert agent for creating and maintaining OpenAPI/Swagger documentation | [`agents/documentation/api-docs/docs-api-openapi.md`](./agents/documentation/api-docs/docs-api-openapi.md) |
| **agentic-payments** | \| | [`agents/payments/agentic-payments.md`](./agents/payments/agentic-payments.md) |
| **consensus-coordinator** | \| | [`agents/sublinear/consensus-coordinator.md`](./agents/sublinear/consensus-coordinator.md) |
| **matrix-optimizer** | \| | [`agents/sublinear/matrix-optimizer.md`](./agents/sublinear/matrix-optimizer.md) |
| **pagerank-analyzer** | \| | [`agents/sublinear/pagerank-analyzer.md`](./agents/sublinear/pagerank-analyzer.md) |
| **performance-optimizer** | \| | [`agents/sublinear/performance-optimizer.md`](./agents/sublinear/performance-optimizer.md) |
| **trading-predictor** | \| | [`agents/sublinear/trading-predictor.md`](./agents/sublinear/trading-predictor.md) |
| **cicd-engineer** | Specialized agent for GitHub Actions CI/CD pipeline creation and optimization | [`agents/devops/ci-cd/ops-cicd-github.md`](./agents/devops/ci-cd/ops-cicd-github.md) |
| **coder** | Implementation specialist for writing clean, efficient code | [`agents/core/coder.md`](./agents/core/coder.md) |
| **planner** | Strategic planning and task orchestration agent | [`agents/core/planner.md`](./agents/core/planner.md) |
| **researcher** | Deep research and information gathering specialist | [`agents/core/researcher.md`](./agents/core/researcher.md) |
| **reviewer** | Code review and quality assurance specialist | [`agents/core/reviewer.md`](./agents/core/reviewer.md) |
| **tester** | Comprehensive testing and quality assurance specialist | [`agents/core/tester.md`](./agents/core/tester.md) |
| **code-analyzer** | Advanced code quality analysis agent for comprehensive code reviews and improvements | [`agents/analysis/analyze-code-quality.md`](./agents/analysis/analyze-code-quality.md) |
| **analyst** | Advanced code quality analysis agent for comprehensive code reviews and improvements | [`agents/analysis/code-analyzer.md`](./agents/analysis/code-analyzer.md) |
| **code-analyzer** | Advanced code quality analysis agent for comprehensive code reviews and improvements | [`agents/analysis/code-review/analyze-code-quality.md`](./agents/analysis/code-review/analyze-code-quality.md) |
| **backend-dev** | Specialized agent for backend API development with self-learning and pattern recognition | [`agents/development/dev-backend-api.md`](./agents/development/dev-backend-api.md) |
| **backend-dev** | Specialized agent for backend API development, including REST and GraphQL endpoints | [`agents/development/backend/dev-backend-api.md`](./agents/development/backend/dev-backend-api.md) |
| **Benchmark Suite** | Comprehensive performance benchmarking, regression detection and performance validation | [`agents/optimization/benchmark-suite.md`](./agents/optimization/benchmark-suite.md) |
| **Load Balancing Coordinator** | Dynamic task distribution, work-stealing algorithms and adaptive load balancing | [`agents/optimization/load-balancer.md`](./agents/optimization/load-balancer.md) |
| **Performance Monitor** | Real-time metrics collection, bottleneck analysis, SLA monitoring and anomaly detection | [`agents/optimization/performance-monitor.md`](./agents/optimization/performance-monitor.md) |
| **Resource Allocator** | Adaptive resource allocation, predictive scaling and intelligent capacity planning | [`agents/optimization/resource-allocator.md`](./agents/optimization/resource-allocator.md) |
| **Topology Optimizer** | Dynamic swarm topology reconfiguration and communication pattern optimization | [`agents/optimization/topology-optimizer.md`](./agents/optimization/topology-optimizer.md) |
| **mobile-dev** | Expert agent for React Native mobile application development across iOS and Android | [`agents/specialized/mobile/spec-mobile-react-native.md`](./agents/specialized/mobile/spec-mobile-react-native.md) |
| **sona-learning-optimizer** | SONA-powered self-optimizing agent with LoRA fine-tuning and EWC++ memory preservation | [`agents/sona/sona-learning-optimizer.md`](./agents/sona/sona-learning-optimizer.md) |
| **sublinear-goal-planner** | \| | [`agents/reasoning/agent.md`](./agents/reasoning/agent.md) |
| **goal-planner** | \| | [`agents/reasoning/goal-planner.md`](./agents/reasoning/goal-planner.md) |
| **production-validator** | Production validation specialist ensuring applications are fully implemented and deployment-ready | [`agents/testing/production-validator.md`](./agents/testing/production-validator.md) |
| **tdd-london-swarm** | TDD London School specialist for mock-driven development within swarm coordination | [`agents/testing/tdd-london-swarm.md`](./agents/testing/tdd-london-swarm.md) |
| **tdd-london-swarm** | TDD London School specialist for mock-driven development within swarm coordination | [`agents/testing/unit/tdd-london-swarm.md`](./agents/testing/unit/tdd-london-swarm.md) |
| **production-validator** | Production validation specialist ensuring applications are fully implemented and deployment-ready | [`agents/testing/validation/production-validator.md`](./agents/testing/validation/production-validator.md) |
| **system-architect** | Expert agent for system architecture design, patterns, and high-level technical decisions | [`agents/architecture/system-design/arch-system-design.md`](./agents/architecture/system-design/arch-system-design.md) |
| **flow-nexus-app-store** | \| | [`agents/flow-nexus/app-store.md`](./agents/flow-nexus/app-store.md) |
| **flow-nexus-auth** | \| | [`agents/flow-nexus/authentication.md`](./agents/flow-nexus/authentication.md) |
| **flow-nexus-challenges** | \| | [`agents/flow-nexus/challenges.md`](./agents/flow-nexus/challenges.md) |
| **flow-nexus-neural** | \| | [`agents/flow-nexus/neural-network.md`](./agents/flow-nexus/neural-network.md) |
| **flow-nexus-payments** | \| | [`agents/flow-nexus/payments.md`](./agents/flow-nexus/payments.md) |
| **flow-nexus-sandbox** | \| | [`agents/flow-nexus/sandbox.md`](./agents/flow-nexus/sandbox.md) |
| **flow-nexus-swarm** | \| | [`agents/flow-nexus/swarm.md`](./agents/flow-nexus/swarm.md) |
| **flow-nexus-user-tools** | \| | [`agents/flow-nexus/user-tools.md`](./agents/flow-nexus/user-tools.md) |
| **flow-nexus-workflow** | \| | [`agents/flow-nexus/workflow.md`](./agents/flow-nexus/workflow.md) |
| **code-review-swarm** | \| | [`agents/github/code-review-swarm.md`](./agents/github/code-review-swarm.md) |
| **github-modes** | \| | [`agents/github/github-modes.md`](./agents/github/github-modes.md) |
| **issue-tracker** | \| | [`agents/github/issue-tracker.md`](./agents/github/issue-tracker.md) |
| **multi-repo-swarm** | Cross-repository swarm orchestration for organization-wide automation and intelligent collaboration | [`agents/github/multi-repo-swarm.md`](./agents/github/multi-repo-swarm.md) |
| **pr-manager** | \| | [`agents/github/pr-manager.md`](./agents/github/pr-manager.md) |
| **project-board-sync** | \| | [`agents/github/project-board-sync.md`](./agents/github/project-board-sync.md) |
| **release-manager** | \| | [`agents/github/release-manager.md`](./agents/github/release-manager.md) |
| **release-swarm** | \| | [`agents/github/release-swarm.md`](./agents/github/release-swarm.md) |
| **repo-architect** | \| | [`agents/github/repo-architect.md`](./agents/github/repo-architect.md) |
| **swarm-issue** | \| | [`agents/github/swarm-issue.md`](./agents/github/swarm-issue.md) |
| **swarm-pr** | \| | [`agents/github/swarm-pr.md`](./agents/github/swarm-pr.md) |
| **sync-coordinator** | \| | [`agents/github/sync-coordinator.md`](./agents/github/sync-coordinator.md) |
| **workflow-automation** | \| | [`agents/github/workflow-automation.md`](./agents/github/workflow-automation.md) |
| **database-specialist** | Database design and optimization specialist | [`agents/v3/database-specialist.md`](./agents/v3/database-specialist.md) |
| **project-coordinator** | Coordinates multi-agent workflows for this project | [`agents/v3/project-coordinator.md`](./agents/v3/project-coordinator.md) |
| **python-specialist** | Python development specialist | [`agents/v3/python-specialist.md`](./agents/v3/python-specialist.md) |
| **test-architect** | Testing and quality assurance specialist | [`agents/v3/test-architect.md`](./agents/v3/test-architect.md) |
| **typescript-specialist** | TypeScript development specialist | [`agents/v3/typescript-specialist.md`](./agents/v3/typescript-specialist.md) |
| **v3-integration-architect** | \| | [`agents/v3/v3-integration-architect.md`](./agents/v3/v3-integration-architect.md) |
| **v3-memory-specialist** | \| | [`agents/v3/v3-memory-specialist.md`](./agents/v3/v3-memory-specialist.md) |
| **v3-performance-engineer** | \| | [`agents/v3/v3-performance-engineer.md`](./agents/v3/v3-performance-engineer.md) |
| **v3-queen-coordinator** | \| | [`agents/v3/v3-queen-coordinator.md`](./agents/v3/v3-queen-coordinator.md) |
| **v3-security-architect** | \| | [`agents/v3/v3-security-architect.md`](./agents/v3/v3-security-architect.md) |
| **collective-intelligence-coordinator** | \| | [`agents/hive-mind/collective-intelligence-coordinator.md`](./agents/hive-mind/collective-intelligence-coordinator.md) |
| **queen-coordinator** | \| | [`agents/hive-mind/queen-coordinator.md`](./agents/hive-mind/queen-coordinator.md) |
| **scout-explorer** | \| | [`agents/hive-mind/scout-explorer.md`](./agents/hive-mind/scout-explorer.md) |
| **swarm-memory-manager** | \| | [`agents/hive-mind/swarm-memory-manager.md`](./agents/hive-mind/swarm-memory-manager.md) |
| **worker-specialist** | \| | [`agents/hive-mind/worker-specialist.md`](./agents/hive-mind/worker-specialist.md) |
| **smart-agent** | Intelligent agent coordination and dynamic spawning specialist | [`agents/templates/automation-smart-agent.md`](./agents/templates/automation-smart-agent.md) |
| **swarm-init** | Swarm initialization and topology optimization specialist | [`agents/templates/coordinator-swarm-init.md`](./agents/templates/coordinator-swarm-init.md) |
| **pr-manager** | Complete pull request lifecycle management and GitHub workflow coordination | [`agents/templates/github-pr-manager.md`](./agents/templates/github-pr-manager.md) |
| **sparc-coder** | Transform specifications into working code with TDD practices | [`agents/templates/implementer-sparc-coder.md`](./agents/templates/implementer-sparc-coder.md) |
| **memory-coordinator** | Manage persistent memory across sessions and facilitate cross-agent memory sharing | [`agents/templates/memory-coordinator.md`](./agents/templates/memory-coordinator.md) |
| **migration-planner** | Comprehensive migration plan for converting commands to agent-based system | [`agents/templates/migration-plan.md`](./agents/templates/migration-plan.md) |
| **task-orchestrator** | Central coordination agent for task decomposition, execution planning, and result synthesis | [`agents/templates/orchestrator-task.md`](./agents/templates/orchestrator-task.md) |
| **perf-analyzer** | Performance bottleneck analyzer for identifying and resolving workflow inefficiencies | [`agents/templates/performance-analyzer.md`](./agents/templates/performance-analyzer.md) |
| **sparc-coord** | SPARC methodology orchestrator for systematic development phase coordination | [`agents/templates/sparc-coordinator.md`](./agents/templates/sparc-coordinator.md) |
| **test-long-runner** | Test agent that can run for 30+ minutes on complex tasks | [`agents/custom/test-long-runner.md`](./agents/custom/test-long-runner.md) |
| **ml-developer** | Specialized agent for machine learning model development, training, and deployment | [`agents/data/ml/data-ml-model.md`](./agents/data/ml/data-ml-model.md) |
| **safla-neural** | \| | [`agents/neural/safla-neural.md`](./agents/neural/safla-neural.md) |
| **architecture** | SPARC Architecture phase specialist for system design | [`agents/sparc/architecture.md`](./agents/sparc/architecture.md) |
| **pseudocode** | SPARC Pseudocode phase specialist for algorithm design | [`agents/sparc/pseudocode.md`](./agents/sparc/pseudocode.md) |
| **refinement** | SPARC Refinement phase specialist for iterative improvement | [`agents/sparc/refinement.md`](./agents/sparc/refinement.md) |
| **specification** | SPARC Specification phase specialist for requirements analysis | [`agents/sparc/specification.md`](./agents/sparc/specification.md) |
| **codex-coordinator** | Coordinates multiple headless Codex workers for parallel execution | [`agents/dual-mode/codex-coordinator.md`](./agents/dual-mode/codex-coordinator.md) |
| **codex-worker** | Headless Codex background worker for parallel task execution with self-learning | [`agents/dual-mode/codex-worker.md`](./agents/dual-mode/codex-worker.md) |
| **dual-orchestrator** | Orchestrates Claude Code (interactive) + Codex (headless) for hybrid workflows | [`agents/dual-mode/dual-orchestrator.md`](./agents/dual-mode/dual-orchestrator.md) |
| **sublinear-goal-planner** | \| | [`agents/goal/agent.md`](./agents/goal/agent.md) |
| **code-goal-planner** | Code-centric Goal-Oriented Action Planning specialist that creates intelligent plans for software development objectives. Excels at breaking down complex cod... | [`agents/goal/code-goal-planner.md`](./agents/goal/code-goal-planner.md) |
| **goal-planner** | \| | [`agents/goal/goal-planner.md`](./agents/goal/goal-planner.md) |

## Plugin agents (`plugins/`)

### orchestration-adr

| Agent | Description | File |
|---|---|---|
| **adr-architect** | ADR lifecycle manager -- create, index, supersede, and link Architecture Decision Records to code | [`plugins/orchestration-adr/adr-architect.md`](./plugins/orchestration-adr/adr-architect.md) |

### orchestration-agent

| Agent | Description | File |
|---|---|---|
| **nested-coordinator** | Orchestrator that spawns nested sub-agents (up to depth=5) via Claude Code's native Task tool — for deep delegation where context isolation matters more than... | [`plugins/orchestration-agent/nested-coordinator.md`](./plugins/orchestration-agent/nested-coordinator.md) |
| **nested-leaf** | Leaf-worker template for nested spawn trees — performs one focused task and returns a structured summary. Deliberately does NOT have the Task tool (least-pri... | [`plugins/orchestration-agent/nested-leaf.md`](./plugins/orchestration-agent/nested-leaf.md) |
| **nested-queen-leaf** | Tier-2 leaf — bottom of a queen-led tree. Deliberately no Task tool (least-privilege), but DOES record trajectory steps, AIDefence-scan its own inbound promp... | [`plugins/orchestration-agent/nested-queen-leaf.md`](./plugins/orchestration-agent/nested-queen-leaf.md) |
| **nested-queen-researcher** | Tier-2 recursive researcher — nested-researcher's role with HNSW pattern retrieval, AIDefence-gated web content, hive-mind consensus on which followups to pu... | [`plugins/orchestration-agent/nested-queen-researcher.md`](./plugins/orchestration-agent/nested-queen-researcher.md) |
| **nested-queen-reviewer** | Tier-2 recursive reviewer — find-and-verify like nested-reviewer, but with hive-mind byzantine consensus on findings (replaces inline majority voting), AIDef... | [`plugins/orchestration-agent/nested-queen-reviewer.md`](./plugins/orchestration-agent/nested-queen-reviewer.md) |
| **nested-queen** | Heavyweight nested orchestrator — wires Claude Code's depth=5 nesting onto orchestration's hive-mind, swarm, intelligence pipeline, claims/AuthScope, AIDefence, and ... | [`plugins/orchestration-agent/nested-queen.md`](./plugins/orchestration-agent/nested-queen.md) |
| **nested-researcher** | Recursive research orchestrator — fans out into sub-research branches when an investigation deepens, keeping each branch in its own context window | [`plugins/orchestration-agent/nested-researcher.md`](./plugins/orchestration-agent/nested-researcher.md) |
| **nested-reviewer** | Recursive review orchestrator — each finding can spawn an adversarial verifier in its own context, so review remains thorough without bloating the top-level ... | [`plugins/orchestration-agent/nested-reviewer.md`](./plugins/orchestration-agent/nested-reviewer.md) |
| **wasm-specialist** | WASM sandbox specialist for creating, managing, and sharing isolated agent environments | [`plugins/orchestration-agent/wasm-specialist.md`](./plugins/orchestration-agent/wasm-specialist.md) |

### orchestration-agentdb

| Agent | Description | File |
|---|---|---|
| **agentdb-specialist** | AgentDB and RuVector specialist for memory operations, HNSW indexing, RaBitQ quantization, and semantic search across the controller bridge | [`plugins/orchestration-agentdb/agentdb-specialist.md`](./plugins/orchestration-agentdb/agentdb-specialist.md) |

### orchestration-aidefence

| Agent | Description | File |
|---|---|---|
| **safety-specialist** | AI safety specialist for threat detection, PII scanning, and adaptive defense training | [`plugins/orchestration-aidefence/safety-specialist.md`](./plugins/orchestration-aidefence/safety-specialist.md) |

### orchestration-autopilot

| Agent | Description | File |
|---|---|---|
| **autopilot-coordinator** | Autonomous task completion coordinator using /loop and autopilot MCP tools | [`plugins/orchestration-autopilot/autopilot-coordinator.md`](./plugins/orchestration-autopilot/autopilot-coordinator.md) |

### orchestration-browser

| Agent | Description | File |
|---|---|---|
| **browser-agent** | Browser automation agent — drives Playwright via 23 MCP tools, captures every session as an RVF container with a ruvector trajectory, and gates content throu... | [`plugins/orchestration-browser/browser-agent.md`](./plugins/orchestration-browser/browser-agent.md) |

### orchestration-core

| Agent | Description | File |
|---|---|---|
| **coder** | Implementation specialist for writing clean, efficient code following project patterns | [`plugins/orchestration-core/coder.md`](./plugins/orchestration-core/coder.md) |
| **researcher** | Pathfinder research specialist — traverses RuVector memory graphs and codebase to surface patterns, dependencies, and prior art | [`plugins/orchestration-core/researcher.md`](./plugins/orchestration-core/researcher.md) |
| **reviewer** | Code review specialist for quality, security, and best-practice enforcement | [`plugins/orchestration-core/reviewer.md`](./plugins/orchestration-core/reviewer.md) |
| **witness-curator** | Maintains the cryptographically-signed witness manifest. Adds new fix entries when shipping a release, regenerates the signed manifest + temporal history, id... | [`plugins/orchestration-core/witness-curator.md`](./plugins/orchestration-core/witness-curator.md) |

### orchestration-cost-tracker

| Agent | Description | File |
|---|---|---|
| **cost-analyst** | Tracks token usage per agent and model, computes cost attribution in USD, monitors budgets, and recommends optimizations | [`plugins/orchestration-cost-tracker/cost-analyst.md`](./plugins/orchestration-cost-tracker/cost-analyst.md) |

### orchestration-daa

| Agent | Description | File |
|---|---|---|
| **daa-specialist** | Dynamic Agentic Architecture specialist for adaptive agents, cognitive patterns, and knowledge sharing | [`plugins/orchestration-daa/daa-specialist.md`](./plugins/orchestration-daa/daa-specialist.md) |

### orchestration-ddd

| Agent | Description | File |
|---|---|---|
| **domain-modeler** | Domain-Driven Design specialist -- maps domains to bounded contexts, designs aggregate roots, defines domain events, and generates anti-corruption layers | [`plugins/orchestration-ddd/domain-modeler.md`](./plugins/orchestration-ddd/domain-modeler.md) |

### orchestration-docs

| Agent | Description | File |
|---|---|---|
| **docs-writer** | Documentation specialist -- generates and maintains project documentation | [`plugins/orchestration-docs/docs-writer.md`](./plugins/orchestration-docs/docs-writer.md) |

### orchestration-federation

| Agent | Description | File |
|---|---|---|
| **federation-coordinator** | Orchestrates cross-installation agent federation with zero-trust security | [`plugins/orchestration-federation/federation-coordinator.md`](./plugins/orchestration-federation/federation-coordinator.md) |

### orchestration-goals

| Agent | Description | File |
|---|---|---|
| **deep-researcher** | Multi-source research specialist that gathers, cross-references, and synthesizes information with evidence grading and contradiction resolution | [`plugins/orchestration-goals/deep-researcher.md`](./plugins/orchestration-goals/deep-researcher.md) |
| **dossier-investigator** | Recursive parallel multi-source investigator that fans out across web, memory, knowledge-graph, codebase, and ADR index to build a graph-structured dossier o... | [`plugins/orchestration-goals/dossier-investigator.md`](./plugins/orchestration-goals/dossier-investigator.md) |
| **goal-planner** | GOAP specialist that creates optimal action plans using A* search through state spaces, with adaptive replanning, trajectory learning, and multi-mode execution | [`plugins/orchestration-goals/goal-planner.md`](./plugins/orchestration-goals/goal-planner.md) |
| **horizon-tracker** | Long-horizon objective tracker that persists progress across sessions with milestone checkpoints, drift detection, and adaptive timeline management | [`plugins/orchestration-goals/horizon-tracker.md`](./plugins/orchestration-goals/horizon-tracker.md) |

### orchestration-intelligence

| Agent | Description | File |
|---|---|---|
| **intelligence-specialist** | Self-learning intelligence specialist — drives the 4-step pipeline (RETRIEVE → JUDGE → DISTILL → CONSOLIDATE) across 29 MCP tools, coordinates with orchestration-age... | [`plugins/orchestration-intelligence/intelligence-specialist.md`](./plugins/orchestration-intelligence/intelligence-specialist.md) |

### orchestration-iot-cognitum

| Agent | Description | File |
|---|---|---|
| **device-coordinator** | Manages Cognitum Seed device fleet as Orchestration agent swarm members with 5-tier trust scoring | [`plugins/orchestration-iot-cognitum/device-coordinator.md`](./plugins/orchestration-iot-cognitum/device-coordinator.md) |
| **fleet-manager** | Manages device fleets, firmware rollouts, and fleet-wide policies | [`plugins/orchestration-iot-cognitum/fleet-manager.md`](./plugins/orchestration-iot-cognitum/fleet-manager.md) |
| **telemetry-analyzer** | Analyzes Cognitum Seed device telemetry for anomalies using Z-score detection | [`plugins/orchestration-iot-cognitum/telemetry-analyzer.md`](./plugins/orchestration-iot-cognitum/telemetry-analyzer.md) |
| **witness-auditor** | Verifies Ed25519 witness chain integrity and detects provenance gaps | [`plugins/orchestration-iot-cognitum/witness-auditor.md`](./plugins/orchestration-iot-cognitum/witness-auditor.md) |

### orchestration-jujutsu

| Agent | Description | File |
|---|---|---|
| **git-specialist** | Git workflow specialist for diff analysis, risk assessment, and PR management | [`plugins/orchestration-jujutsu/git-specialist.md`](./plugins/orchestration-jujutsu/git-specialist.md) |

### orchestration-knowledge-graph

| Agent | Description | File |
|---|---|---|
| **graph-navigator** | Extracts entities and relations from code and docs, builds knowledge graphs, and traverses them with pathfinder scoring | [`plugins/orchestration-knowledge-graph/graph-navigator.md`](./plugins/orchestration-knowledge-graph/graph-navigator.md) |

### orchestration-loop-workers

| Agent | Description | File |
|---|---|---|
| **loop-worker-coordinator** | Coordinates background worker scheduling, health monitoring, and dispatch across loop and cron execution modes | [`plugins/orchestration-loop-workers/loop-worker-coordinator.md`](./plugins/orchestration-loop-workers/loop-worker-coordinator.md) |

### orchestration-market-data

| Agent | Description | File |
|---|---|---|
| **data-engineer** | Ingests market data feeds, normalizes OHLCV vectors, and performs HNSW-indexed candlestick pattern matching | [`plugins/orchestration-market-data/data-engineer.md`](./plugins/orchestration-market-data/data-engineer.md) |

### orchestration-migrations

| Agent | Description | File |
|---|---|---|
| **migration-engineer** | Generates sequential database migrations with up/down pairs, dry-run validation, and rollback safety checks | [`plugins/orchestration-migrations/migration-engineer.md`](./plugins/orchestration-migrations/migration-engineer.md) |

### orchestration-neural-trader

| Agent | Description | File |
|---|---|---|
| **backtest-engineer** | Backtesting specialist using npx neural-trader Rust/NAPI engine — walk-forward validation, Monte Carlo simulation, parameter optimization. Orthogonal researc... | [`plugins/orchestration-neural-trader/backtest-engineer.md`](./plugins/orchestration-neural-trader/backtest-engineer.md) |
| **market-analyst** | Market regime detection and technical analysis using npx neural-trader — RSI, MACD, Bollinger Bands, volume profile, regime classification. Pipeline entry po... | [`plugins/orchestration-neural-trader/market-analyst.md`](./plugins/orchestration-neural-trader/market-analyst.md) |
| **risk-analyst** | Portfolio risk assessment and position sizing using npx neural-trader — VaR/CVaR, Kelly criterion, circuit breakers, correlation monitoring. Pipeline BLOCKIN... | [`plugins/orchestration-neural-trader/risk-analyst.md`](./plugins/orchestration-neural-trader/risk-analyst.md) |
| **trading-strategist** | Designs and optimizes neural trading strategies using npx neural-trader — LSTM/Transformer models, Rust/NAPI backtesting, Z-score anomaly detection. Pipeline... | [`plugins/orchestration-neural-trader/trading-strategist.md`](./plugins/orchestration-neural-trader/trading-strategist.md) |

### orchestration-observability

| Agent | Description | File |
|---|---|---|
| **observability-engineer** | Implements structured logging, distributed tracing, and metrics collection to correlate agent swarm activity with application telemetry | [`plugins/orchestration-observability/observability-engineer.md`](./plugins/orchestration-observability/observability-engineer.md) |

### orchestration-plugin-creator

| Agent | Description | File |
|---|---|---|
| **plugin-developer** | Plugin development specialist for scaffolding, validating, and publishing Claude Code plugins | [`plugins/orchestration-plugin-creator/plugin-developer.md`](./plugins/orchestration-plugin-creator/plugin-developer.md) |

### orchestration-rag-memory

| Agent | Description | File |
|---|---|---|
| **memory-specialist** | SOTA RAG memory specialist — hybrid search (sparse+dense), Graph RAG multi-hop retrieval, MMR diversity reranking, smart consolidation, ruvector integration | [`plugins/orchestration-rag-memory/memory-specialist.md`](./plugins/orchestration-rag-memory/memory-specialist.md) |

### orchestration-ruvector

| Agent | Description | File |
|---|---|---|
| **vector-engineer** | Vector operations specialist using npx ruvector@0.2.25 — HNSW indexing, adaptive LoRA embeddings, code-graph clustering, hooks routing, brain/SONA, 103 MCP t... | [`plugins/orchestration-ruvector/vector-engineer.md`](./plugins/orchestration-ruvector/vector-engineer.md) |

### orchestration-ruvllm

| Agent | Description | File |
|---|---|---|
| **llm-specialist** | RuVLLM specialist for local inference configuration, MicroLoRA fine-tuning, and multi-provider routing | [`plugins/orchestration-ruvllm/llm-specialist.md`](./plugins/orchestration-ruvllm/llm-specialist.md) |

### orchestration-rvf

| Agent | Description | File |
|---|---|---|
| **session-specialist** | Session persistence specialist for state management, memory transfer, and cross-conversation continuity | [`plugins/orchestration-rvf/session-specialist.md`](./plugins/orchestration-rvf/session-specialist.md) |

### orchestration-security-audit

| Agent | Description | File |
|---|---|---|
| **security-auditor** | Specialized agent for security auditing and vulnerability remediation | [`plugins/orchestration-security-audit/security-auditor.md`](./plugins/orchestration-security-audit/security-auditor.md) |

### orchestration-sparc

| Agent | Description | File |
|---|---|---|
| **sparc-orchestrator** | Orchestrates the 5-phase SPARC methodology (Specification, Pseudocode, Architecture, Refinement, Completion) with quality gates between each phase, spawning ... | [`plugins/orchestration-sparc/sparc-orchestrator.md`](./plugins/orchestration-sparc/sparc-orchestrator.md) |

### orchestration-swarm

| Agent | Description | File |
|---|---|---|
| **architect** | System architect for designing implementation approaches, API contracts, and module boundaries | [`plugins/orchestration-swarm/architect.md`](./plugins/orchestration-swarm/architect.md) |
| **coordinator** | Swarm coordinator that manages agent lifecycle, task assignment, and anti-drift enforcement | [`plugins/orchestration-swarm/coordinator.md`](./plugins/orchestration-swarm/coordinator.md) |

### orchestration-testgen

| Agent | Description | File |
|---|---|---|
| **tester** | Specialized testing agent -- writes comprehensive tests using TDD London School | [`plugins/orchestration-testgen/tester.md`](./plugins/orchestration-testgen/tester.md) |

### orchestration-workflows

| Agent | Description | File |
|---|---|---|
| **gaia-benchmark-runner** | Specialized agent for executing GAIA benchmark runs, monitoring progress, and analyzing results | [`plugins/orchestration-workflows/gaia-benchmark-runner.md`](./plugins/orchestration-workflows/gaia-benchmark-runner.md) |
| **gaia-submission-coordinator** | Specialized agent for packaging, signing, and coordinating HAL leaderboard submission of GAIA benchmark results | [`plugins/orchestration-workflows/gaia-submission-coordinator.md`](./plugins/orchestration-workflows/gaia-submission-coordinator.md) |
| **workflow-specialist** | Workflow automation specialist for creating, executing, and managing multi-step processes | [`plugins/orchestration-workflows/workflow-specialist.md`](./plugins/orchestration-workflows/workflow-specialist.md) |

