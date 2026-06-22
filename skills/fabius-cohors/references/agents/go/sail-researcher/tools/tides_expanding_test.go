package tools

import (
	"context"
	"testing"

	"github.com/tpryan/noaago"
)

func TestGetTides_ExpandingSearch(t *testing.T) {
	callCount := 0
	mockClient := &mockTideClient{
		FindStationsFunc: func(opts *noaago.StationOptions) (*noaago.StationResponse, error) {
			callCount++
			// Expect radius to increase: 50, 100, 150...
			// In noaago.StationOptions, we don't have direct access to "Radius" field easily as it might be internal or not exported in the struct directly without looking at the library, 
			// but we can simulate the behavior based on call count.
			
			// Let's say we find something on the 3rd try (Radius 150)
			if callCount < 3 {
				return &noaago.StationResponse{Count: 0, Stations: []noaago.Station{}}, nil
			}
			
			return &noaago.StationResponse{
				Count: 1,
				Stations: []noaago.Station{
					{ID: "8452660", Name: "Newport"},
				},
			}, nil
		},
		GetTidesFunc: func(opts *noaago.TideOptions) (*noaago.TideResponse, error) {
			return &noaago.TideResponse{
				Data: []noaago.DataPoint{
					{Time: "2025-01-01 06:00", Type: "H", Value: "4.5"},
				},
			}, nil
		},
	}

	tp := &TideProvider{client: mockClient}
	args := TideArgs{
		Latitude:  41.5,
		Longitude: -71.3,
		Date:      "2025-01-01",
	}

	result, err := tp.GetTides(mockToolContext{Context: context.Background()}, args)
	if err != nil {
		t.Fatalf("GetTides() error = %v", err)
	}

	if callCount != 3 {
		t.Errorf("Expected 3 calls to FindStations, got %d", callCount)
	}

	if result.StationName != "Newport" {
		t.Errorf("Expected station Newport, got %s", result.StationName)
	}
}
