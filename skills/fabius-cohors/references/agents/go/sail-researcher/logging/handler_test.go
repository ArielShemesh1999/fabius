package logging

import (
	"bytes"
	"context"
	"encoding/json"
	"log/slog"
	"testing"
	"time"
)

func TestCloudLoggingHandler_Handle(t *testing.T) {
	tests := []struct {
		name          string
		formatMessage bool
		traceID       string
		message       string
		attrs         []slog.Attr
		wantMessage   string // Expected message in JSON
		wantTrace     string // Expected trace in JSON
	}{
		{
			name:          "No formatting, no trace",
			formatMessage: false,
			traceID:       "",
			message:       "test message",
			attrs:         []slog.Attr{slog.String("key", "value")},
			wantMessage:   "test message",
			wantTrace:     "",
		},
		{
			name:          "With formatting",
			formatMessage: true,
			traceID:       "",
			message:       "test message",
			attrs:         []slog.Attr{slog.String("key", "value"), slog.Int("count", 42)},
			wantMessage:   "test message key=value count=42",
			wantTrace:     "",
		},
		{
			name:          "With trace",
			formatMessage: false,
			traceID:       "projects/my-project/traces/12345",
			message:       "trace test",
			attrs:         nil,
			wantMessage:   "trace test",
			wantTrace:     "projects/my-project/traces/12345",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var buf bytes.Buffer
			// Use JSONHandler as the underlying handler
			jsonHandler := slog.NewJSONHandler(&buf, nil)
			
			h := &CloudLoggingHandler{
				Handler:       jsonHandler,
				FormatMessage: tt.formatMessage,
			}

			ctx := context.Background()
			if tt.traceID != "" {
				ctx = AddTraceToContext(ctx, tt.traceID)
			}

			r := slog.NewRecord(time.Now(), slog.LevelInfo, tt.message, 0)
			r.AddAttrs(tt.attrs...)

			if err := h.Handle(ctx, r); err != nil {
				t.Fatalf("Handle() error = %v", err)
			}

			// Parse JSON output
			var logEntry map[string]interface{}
			if err := json.Unmarshal(buf.Bytes(), &logEntry); err != nil {
				t.Fatalf("Failed to parse log output: %v", err)
			}

			if got := logEntry["msg"].(string); got != tt.wantMessage {
				t.Errorf("Handle() message = %q, want %q", got, tt.wantMessage)
			}

			if tt.wantTrace != "" {
				if got, ok := logEntry["logging.googleapis.com/trace"].(string); !ok || got != tt.wantTrace {
					t.Errorf("Handle() trace = %v, want %q", logEntry["logging.googleapis.com/trace"], tt.wantTrace)
				}
			}
		})
	}
}
