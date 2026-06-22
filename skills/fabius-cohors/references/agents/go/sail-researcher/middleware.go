package main

import (
	"fmt"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"github.com/tpryan/navalplan/services/researcher/logging"
)

// ResponseWriter wraps http.ResponseWriter to capture status code.
type ResponseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (rw *ResponseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}

func (rw *ResponseWriter) Flush() {
	if f, ok := rw.ResponseWriter.(http.Flusher); ok {
		f.Flush()
	}
}

// LoggingMiddleware logs the details of each request.
func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		ww := &ResponseWriter{ResponseWriter: w, statusCode: http.StatusOK}

		defer func() {
			timesince := time.Since(start)
			str := timesince.String()

			level := slog.LevelInfo
			if ww.statusCode >= 400 {
				level = slog.LevelWarn
			}
			if ww.statusCode >= 500 {
				level = slog.LevelError
			}

			slog.Log(r.Context(), level, "Request handled",
				"method", r.Method,
				"path", r.URL.Path,
				"status", ww.statusCode,
				"duration", str,
				"remote_addr", r.RemoteAddr,
			)
		}()

		next.ServeHTTP(ww, r)
	})
}

// TraceMiddleware propagates Cloud Trace context.
func TraceMiddleware(projectID string, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		traceHeader := r.Header.Get("X-Cloud-Trace-Context")
		traceParts := strings.Split(traceHeader, "/")
		if len(traceParts) > 0 && len(traceParts[0]) > 0 {
			traceID := traceParts[0]
			var trace string
			if projectID != "" {
				trace = fmt.Sprintf("projects/%s/traces/%s", projectID, traceID)
			} else {
				trace = traceID
			}
			ctx := logging.AddTraceToContext(r.Context(), trace)
			next.ServeHTTP(w, r.WithContext(ctx))
			return
		}
		next.ServeHTTP(w, r)
	})
}