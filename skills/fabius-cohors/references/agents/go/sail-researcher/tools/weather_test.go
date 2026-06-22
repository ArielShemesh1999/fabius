package tools

import (
	"context"
	"fmt"
	"testing"

	"github.com/tpryan/openmeteogo"
)

// mockWeatherClient is a mock implementation of the WeatherClient interface.
type mockWeatherClient struct {
	GetFunc func(opts *openmeteogo.Options) (*openmeteogo.WeatherData, error)
}

func (m *mockWeatherClient) Get(opts *openmeteogo.Options) (*openmeteogo.WeatherData, error) {
	if m.GetFunc != nil {
		return m.GetFunc(opts)
	}
	return nil, nil
}

func TestDegreesToDirection(t *testing.T) {
	tests := []struct {
		deg  float64
		want string
	}{
		{0, "N"},
		{22.5, "NNE"},
		{45, "NE"},
		{90, "E"},
		{180, "S"},
		{270, "W"},
		{350, "N"}, // 350 is close to 360/0
		{337.5, "NNW"},
		{11.24, "N"},
		{11.26, "NNE"},
	}

	for _, tt := range tests {
		t.Run(string(rune(tt.deg)), func(t *testing.T) {
			if got := DegreesToDirection(tt.deg); got != tt.want {
				t.Errorf("DegreesToDirection(%v) = %v, want %v", tt.deg, got, tt.want)
			}
		})
	}
}

func TestNewWeatherTool(t *testing.T) {
	tool, _, err := NewWeatherTool()
	if err != nil {
		t.Fatalf("NewWeatherTool() error = %v", err)
	}

	if tool.Name() != "get_weather_forecast" {
		t.Errorf("NewWeatherTool().Name() = %v, want %v", tool.Name(), "get_weather_forecast")
	}
}

func TestGetWeatherForecast_Success(t *testing.T) {
	mockClient := &mockWeatherClient{
		GetFunc: func(opts *openmeteogo.Options) (*openmeteogo.WeatherData, error) {
			// Check if marine or weather request based on metrics
			// This is a simplified check
			
			return &openmeteogo.WeatherData{
				Daily: openmeteogo.Daily{
					Time:                   []string{"2025-01-01"},
					WeatherCode:            []int{1}, // Main Clear
					Temperature2mMax:       []float64{75.0},
					Temperature2mMin:       []float64{65.0},
					WindSpeed10mMax:        []float64{15.0},
					WindGusts10mMax:        []float64{20.0},
					WindDirection10mDominant: []int{90},
					PrecipitationSum:       []float64{0.1},
					WaveHeightMax:          []float64{1.5}, // 1.5m ~ 4.9ft
					WaveDirectionDominant:  []float64{180.0},
					WavePeriodMax:          []float64{8.0},
				},
			}, nil
		},
	}

	wp := &WeatherProvider{client: mockClient}
	args := WeatherArgs{
		Latitude:  10.0,
		Longitude: 20.0,
		Date:      "2025-01-01",
	}

	result, err := wp.GetWeatherForecast(mockToolContext{Context: context.Background()}, args)
	if err != nil {
		t.Fatalf("GetWeatherForecast() error = %v", err)
	}

	if result.MaxTemp != 75.0 {
		t.Errorf("Expected MaxTemp 75.0, got %f", result.MaxTemp)
	}
	// 1.5 meters * 3.28084 = 4.92126
	if result.WaveHeight < 4.9 || result.WaveHeight > 5.0 {
		t.Errorf("Expected WaveHeight ~4.92, got %f", result.WaveHeight)
	}
}

func TestGetWeatherForecast_InvalidDate(t *testing.T) {
	args := WeatherArgs{
		Latitude:  41.497,
		Longitude: -71.362,
		Date:      "invalid",
	}

	wp := &WeatherProvider{client: &mockWeatherClient{}}
	_, err := wp.GetWeatherForecast(mockToolContext{Context: context.Background()}, args)
	if err == nil {
		t.Error("Expected error for invalid date, got none")
	}
}

func TestGetWeatherForecast_APIError(t *testing.T) {
	mockClient := &mockWeatherClient{
		GetFunc: func(opts *openmeteogo.Options) (*openmeteogo.WeatherData, error) {
			return nil, fmt.Errorf("API error")
		},
	}

	wp := &WeatherProvider{client: mockClient}
	args := WeatherArgs{
		Latitude:  10.0,
		Longitude: 20.0,
		Date:      "2025-01-01",
	}

	_, err := wp.GetWeatherForecast(mockToolContext{Context: context.Background()}, args)
	if err == nil {
		t.Error("Expected error for API error, got none")
	}
}