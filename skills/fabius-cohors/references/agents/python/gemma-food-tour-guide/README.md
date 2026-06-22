# Gemma Food Tour Agent

**by [Smitha Kolan](https://github.com/smithakolan)**

This directory contains a sample ADK agent that builds personalized food tours using the Gemma 4 31b model and Google Maps MCP. Given a dish photo or text description, a location, and an optional budget, the agent identifies the cuisine, finds relevant places, creates a walking route, and recommends what to order at each stop.

## Prerequisites
- Enable [Google Maps API](https://console.cloud.google.com/maps-api/) on Google Cloud Console.
- Create a [Google Maps Platform API key](https://console.cloud.google.com/maps-api/credentials).   
- Create a Google AI Studio API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
- [ADK](https://adk.dev) installed and configured in your Python environment

## Setup Instructions

1. **Clone the sample repository**
   ```bash
   git clone https://github.com/ArielShemesh1999/fabius
   ```
2. **Navigate to the sample directory**
   ```bash
   cd adk-samples/python/agents/gemma-food-tour-guide
   ```
3. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```
4. **Activate the virtual environment**
   ```bash
   source .venv/bin/activate
   ```
5. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure Environment Variables**
   Rename `.env.example` to `.env` and fill in your keys:
   - `MAPS_API_KEY`: Your Google Maps API Key
   - `GEMINI_API_KEY`: Your API Key from AI Studio

## Running the Agent

Run the ADK web interface from the root `gemma-food-tour-guide` folder:
```bash
# Ensure you are in the root food_tour_agent directory
adk web
```

Then follow the link to chat with the agent! Give it an image or description of food, a location, and a budget.

## Sample Prompts

To test out the capabilities of the Food Tour Agent, try pasting one of these prompts into the chat:

- *"I want to do a ramen tour in Toronto. My budget is $60 for the day. Give me a walking route for the top 3 spots and tell me what I should order at each."*
- *"I have this photo of a deep dish pizza [insert image URL]. I want to find the best places for this around Navy Pier in Chicago. Structure a walking tour and tell me what the must-have slice is at each stop."*
- *"I'm in Downtown Austin looking for an authentic BBQ tour. Let's keep the budget under $100. Build a walking route between 3 highly-rated spots and give me insider tips on the best cuts of meat to get."*

## What this sample demonstrates
This sample shows how to:
- Use Gemma 4 31b with ADK through the Google AI Studio API
- Connect an ADK agent to Google Maps MCP tools
- Use tool calling to search for places and build routes
- Generate grounded, structured food tour recommendations from Text or Image based input

## Implementation notes
The agent is configured to:
- use `search_places` to find relevant restaurants, stalls, or cafes
- use `compute_routes` to create a walking-optimized itinerary
- rely only on exact `place_id`values or `lat_lng` objects returned by tools when building routes
- avoid inventing addresses or place identifiers that were not returned by the tools

This helps reduce hallucinations and keeps route generation grounded in tool output.