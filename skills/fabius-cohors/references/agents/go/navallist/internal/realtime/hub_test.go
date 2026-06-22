package realtime

import (
	"context"
	"encoding/json"
	"fmt"
	"testing"

	"navallist/internal/data"
	"navallist/internal/data/models"

	"github.com/centrifugal/centrifuge"
)

func TestHandleConnect(t *testing.T) {
	mockStore := &data.MockStore{}
	service := &Service{
		Store: mockStore,
	}

	userName := "Captain Steve"
	userID := "user_123"

	mockStore.GetUserFunc = func(_ context.Context, id string) (*models.User, error) {
		if id == userID {
			return &models.User{ID: userID, Name: &userName}, nil
		}
		if id == "user_456" {
			return &models.User{ID: "user_456", Name: nil}, nil
		}
		return nil, fmt.Errorf("not found")
	}

	tests := []struct {
		name           string
		ctx            func() context.Context
		expectedUserID string
		expectedName   string
	}{
		{
			name:           "Anonymous Connection",
			ctx:            func() context.Context { return context.Background() },
			expectedUserID: "",
			expectedName:   "",
		},
		{
			name: "Guest Connection",
			ctx: func() context.Context {
				return data.WithGuestName(context.Background(), "John")
			},
			expectedUserID: "guest_John",
			expectedName:   "John",
		},
		{
			name: "Registered User Connection",
			ctx: func() context.Context {
				return data.WithUser(context.Background(), &models.User{ID: userID})
			},
			expectedUserID: userID,
			expectedName:   userName,
		},
		{
			name: "Registered User Without Name",
			ctx: func() context.Context {
				return data.WithUser(context.Background(), &models.User{ID: "user_456"})
			},
			expectedUserID: "user_456",
			expectedName:   "user_456", // Fallback to ID
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctx := tt.ctx()
			event := centrifuge.ConnectEvent{ClientID: "client"}
			reply, err := service.HandleConnect(ctx, event)
			if err != nil {
				t.Fatalf("Unexpected error: %v", err)
			}

			if reply.Credentials.UserID != tt.expectedUserID {
				t.Errorf("Expected UserID %q, got %q", tt.expectedUserID, reply.Credentials.UserID)
			}

			if reply.Credentials.UserID != "" {
				var info map[string]string
				if err := json.Unmarshal(reply.Credentials.Info, &info); err != nil {
					t.Fatalf("Failed to unmarshal info: %v", err)
				}
				if info["name"] != tt.expectedName {
					t.Errorf("Expected name %q, got %q", tt.expectedName, info["name"])
				}
			}
		})
	}
}
