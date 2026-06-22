package server

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"navallist/internal/config"
	"navallist/internal/data"
	"navallist/internal/data/models"
)

func TestAuthMiddleware_Unit(t *testing.T) {
	// AuthLevelUser requires a valid user session.
	const AuthLevelUser = 1

	mockStore := &data.MockStore{
		GetUserFunc: func(_ context.Context, id string) (*models.User, error) {
			if id == "user_123" {
				return &models.User{ID: "user_123", Name: toPtr("Test User")}, nil
			}
			return nil, errors.New("not found")
		},
	}

	srv := &Server{
		Store:  mockStore,
		Config: &config.Config{},
	}
	nextHandler := http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	tests := []struct {
		name           string
		cookieValue    string
		expectedStatus int
	}{
		{
			name:           "Valid User",
			cookieValue:    "user_123",
			expectedStatus: http.StatusOK,
		},
		{
			name:           "Invalid User",
			cookieValue:    "invalid",
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:           "No Cookie",
			cookieValue:    "",
			expectedStatus: http.StatusUnauthorized,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/", nil)
			if tt.cookieValue != "" {
				req.AddCookie(&http.Cookie{Name: "user_session", Value: tt.cookieValue})
			}
			w := httptest.NewRecorder()

			srv.AuthMiddleware(AuthLevelUser, nextHandler).ServeHTTP(w, req)

			if w.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, w.Code)
			}
		})
	}
}

func toPtr(s string) *string {
	return &s
}
