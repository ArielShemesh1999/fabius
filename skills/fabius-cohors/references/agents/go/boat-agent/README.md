# Boat Agent

This is a simple sailboat information agent built using the [Agent Development Kit
(ADK)](https://google.github.io/adk-docs/). It uses the Gemini model to gather and
format technical specifications for sailboats, such as length, beam, draft, and
mast height. It also forces the output to be json, for consumption by another
application.  This pattern allows for this agent to be incorporated into a REST
based applicaiton. 


<figure>
  <img src="demo.gif" alt="Demo">
  <figcaption>Example of the agent encorporated into a traditional web form.</figcaption>
</figure>


## Features

- **Simple Agent Logic**: Uses `llmagent` to define an agent with a specific
  role and set of tools.
- **Google Search Integration**: Equipped with `geminitool.GoogleSearch` to find
  missing information online.
- **Standard Go HTTP Server**: Instead of using the default ADK launcher, this
  project demonstrates how to integrate ADK into a standard `net/http` server.
- **Embedded Instructions**: Uses Go's `//go:embed` directive to keep agent
  instructions in a separate, readable Markdown file.
- **Advanced Logging**: Uses `charmbracelet/log` for beautiful, structured
  logging with custom styling for long-running requests.

## Embedded Instructions Pattern

To keep the codebase clean and the agent's behavior easy to manage, the
instructions are stored in `instruction.md`. This file is embedded into the
binary at compile time:

```go
//go:embed instruction.md
var instruction string

// ...

boatAgent, err := llmagent.New(llmagent.Config{
    // ...
    Instruction: instruction,
    // ...
})
```

This pattern allows you to leverage Markdown formatting for complex instructions
without cluttering your Go source code with long string literals.

## Prerequisites

- Go 1.25 or later
- A Google Gemini API Key

## Setup

1. Clone the repository.
2. Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   GEMINI_MODEL_NAME=gemini-2.5-flash
   PORT=8081
   ```
3. Install dependencies:
   ```bash
   go mod tidy
   ```

## Running the Agent

Start the server:

```bash
go run main.go
```

The server will start on the configured port (default `8081`).

## API Usage

The agent exposes a REST API via the ADK. Interacting with the agent involves
creating a session and then sending messages to it.

### 1. Create a Session

First, initialize a session for a specific user and agent:

```bash
curl -X POST http://localhost:8081/api/apps/boat_agent/users/testuser/sessions/testsession
```

### 2. Send a Message

Send a query to the agent using the session IDs created above:

```bash
curl -X POST http://localhost:8081/api/run \
  -H "Content-Type: application/json" \
  -d 
    "{
    "appName": "boat_agent",
    "userId": "testuser",
    "sessionId": "testsession",
    "newMessage": {
        "role": "user",
        "parts": [{"text": "Tell me about the Catalina 30"}]
    }
  }"
```

## Project Structure

- `main.go`: Entry point, server setup, and agent configuration.
- `instruction.md`: The system prompt and instructions for the agent.
- `test_scripts/`: Contains utility scripts for testing the agent's API.

```
