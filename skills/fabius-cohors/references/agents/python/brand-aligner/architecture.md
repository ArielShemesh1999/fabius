# Brand Aligner Agent Architecture

This document provides a visual representation of the Brand Aligner agent's consolidated, in-process architecture.

The agent's logic is self-contained. The backend services (`GuidelineService`, `EvalService`) run as part of the agent's own process, and the agent's tools invoke these services directly without making network calls.

```mermaid
graph TD
    subgraph User Interaction
        User
    end

    subgraph AGENT_PROCESS [Agent Process]
        style AGENTS fill:#d4edff,stroke:#333,stroke-width:2px
        style TOOLS fill:#e2ffe2,stroke:#333,stroke-width:1px
        style SERVICES fill:#fff0d4,stroke:#333,stroke-width:1px
        style AUTH fill:#ffe6cc,stroke:#333,stroke-width:1px

        subgraph AUTH [Authentication]
            AuthModule["Auth Logic (auth.py)"]
        end

        subgraph AGENTS [ADK Agent Chain]
            Root["brand_aligner_agent (Planner)"]
            GuidelineAgent["guideline_processor_agent"]
            AssetAgent["asset_evaluator_agent"]
            Summarizer["summarizer_agent"]
        end

        subgraph TOOLS [Agent Tools]
            PlanTools["save/search_files_tools"]
            GuidelineTool["guideline_processor_tool"]
            AssetTool["asset_evaluator_tool"]
        end

        subgraph SERVICES [In-Process Services]
            GuidelineService["GuidelineService"]
            EvalService["EvalService"]
        end

        Root -- "1. Handoff" --> GuidelineAgent
        GuidelineAgent -- "2. Handoff" --> AssetAgent
        AssetAgent -- "3. Handoff" --> Summarizer

        Root -- "calls" --> PlanTools
        GuidelineAgent -- "calls (iterative)" --> GuidelineTool
        AssetAgent -- "calls (iterative)" --> AssetTool

        GuidelineTool -- "Invokes" --> GuidelineService
        AssetTool -- "Invokes" --> EvalService

        TOOLS -.-> AuthModule
    end


    subgraph CLOUD [Google Cloud]
        style GCS fill:#f8d7da,stroke:#333,stroke-width:1px
        style GenModels fill:#f8d7da,stroke:#333,stroke-width:1px
        GCS["Google Cloud Storage </br> (Artifacts, Files)"]
        GenModels["Generative Models </br> (Gemini, Vertex AI Eval)"]
    end

    %% --- Connections ---

    User -- "Interacts" --> Root
    PlanTools -- "Reads/Writes" --> GCS

    GuidelineService -- "Reads Docs" --> GCS
    GuidelineService -- "Extracts Criteria" --> GenModels

    EvalService -- "Reads Assets" --> GCS
    EvalService -- "Evaluates" --> GenModels

    Summarizer -- "Final Response" --> User

    style CLOUD fill:#e3f2fd,stroke:#333,stroke-width:2px
```
