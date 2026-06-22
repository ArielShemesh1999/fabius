package data

import (
	"context"
	"navallist/internal/data/models"
)

type contextKey string

const (
	userContextKey      contextKey = "user"
	userIDContextKey    contextKey = "user_id"
	guestNameContextKey contextKey = "guest_name"
)

// WithUser adds a user object to the context.
func WithUser(ctx context.Context, user *models.User) context.Context {
	ctx = context.WithValue(ctx, userContextKey, user)
	return context.WithValue(ctx, userIDContextKey, user.ID)
}

// WithGuestName adds a guest name to the context.
func WithGuestName(ctx context.Context, name string) context.Context {
	return context.WithValue(ctx, guestNameContextKey, name)
}

// GetUser retrieves the user from the context.
func GetUser(ctx context.Context) *models.User {
	user, _ := ctx.Value(userContextKey).(*models.User)
	return user
}

// GetUserID retrieves the user ID from the context.
func GetUserID(ctx context.Context) string {
	id, _ := ctx.Value(userIDContextKey).(string)
	return id
}

// GetGuestName retrieves the guest name from the context.
func GetGuestName(ctx context.Context) string {
	name, _ := ctx.Value(guestNameContextKey).(string)
	return name
}
