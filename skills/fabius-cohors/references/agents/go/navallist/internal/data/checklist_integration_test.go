//go:build integration

package data

import (
	"context"
	"testing"

	"github.com/charmbracelet/log"
)

func TestChecklistOperations(t *testing.T) {
	db := setupTestDB(t)
	defer func() {
		if err := db.Close(); err != nil {
			log.Error("failed to close database connection", "error", err)
		}
	}()

	store := NewSQLStore(db)
	ctx := context.Background()

	// Cleanup
	cleanupData(t, db, "artifact", "checklist_item", "trip", "users")
	defer cleanupData(t, db, "artifact", "checklist_item", "trip", "users")

	// Setup: Create a Trip
	trip, _ := store.GetOrCreateTrip(ctx, "session_checklist", "", "Captain", "Returning")

	t.Run("UpdateItem (Insert and Update)", func(t *testing.T) {
		itemName := "Engine Oil"

		// 1. Insert
		item, err := store.UpdateItem(ctx, trip.ID, itemName, true, "Engine Room", "", nil, "Checker", nil, nil)
		if err != nil {
			t.Fatalf("UpdateItem (Insert) failed: %v", err)
		}
		if item.Name != itemName || !item.IsChecked {
			t.Errorf("Unexpected item state: %+v", item)
		}

		// 2. Update
		updatedItem, err := store.UpdateItem(ctx, trip.ID, itemName, true, "Locker A", "", nil, "Checker", nil, nil)
		if err != nil {
			t.Fatalf("UpdateItem (Update) failed: %v", err)
		}
		if updatedItem.ID != item.ID {
			t.Error("Expected same ID for update")
		}
		if updatedItem.LocationText == nil || *updatedItem.LocationText != "Locker A" {
			t.Errorf("Expected location 'Locker A', got %v", updatedItem.LocationText)
		}
	})

	t.Run("AddItemPhoto", func(t *testing.T) {
		itemName := "Flares"
		// 1. Create an artifact first
		art, err := store.CreateArtifact(ctx, trip.ID, "flares.jpg", "image/jpeg", "/tmp/flares.jpg")
		if err != nil {
			t.Fatalf("CreateArtifact failed: %v", err)
		}

		// 2. Link to item
		item, err := store.AddItemPhoto(ctx, trip.ID, itemName, art.ID)
		if err != nil {
			t.Fatalf("AddItemPhoto failed: %v", err)
		}

		// 3. Verify artifact is linked
		var linkedItemID string
		err = db.GetContext(ctx, &linkedItemID, "SELECT checklist_item_id FROM artifact WHERE id = $1", art.ID)
		if err != nil {
			t.Fatalf("Failed to query artifact: %v", err)
		}
		if linkedItemID != item.ID {
			t.Errorf("Expected linkedItemID %s, got %s", item.ID, linkedItemID)
		}
	})
}
