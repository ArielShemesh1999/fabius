# Sail Researcher Agent

The Sail Researcher Agent is a multi-agent AI service designed to assist with sailing voyage planning. It leverages Google's **Agent Development Kit (ADK)** and **Gemini** models to provide expert advice on sailing destinations, weather conditions, anchorages, and voyage logistics.

## Architecture

The application is built as a Go web server that orchestrates a team of specialized AI agents:

### Agents

1.  **Discovery Agent ("The Commodore")**:
    *   **Role**: Global Seasonal Discovery Expert.
    *   **Goal**: Identifies regions in their prime sailing season based on the time of year.
    *   **Capabilities**: Suggests destinations (Standard, Hidden Gems, Regional Favorites, Challenging) with sailing suitability scores.

2.  **Voyage Agent ("The Guide")**:
    *   **Role**: Local Knowledge Expert and Sailing Guide.
    *   **Goal**: Provides specific routing and local advice.
    *   **Tools**: Google Search.

3.  **Researcher Agent ("The Harbourmaster")**:
    *   **Role**: Virtual Harbourmaster.
    *   **Goal**: Researches specific stops, anchorages, and marinas.
    *   **Tools**:
        *   **Weather**: Forecasts and marine conditions.
        *   **Tides**: Tide predictions.
        *   **Sunrise/Sunset**: Daylight hours.
        *   **Places**: Finds marinas, restaurants, and facilities using Google Maps.
        *   **Search Specialist**: A sub-agent for finding web information (reviews, facilities).

### Technical Stack

*   **Language**: Go (1.23+)
*   **Framework**: [Google Agent Development Kit (ADK)](https://github.com/googleapis/agent-development-kit)
*   **AI Model**: Google Gemini (via Vertex AI or AI Studio).
*   **APIs**: Google Maps (Places), NOAA/OpenMeteo (Weather/Tides).
*   **Observability**: Structured JSON logging (`log/slog`) and Google Cloud Trace integration.

## Prerequisites

*   Go 1.23 or higher.
*   A Google Cloud Project.
*   API Keys for:
    *   Google Gemini API.
    *   Google Maps API (Places API enabled).

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd sail-researcher
    ```

2.  **Configure Environment**:
    Create a `.env` file in the root directory with the following variables:

    ```env
    # Required
    GOOGLE_CLOUD_PROJECT=your-project-id
    GEMINI_API_KEY=your-gemini-api-key
    GOOGLE_MAPS_KEY=your-google-maps-api-key

    # Optional (Defaults shown)
    PORT=8081
    MODEL=gemini-2.0-flash-001
    ENV=development  # Use 'production' for JSON logging
    ```

## Usage

### Running the Server

Start the agent server:

```bash
go run .
```

Or build and run the binary:

```bash
go build -o server .
./server
```

The server listens on port `8081` (default).

### Interactive Testing

The project includes shell scripts to interact with the agents via the REST API.

1.  **Discovery Test**:
    Asks the Commodore for sailing destinations in a specific month (e.g., September).
    ```bash
    ./test_scripts/test_discovery.sh
    ```

2.  **General Research Test**:
    Asks the Researcher Agent about specific coordinates (e.g., Poets Cove).
    ```bash
    ./test_scripts/test.sh
    ```

## Testing

### Unit Tests

Run the Go unit tests for all packages:

```bash
go test ./...
```

### Integration Testing

The `test_scripts/*.sh` files act as manual integration tests, ensuring the full HTTP flow, session management, and agent execution work as expected against a running server.

## Data Structures

The agents are designed to produce structured JSON outputs. Below are the primary data models used across the system:

### 1. Discovery Data (Sailing Regions)
The **Commodore** identifies prime sailing areas for a given month.
- **Fields**:
  - `name`: Region name (e.g., "Whitsunday Islands").
  - `tier`: Classification (Standard, Hidden Gem, Regional Favorite, Challenging).
  - `suitability_score`: 0-100 rating for sailing conditions.
  - `avg_wind_speed_knots` / `avg_temp_c`: Seasonal averages.
  - `geometry`: A GeoJSON Polygon outlining the area.
  - `summary`: Pitch for the destination.

### 2. Voyage Data (Regional Guide)
The **Guide Agent** provides a high-level briefing for a general area or country.
- **Fields**:
  - `sailing_season`: Primary months, storm risks, and peak periods.
  - `hazards`: Navigation risks like reefs or strong currents.
  - `hubs`: Key marinas and sailing centers.
  - `logistics`: Nearby airports, currency, languages, and emergency numbers.
  - `points_of_interest`: Top nautical sites and landmarks.

### 3. Stop Data (Destination Briefing)
The **Harbourmaster** generates a detailed report for a specific coordinate and date.
- **Fields**:
  - `weather_summary`: Synthesized forecast including wind, waves, and temperature.
  - `sun_phase`: Sunrise and sunset times for the specific location.
  - `tides`: Detailed tide events (High/Low) from the nearest station.
  - `facilities`: Structured list of Anchorages, Marinas, Moorings, and waterfront amenities.
  - `details`: Specifics like protection level, VHF channels, and websites.

## Project Structure

*   `main.go`: Entry point. Sets up the server, middleware, and wires dependencies.
*   `agent_setup.go`: Configures and constructs the ADK agents (prompts, tools, models).
*   `middleware.go`: HTTP middleware for logging and tracing.
*   `tool_monitor.go`: Telemetry helper for tracking tool execution duration.
*   `tools/`: Implementations of Weather, Tide, Places, and Sunrise tools.
*   `config/`: Configuration loading and validation.
*   `logging/`: Structured logging setup and handlers.
*   `prompts/`: Markdown files containing system instructions for the AI agents.
*   `test_scripts/`: Curl-based scripts for testing the API.
