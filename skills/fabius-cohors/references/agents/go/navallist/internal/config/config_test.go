package config

import (
	"testing"
)

func TestDSN(t *testing.T) {
	tests := []struct {
		name     string
		db       DBConfig
		expected string
	}{
		{
			name: "Host and Port",
			db: DBConfig{
				User:     "user",
				Password: "password",
				Host:     "localhost",
				Port:     "5432",
				Name:     "dbname",
				SSLMode:  "disable",
			},
			expected: "postgres://user:password@localhost:5432/dbname?sslmode=disable",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.db.DSN(); got != tt.expected {
				t.Errorf("DSN() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestLoad(t *testing.T) {
	tests := []struct {
		name     string
		env      map[string]string
		validate func(*testing.T, *Config)
	}{
		{
			name: "Defaults",
			env:  map[string]string{},
			validate: func(t *testing.T, cfg *Config) {
				if cfg.Port != "8080" {
					t.Errorf("Default Port = %v, want 8080", cfg.Port)
				}
				if cfg.DB.User != "navallist_user" {
					t.Errorf("Default DB User = %v, want navallist_user", cfg.DB.User)
				}
			},
		},
		{
			name: "Env Overrides",
			env: map[string]string{
				"NAVALLIST_PORT":      "9090",
				"NAVALLIST_DB_USER":   "test_user",
				"NAVALLIST_OA_CLIENT": "client_id",
			},
			validate: func(t *testing.T, cfg *Config) {
				if cfg.Port != "9090" {
					t.Errorf("Port = %v, want 9090", cfg.Port)
				}
				if cfg.DB.User != "test_user" {
					t.Errorf("DB User = %v, want test_user", cfg.DB.User)
				}
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mockEnv := func(key string) (string, bool) {
				val, ok := tt.env[key]
				return val, ok
			}

			cfg, err := Load(mockEnv)
			if err != nil {
				t.Fatalf("Load() error = %v", err)
			}
			tt.validate(t, cfg)
		})
	}
}
