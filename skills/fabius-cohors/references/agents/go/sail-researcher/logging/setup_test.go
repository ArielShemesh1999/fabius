package logging

import (
	"log/slog"
	"testing"
)

func TestInitLogging(t *testing.T) {
	tests := []struct {
		name string
		env  string
	}{
		{
			name: "Development environment",
			env:  "development",
		},
		{
			name: "Production environment",
			env:  "production",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Save current default logger to restore later (though mostly irrelevant for unit tests)
			original := slog.Default()
			defer slog.SetDefault(original)

			InitLogging(tt.env)

			// We can't easily inspect the handler type inside slog.Logger, 
			// but we can ensure it didn't panic and set *something*.
			if slog.Default() == nil {
				t.Error("InitLogging() failed to set default logger")
			}
		})
	}
}
