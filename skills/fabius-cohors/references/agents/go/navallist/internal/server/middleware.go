package server

import (
	"net/http"

	"navallist/internal/data"
)

// AuthMiddleware wraps handlers to enforce authentication.
func (s *Server) AuthMiddleware(authLevel int, next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Attempt to resolve user from cookie
		cookie, err := r.Cookie("user_session")
		if err == nil {
			userID := cookie.Value
			user, err := s.Store.GetUser(r.Context(), userID)
			if err == nil {
				// User found, add to context using helpers
				r = r.WithContext(data.WithUser(r.Context(), user))
			}
		}

		// Also check for guest name in query params (for presence)
		if name := r.URL.Query().Get("name"); name != "" {
			r = r.WithContext(data.WithGuestName(r.Context(), name))
		}

		// Enforce Authentication if required
		if authLevel != AuthLevelPublic && data.GetUserID(r.Context()) == "" {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		next(w, r)
	}
}

// PermissiveAuthMiddleware resolves user if possible but always allows the request.
func (s *Server) PermissiveAuthMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return s.AuthMiddleware(AuthLevelPublic, next)
}
