//go:build integration

package data

import (
	"context"
	"testing"

	"github.com/charmbracelet/log"
)

func TestArtifactOperations(t *testing.T) {
	db := setupTestDB(t)
	defer func() {
		if err := db.Close(); err != nil {
			log.Error("failed to close database connection", "error", err)
		}
	}()

	store := NewSQLStore(db)
	ctx := context.Background()

	// Cleanup
	cleanupData(t, db, "artifact", "trip", "users")
	defer cleanupData(t, db, "artifact", "trip", "users")

	trip, err := store.GetOrCreateTrip(ctx, "session_artifact", "", "Captain", "Leisure")
	if err != nil {
		t.Fatalf("Failed to create trip: %v", err)
	}

	tests := []struct {
		name        string
		tripID      string
		filename    string
		mimeType    string
		storagePath string
	}{
		{
			name:        "Create with TripID",
			tripID:      trip.ID,
			filename:    "photo1.jpg",
			mimeType:    "image/jpeg",
			storagePath: "/tmp/photo1.jpg",
		},
		{
			name:        "Create without TripID",
			tripID:      "",
			filename:    "photo2.jpg",
			mimeType:    "image/jpeg",
			storagePath: "/tmp/photo2.jpg",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 1. Test CreateArtifact
			created, err := store.CreateArtifact(ctx, tt.tripID, tt.filename, tt.mimeType, tt.storagePath)
			if err != nil {
				// If this fails due to NULL scanning into string TripID, we'll catch it here.
				t.Fatalf("CreateArtifact failed: %v", err)
			}
			if created.Filename != tt.filename {
				t.Errorf("Expected filename %s, got %s", tt.filename, created.Filename)
			}
			if created.StoragePath != tt.storagePath {
				t.Errorf("Expected storagePath %s, got %s", tt.storagePath, created.StoragePath)
			}

			// 2. Test GetArtifact
			fetched, err := store.GetArtifact(ctx, tt.filename)
			if err != nil {
				t.Fatalf("GetArtifact failed: %v", err)
			}
			if fetched.ID != created.ID {
				t.Errorf("Expected ID %s, got %s", created.ID, fetched.ID)
			}

			// 3. Test GetArtifactByID
			fetchedByID, err := store.GetArtifactByID(ctx, created.ID)
			if err != nil {
				t.Fatalf("GetArtifactByID failed: %v", err)
			}
			if fetchedByID.Filename != tt.filename {
				t.Errorf("Expected filename %s, got %s", tt.filename, fetchedByID.Filename)
			}
		})
	}

	t.Run("Get Non-existent Artifact", func(t *testing.T) {
		_, err := store.GetArtifact(ctx, "nonexistent.jpg")
		if err == nil {
			t.Error("Expected error for non-existent artifact, got nil")
		}
	})
}
