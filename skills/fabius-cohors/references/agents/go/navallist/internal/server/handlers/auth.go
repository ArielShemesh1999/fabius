package handlers

import (
	"encoding/json"
	"net/http"

	"navallist/internal/data"
)

// AuthHandler handles authentication flows (simplified for local sample).
type AuthHandler struct {
	Store data.Store
}

// NewAuthHandler initializes a new AuthHandler with the given store.
func NewAuthHandler(store data.Store) *AuthHandler {
	return &AuthHandler{
		Store: store,
	}
}

// Logout clears the user session.
func (h *AuthHandler) Logout(w http.ResponseWriter, r *http.Request) {
	http.SetCookie(w, &http.Cookie{
		Name:   "user_session",
		Value:  "",
		Path:   "/",
		MaxAge: -1,
	})
	http.Redirect(w, r, "/", http.StatusTemporaryRedirect)
}

// GetMe returns the currently logged in user (if any).
func (h *AuthHandler) GetMe(w http.ResponseWriter, r *http.Request) {
	userID := data.GetUserID(r.Context())
	if userID == "" {
		http.Error(w, "Not Found", http.StatusNotFound)
		return
	}

	user, err := h.Store.GetUser(r.Context(), userID)
	if err != nil {
		http.Error(w, "Not Found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(user)
}

// UpdateMe updates the current user's profile.
func (h *AuthHandler) UpdateMe(w http.ResponseWriter, r *http.Request) {
	userID := data.GetUserID(r.Context())
	if userID == "" {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	var req struct {
		Name string `json:"name"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid body", http.StatusBadRequest)
		return
	}

	if err := h.Store.UpdateUser(r.Context(), userID, req.Name); err != nil {
		http.Error(w, "Failed to update user", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// DevLogin is kept for backward compatibility if needed, but redirects to home.
func (h *AuthHandler) DevLogin(w http.ResponseWriter, r *http.Request) {
	http.Redirect(w, r, "/", http.StatusTemporaryRedirect)
}
