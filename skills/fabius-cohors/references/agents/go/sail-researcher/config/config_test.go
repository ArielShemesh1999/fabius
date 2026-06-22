package config

import (
	"testing"
)

func TestNew(t *testing.T) {
	tests := []struct {
		name    string
		env     map[string]string
		want    *Config
		wantErr bool
	}{
		{
			name: "All required fields set",
			env: map[string]string{
				"GOOGLE_MAPS_KEY":      "maps-key",
				"GEMINI_API_KEY":       "gemini-key",
				"GOOGLE_CLOUD_PROJECT": "my-project",
			},
			want: &Config{
				Env:          DefaultEnv, // Default
				Project:      "my-project",
				ModelName:    DefaultModelName, // Default
				GeminiAPIKey: "gemini-key",
				MapsAPIKey:   "maps-key",
				Port:         DefaultPort, // Default
			},
			wantErr: false,
		},
		{
			name: "All fields set including defaults",
			env: map[string]string{
				"GOOGLE_MAPS_KEY":      "maps-key",
				"GEMINI_API_KEY":       "gemini-key",
				"GOOGLE_CLOUD_PROJECT": "my-project",
				"ENV":                  "production",
				"MODEL":                "gemini-ultra",
				"PORT":                 "9000",
			},
			want: &Config{
				Env:          "production",
				Project:      "my-project",
				ModelName:    "gemini-ultra",
				GeminiAPIKey: "gemini-key",
				MapsAPIKey:   "maps-key",
				Port:         "9000",
			},
			wantErr: false,
		},
		{
			name: "Missing GOOGLE_MAPS_KEY",
			env: map[string]string{
				"GEMINI_API_KEY":       "gemini-key",
				"GOOGLE_CLOUD_PROJECT": "my-project",
			},
			want:    nil,
			wantErr: true,
		},
		{
			name: "Missing GEMINI_API_KEY",
			env: map[string]string{
				"GOOGLE_MAPS_KEY":      "maps-key",
				"GOOGLE_CLOUD_PROJECT": "my-project",
			},
			want:    nil,
			wantErr: true,
		},
		{
			name: "Missing GOOGLE_CLOUD_PROJECT",
			env: map[string]string{
				"GOOGLE_MAPS_KEY": "maps-key",
				"GEMINI_API_KEY":  "gemini-key",
			},
			want:    nil,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			getEnv := func(key string) string {
				return tt.env[key]
			}

			got, err := New(getEnv)
			if (err != nil) != tt.wantErr {
				t.Errorf("New() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				if got.Env != tt.want.Env {
					t.Errorf("New() Env = %v, want %v", got.Env, tt.want.Env)
				}
				if got.Project != tt.want.Project {
					t.Errorf("New() Project = %v, want %v", got.Project, tt.want.Project)
				}
				if got.ModelName != tt.want.ModelName {
					t.Errorf("New() ModelName = %v, want %v", got.ModelName, tt.want.ModelName)
				}
				if got.GeminiAPIKey != tt.want.GeminiAPIKey {
					t.Errorf("New() GeminiAPIKey = %v, want %v", got.GeminiAPIKey, tt.want.GeminiAPIKey)
				}
				if got.MapsAPIKey != tt.want.MapsAPIKey {
					t.Errorf("New() MapsAPIKey = %v, want %v", got.MapsAPIKey, tt.want.MapsAPIKey)
				}
				if got.Port != tt.want.Port {
					t.Errorf("New() Port = %v, want %v", got.Port, tt.want.Port)
				}
			}
		})
	}
}
