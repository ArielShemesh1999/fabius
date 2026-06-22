package main

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/charmbracelet/log"
)

func TestLoadConfig(t *testing.T) {
	t.Run("Custom values from environment", func(t *testing.T) {
		t.Setenv("PORT", "9090")
		t.Setenv("GEMINI_MODEL_NAME", "test-model")
		t.Setenv("GOOGLE_API_KEY", "test-key")

		cfg := LoadConfig()

		if cfg.Port != "9090" {
			t.Errorf("expected Port 9090, got %s", cfg.Port)
		}
		if cfg.ModelName != "test-model" {
			t.Errorf("expected ModelName test-model, got %s", cfg.ModelName)
		}
		if cfg.GoogleAPIKey != "test-key" {
			t.Errorf("expected GoogleAPIKey test-key, got %s", cfg.GoogleAPIKey)
		}
	})
}

func TestRecoveryMiddleware(t *testing.T) {
	t.Run("Recovers from panic", func(t *testing.T) {
		panickingHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			panic("something went wrong")
		})

		handler := recoveryMiddleware(panickingHandler)

		req := httptest.NewRequest("GET", "/", nil)
		rr := httptest.NewRecorder()

		// This should not panic
		func() {
			defer func() {
				if r := recover(); r != nil {
					t.Errorf("middleware failed to recover from panic: %v", r)
				}
			}()
			handler.ServeHTTP(rr, req)
		}()

		if rr.Code != http.StatusInternalServerError {
			t.Errorf("expected status 500, got %d", rr.Code)
		}
	})

	t.Run("Passes through normal request", func(t *testing.T) {
		normalHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("ok"))
		})

		handler := recoveryMiddleware(normalHandler)

		req := httptest.NewRequest("GET", "/", nil)
		rr := httptest.NewRecorder()

		handler.ServeHTTP(rr, req)

		if rr.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rr.Code)
		}
		if rr.Body.String() != "ok" {
			t.Errorf("expected body 'ok', got %q", rr.Body.String())
		}
	})
}

func TestLoggingMiddleware(t *testing.T) {
	t.Run("Calls next handler", func(t *testing.T) {
		nextCalled := false
		nextHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			nextCalled = true
			w.WriteHeader(http.StatusTeapot)
		})

		handler := loggingMiddleware(nextHandler)

		req := httptest.NewRequest("GET", "/test", nil)
		rr := httptest.NewRecorder()

		handler.ServeHTTP(rr, req)

		if !nextCalled {
			t.Error("logging middleware did not call next handler")
		}
		if rr.Code != http.StatusTeapot {
			t.Errorf("expected status %d, got %d", http.StatusTeapot, rr.Code)
		}
	})
}

func TestInstructionEmbedded(t *testing.T) {
	if instruction == "" {
		t.Error("instruction variable is empty; embedding failed")
	}
}

func TestLoggingMiddleware_Styling(t *testing.T) {
	// Capture original log output and restore it later
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer log.SetOutput(os.Stdout)

	// Capture original thresholds and restore them later
	origWarn := thresholdWarn
	origUrgent := thresholdUrgentWarn
	defer func() {
		thresholdWarn = origWarn
		thresholdUrgentWarn = origUrgent
	}()

	// Lower thresholds for testing
	thresholdWarn = 10 * time.Millisecond
	thresholdUrgentWarn = 50 * time.Millisecond

	t.Run("Warn Threshold", func(t *testing.T) {
		buf.Reset()
		handler := loggingMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			time.Sleep(20 * time.Millisecond)
			w.WriteHeader(http.StatusOK)
		}))

		req := httptest.NewRequest("GET", "/warn", nil)
		rr := httptest.NewRecorder()
		handler.ServeHTTP(rr, req)

		logOutput := buf.String()
		if !strings.Contains(logOutput, "/warn") {
			t.Errorf("log output missing path: %s", logOutput)
		}
		// Since lipgloss might or might not render colors depending on the test env,
		// we mainly verify the code ran and logged.
		// However, we can check that it didn't panic and produced a log.
	})

	t.Run("Urgent Threshold", func(t *testing.T) {
		buf.Reset()
		handler := loggingMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			time.Sleep(60 * time.Millisecond)
			w.WriteHeader(http.StatusOK)
		}))

		req := httptest.NewRequest("GET", "/urgent", nil)
		rr := httptest.NewRecorder()
		handler.ServeHTTP(rr, req)

		logOutput := buf.String()
		if !strings.Contains(logOutput, "/urgent") {
			t.Errorf("log output missing path: %s", logOutput)
		}
	})
}
