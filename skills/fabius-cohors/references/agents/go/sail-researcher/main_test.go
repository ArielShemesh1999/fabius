package main

import (
	"context"
	"os"
	"testing"

	"github.com/tpryan/navalplan/services/researcher/config"
)

func TestCreateResearcherAgent(t *testing.T) {
	// Use a mock model if possible, or just check configuration
	// For now, let's see if it instantiates without error (requires API key if real)

	modelName := config.DefaultModelName
	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping agent creation test because GEMINI_API_KEY is not set")
	}

	mapsKey := os.Getenv("MAPS_API_KEY")
	if mapsKey == "" {
		mapsKey = "dummy-key"
	}

	cfg := &config.Config{
		ModelName:    modelName,
		GeminiAPIKey: apiKey,
		MapsAPIKey:   mapsKey,
	}

	srv := &Server{
		config: cfg,
	}

	researcherTools, err := srv.setupTools(context.Background())
	if err != nil {
		t.Fatalf("Failed to setup tools: %v", err)
	}

	toolMonitor := NewToolMonitor()

	a, err := NewStopAgent(context.Background(), cfg, toolMonitor, researcherTools)
	if err != nil {
		t.Fatalf("Failed to create researcher agent: %v", err)
	}

	if a.Name() != "researcher_agent" {
		t.Errorf("Expected agent name researcher_agent, got %s", a.Name())
	}
}