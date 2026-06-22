package tools

import (
	"context"
	"fmt"
	"testing"

	placespb "cloud.google.com/go/maps/places/apiv1/placespb"
	"github.com/googleapis/gax-go/v2"
	"google.golang.org/genproto/googleapis/type/latlng"
)

// mockPlacesClient is a mock implementation of the PlacesClient interface.
type mockPlacesClient struct {
	SearchTextFunc func(ctx context.Context, req *placespb.SearchTextRequest, opts ...gax.CallOption) (*placespb.SearchTextResponse, error)
	CloseFunc      func() error
}

func (m *mockPlacesClient) SearchText(ctx context.Context, req *placespb.SearchTextRequest, opts ...gax.CallOption) (*placespb.SearchTextResponse, error) {
	if m.SearchTextFunc != nil {
		return m.SearchTextFunc(ctx, req, opts...)
	}
	return nil, nil
}

func (m *mockPlacesClient) Close() error {
	if m.CloseFunc != nil {
		return m.CloseFunc()
	}
	return nil
}

func TestNewPlacesTool(t *testing.T) {
	tool, _, err := NewPlacesTool(t.Context(), "dummy-key")
	if err != nil {
		t.Fatalf("NewPlacesTool() error = %v", err)
	}

	if tool.Name() != "find_places_nearby" {
		t.Errorf("NewPlacesTool().Name() = %v, want %v", tool.Name(), "find_places_nearby")
	}

	expectedDesc := "Finds places (e.g. marinas, restaurants) near a location using Google Maps Text Search. Returns specific locations with Lat/Lng."
	if tool.Description() != expectedDesc {
		t.Errorf("NewPlacesTool().Description() = %v, want %v", tool.Description(), expectedDesc)
	}
}

func TestFindPlaces_Success(t *testing.T) {
	mockClient := &mockPlacesClient{
		SearchTextFunc: func(ctx context.Context, req *placespb.SearchTextRequest, opts ...gax.CallOption) (*placespb.SearchTextResponse, error) {
			if req.TextQuery != "marina" {
				return nil, fmt.Errorf("unexpected query: %s", req.TextQuery)
			}
			return &placespb.SearchTextResponse{
				Places: []*placespb.Place{
					{
						// DisplayName:      &placespb.LocalizedText{Text: "Test Marina"},
						FormattedAddress: "123 Ocean Dr",
						Location:         &latlng.LatLng{Latitude: 10.0, Longitude: 20.0},
						Rating:           4.5,
						UserRatingCount:  int32Ptr(100),
						BusinessStatus:   placespb.Place_OPERATIONAL,
						Types:            []string{"marina"},
						WebsiteUri:       "http://example.com",
					},
				},
			}, nil
		},
	}

	p := &PlacesProvider{client: mockClient}
	args := PlacesArgs{
		Query:     "marina",
		Latitude:  10.0,
		Longitude: 20.0,
	}

	resp, err := p.FindPlaces(mockToolContext{Context: context.Background()}, args)
	if err != nil {
		t.Fatalf("FindPlaces() error = %v", err)
	}

	if len(resp.Places) != 1 {
		t.Errorf("Expected 1 place, got %d", len(resp.Places))
	}
	if resp.Places[0].Address != "123 Ocean Dr" {
		t.Errorf("Expected place address '123 Ocean Dr', got %s", resp.Places[0].Address)
	}
}

func TestFindPlaces_APIError(t *testing.T) {
	mockClient := &mockPlacesClient{
		SearchTextFunc: func(ctx context.Context, req *placespb.SearchTextRequest, opts ...gax.CallOption) (*placespb.SearchTextResponse, error) {
			return nil, fmt.Errorf("API error")
		},
	}

	p := &PlacesProvider{client: mockClient}
	args := PlacesArgs{Query: "marina"}

	_, err := p.FindPlaces(mockToolContext{Context: context.Background()}, args)
	if err == nil {
		t.Fatal("Expected error, got none")
	}
	if err.Error() != "SearchText API: API error" {
		t.Errorf("Expected 'SearchText API: API error', got %v", err)
	}
}
