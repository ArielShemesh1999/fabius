//go:build integration

package server

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"navallist/internal/config"
	"navallist/internal/data"

	"github.com/charmbracelet/log"
)

func TestNewServer(t *testing.T) {
	db := setupTestDB(t)
	defer func() {
		if err := db.Close(); err != nil {
			log.Error("failed to close database connection", "error", err)
		}
	}()

	store := data.NewSQLStore(db)

	cfg := &config.Config{
		FrontendDir: "../frontend",
	}
	srv := NewServer(store, cfg, nil, nil, nil)
	if srv.Mux == nil {
		t.Fatal("Server Mux is nil")
	}

	// Test a public route to ensure wiring is correct
	req := httptest.NewRequest("GET", "/auth/logout", nil)
	w := httptest.NewRecorder()

	srv.Mux.ServeHTTP(w, req)

	// Logout redirects or returns OK (implementation check)
	// Actually handlers/auth.go Logout usually does something.
	// Since we don't have the handler implementation in front of us,
	// we just check we didn't get 404.
	if w.Code == http.StatusNotFound {
		t.Error("Expected route /auth/logout to exist")
	}
}
