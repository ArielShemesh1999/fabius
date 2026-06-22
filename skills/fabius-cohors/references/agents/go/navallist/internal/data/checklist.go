package data

import (
	"context"
	"fmt"
	"log/slog"
	"time"

	"navallist/internal/data/models"

	"github.com/charmbracelet/log"
)

// UpdateItem updates a specific item's status and details, using an UPSERT to prevent duplicates.
func (s *SQLStore) UpdateItem(ctx context.Context, tripID string, itemName string, isChecked bool, location string, _ string, userID *string, completedByName string, assignedToUserID *string, assignedToName *string) (*models.ChecklistItem, error) {
	// Determine the user to record.
	var userToRecord *string
	var nameToRecord *string

	if isChecked {
		userToRecord = userID
		if completedByName != "" {
			nameToRecord = &completedByName
		}
	} else {
		userToRecord = nil
		nameToRecord = nil
	}

	// We use INSERT ... ON CONFLICT to ensure atomicity and prevent race conditions creating duplicates.
	// Note: 'name' must be exactly the same for conflict detection (Postgres unique constraint is case-sensitive by default).
	// If items are pre-seeded, we should use their exact names.

	upsertQuery := `
		INSERT INTO checklist_item (trip_id, category, name, is_checked, location_text, completed_by_user_id, completed_by_name, assigned_to_user_id, assigned_to_name, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
		ON CONFLICT (trip_id, name) 
		DO UPDATE SET 
			is_checked = EXCLUDED.is_checked,
			location_text = CASE 
				WHEN EXCLUDED.location_text IS NOT NULL AND EXCLUDED.location_text <> '' THEN EXCLUDED.location_text 
				ELSE checklist_item.location_text 
			END,
			completed_by_user_id = EXCLUDED.completed_by_user_id,
			completed_by_name = EXCLUDED.completed_by_name,
			assigned_to_user_id = COALESCE(EXCLUDED.assigned_to_user_id, checklist_item.assigned_to_user_id),
			assigned_to_name = COALESCE(EXCLUDED.assigned_to_name, checklist_item.assigned_to_name),
			updated_at = EXCLUDED.updated_at
		RETURNING id, trip_id, category, name, item_type, is_checked, count_value, location_text, flagged_issue, completed_by_user_id, completed_by_name, assigned_to_user_id, assigned_to_name, updated_at
	`

	// Default category if item is new
	category := "General"

	log.Info("Executing UPSERT", "tripID", tripID, "name", itemName)

	start := time.Now()
	var item models.ChecklistItem
	err := s.db.QueryRowxContext(ctx, upsertQuery,
		tripID, category, itemName, isChecked, location, userToRecord, nameToRecord, assignedToUserID, assignedToName, time.Now(),
	).StructScan(&item)

	if err != nil {
		slog.Error("UPSERT failed", "error", err, "duration", time.Since(start))
		return nil, fmt.Errorf("failed to upsert item: %w", err)
	}
	slog.Info("UPSERT success", "id", item.ID, "duration", time.Since(start))

	return &item, nil
}

// AddItemPhoto ensures the checklist item exists (via UPSERT) and then links the artifact to it.
func (s *SQLStore) AddItemPhoto(ctx context.Context, tripID string, itemName string, photoArtifactID string) (*models.ChecklistItem, error) {
	// 1. Ensure item exists
	upsertQuery := `
		INSERT INTO checklist_item (trip_id, category, name, is_checked, updated_at)
		VALUES ($1, $2, $3, $4, $5)
		ON CONFLICT (trip_id, name) 
		DO UPDATE SET 
			is_checked = EXCLUDED.is_checked,
			updated_at = EXCLUDED.updated_at
		RETURNING id, trip_id, category, name, item_type, is_checked, count_value, location_text, flagged_issue, updated_at
	`

	category := "General"
	var item models.ChecklistItem
	err := s.db.QueryRowxContext(ctx, upsertQuery, tripID, category, itemName, true, time.Now()).StructScan(&item)
	if err != nil {
		return nil, fmt.Errorf("failed to ensure item exists: %w", err)
	}

	// 2. Link artifact to item
	updateArtifactQuery := `UPDATE artifact SET checklist_item_id = $1 WHERE id = $2`
	_, err = s.db.ExecContext(ctx, updateArtifactQuery, item.ID, photoArtifactID)
	if err != nil {
		return nil, fmt.Errorf("failed to link photo to item: %w", err)
	}

	return &item, nil
}
