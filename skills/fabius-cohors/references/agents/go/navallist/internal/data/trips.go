package data

import (
	"context"
	"database/sql"
	"fmt"
	"strings"
	"time"

	"navallist/internal/data/models"
)

// UpdateTripMetadata updates the trip's metadata (Boat Name, Captain) via ADK Session ID.
// This is used by the Agent Tool.
func (s *SQLStore) UpdateTripMetadata(ctx context.Context, adkSessionID string, boatName *string, captainName *string) (*models.Trip, error) {
	// 1. Find the trip
	var trip models.Trip
	query := `SELECT * FROM trip WHERE adk_session_id = $1 LIMIT 1`
	err := s.db.GetContext(ctx, &trip, query, adkSessionID)
	if err != nil {
		return nil, fmt.Errorf("trip not found for session %s: %w", adkSessionID, err)
	}

	// 2. Update fields if provided
	updateQuery := `
		UPDATE trip 
		SET boat_name = COALESCE($1, boat_name), 
		    captain_name = COALESCE($2, captain_name)
		WHERE id = $3
		RETURNING *
	`

	var updatedTrip models.Trip
	err = s.db.GetContext(ctx, &updatedTrip, updateQuery, boatName, captainName, trip.ID)
	if err != nil {
		return nil, fmt.Errorf("failed to update trip metadata: %w", err)
	}

	return &updatedTrip, nil
}

// DeleteTrip removes a trip and all its associated data (checklists, artifacts).
func (s *SQLStore) DeleteTrip(ctx context.Context, tripID string) error {
	// Cascading deletes handled by FK constraints usually, but explicit is safer or if schema differs
	// Schema has ON DELETE CASCADE for checklist_item and artifact.
	query := `DELETE FROM trip WHERE id = $1 OR adk_session_id = $1`
	res, err := s.db.ExecContext(ctx, query, tripID)
	if err != nil {
		return err
	}
	rows, _ := res.RowsAffected()
	if rows == 0 {
		return fmt.Errorf("trip not found")
	}
	return nil
}

// UpdateTripStatus updates the status of a trip.
func (s *SQLStore) UpdateTripStatus(ctx context.Context, tripID string, status string) error {
	query := `UPDATE trip SET status = $1 WHERE id = $2 OR adk_session_id = $2`
	res, err := s.db.ExecContext(ctx, query, status, tripID)
	if err != nil {
		return err
	}
	rows, _ := res.RowsAffected()
	if rows == 0 {
		return fmt.Errorf("trip not found")
	}
	return nil
}

// UpdateTripType updates the type of a trip (Departing/Returning).
func (s *SQLStore) UpdateTripType(ctx context.Context, tripID string, tripType string) error {
	query := `UPDATE trip SET trip_type = $1 WHERE id = $2 OR adk_session_id = $2`
	res, err := s.db.ExecContext(ctx, query, tripType, tripID)
	if err != nil {
		return err
	}
	rows, _ := res.RowsAffected()
	if rows == 0 {
		return fmt.Errorf("trip not found")
	}
	return nil
}

// GetActiveCrewNames retrieves all unique names associated with a trip (captain and registered users).
func (s *SQLStore) GetActiveCrewNames(ctx context.Context, tripID string) ([]string, error) {
	// 1. Get real trip ID if adkSessionID passed
	var realID string
	err := s.db.GetContext(ctx, &realID, `SELECT id FROM trip WHERE id = $1 OR adk_session_id = $1 LIMIT 1`, tripID)
	if err != nil {
		return nil, err
	}

	// We ONLY trust the captain_name and registered users.
	// We do NOT trust checklist_item.assigned_to_name as it might contain hallucinations.
	query := `
		SELECT DISTINCT name FROM (
			SELECT captain_name as name FROM trip WHERE id = $1 AND captain_name IS NOT NULL
			UNION
			SELECT display_name as name FROM trip_crew WHERE trip_id = $1 AND display_name IS NOT NULL
			UNION
			SELECT u.name FROM checklist_item ci JOIN users u ON ci.assigned_to_user_id = u.id WHERE ci.trip_id = $1 AND u.name IS NOT NULL
			UNION
			SELECT u.name FROM checklist_item ci JOIN users u ON ci.completed_by_user_id = u.id WHERE ci.trip_id = $1 AND u.name IS NOT NULL
			UNION
			SELECT assigned_to_name as name FROM checklist_item WHERE trip_id = $1 AND assigned_to_name IS NOT NULL
			UNION
			SELECT completed_by_name as name FROM checklist_item WHERE trip_id = $1 AND completed_by_name IS NOT NULL
			UNION
			SELECT u.name FROM trip t JOIN users u ON t.user_id = u.id WHERE t.id = $1 AND u.name IS NOT NULL
		) names WHERE name <> ''
	`
	var names []string
	err = s.db.SelectContext(ctx, &names, query, realID)
	if err != nil {
		return nil, err
	}
	return names, nil
}

// FindCrewMember attempts to find a crew member by name using fuzzy matching.
func (s *SQLStore) FindCrewMember(ctx context.Context, tripID, query string) (string, error) {
	// 1. Get real trip ID
	var realID string
	err := s.db.GetContext(ctx, &realID, `SELECT id FROM trip WHERE id = $1 OR adk_session_id = $1 LIMIT 1`, tripID)
	if err != nil {
		return "", err
	}

	sqlQuery := `
		WITH crew_names AS (
			SELECT captain_name as name FROM trip WHERE id = $1 AND captain_name IS NOT NULL
			UNION
			SELECT display_name as name FROM trip_crew WHERE trip_id = $1 AND display_name IS NOT NULL
			UNION
			SELECT u.name FROM checklist_item ci JOIN users u ON ci.assigned_to_user_id = u.id WHERE ci.trip_id = $1 AND u.name IS NOT NULL
			UNION
			SELECT u.name FROM checklist_item ci JOIN users u ON ci.completed_by_user_id = u.id WHERE ci.trip_id = $1 AND u.name IS NOT NULL
			UNION
			SELECT assigned_to_name as name FROM checklist_item WHERE trip_id = $1 AND assigned_to_name IS NOT NULL
			UNION
			SELECT completed_by_name as name FROM checklist_item WHERE trip_id = $1 AND completed_by_name IS NOT NULL
			UNION
			SELECT u.name FROM trip t JOIN users u ON t.user_id = u.id WHERE t.id = $1 AND u.name IS NOT NULL
		)
		SELECT name
		FROM crew_names
		WHERE name <> '' AND (
			LOWER(name) = LOWER($2)
			OR LOWER(name) LIKE '%' || LOWER($2) || '%'
		)
		ORDER BY 
			CASE 
				WHEN LOWER(name) = LOWER($2) THEN 0 
				ELSE 1
			END ASC,
			name ASC
		LIMIT 1
	`
	var name string
	err = s.db.GetContext(ctx, &name, sqlQuery, realID, query)
	if err != nil {
		if err == sql.ErrNoRows {
			return "", nil
		}
		return "", err
	}
	return name, nil
}

// GetTripReport retrieves all checklist items for a trip to generate a report.
func (s *SQLStore) GetTripReport(ctx context.Context, tripID string) ([]models.ChecklistItem, error) {
	var items []models.ChecklistItem
	query := `
		SELECT ci.id, ci.trip_id, ci.category, ci.name, ci.item_type, ci.is_checked, ci.count_value, 
		       ci.location_text, ci.flagged_issue, ci.completed_by_user_id, ci.completed_by_name, ci.updated_at,
		       ci.assigned_to_user_id, ci.assigned_to_name,
		       u.name as completed_by_user_name
		FROM checklist_item ci
		LEFT JOIN users u ON ci.completed_by_user_id = u.id
		WHERE ci.trip_id = (SELECT id FROM trip WHERE id = $1 OR adk_session_id = $1 LIMIT 1) 
		ORDER BY ci.category, ci.name
	`
	err := s.db.SelectContext(ctx, &items, query, tripID)
	if err != nil {
		return nil, err
	}

	// Fetch Artifacts if there are items
	if len(items) > 0 {
		realTripID := items[0].TripID

		var artifacts []models.Artifact
		artQuery := `SELECT id, trip_id, checklist_item_id, filename, mime_type, storage_path, created_at FROM artifact WHERE trip_id = $1 AND checklist_item_id IS NOT NULL`
		err = s.db.SelectContext(ctx, &artifacts, artQuery, realTripID)
		if err == nil {
			// Map artifacts to items
			artMap := make(map[string][]models.Artifact)
			for _, art := range artifacts {
				if art.ChecklistItemID != nil {
					artMap[*art.ChecklistItemID] = append(artMap[*art.ChecklistItemID], art)
				}
			}

			for i := range items {
				if photos, ok := artMap[items[i].ID]; ok {
					items[i].Photos = photos
				}
			}
		}
	}

	return items, nil
}

// GetTripIDBySessionID retrieves the internal trip ID for a given ADK session ID.
func (s *SQLStore) GetTripIDBySessionID(ctx context.Context, sessionID string) (string, error) {
	var id string
	query := `SELECT id FROM trip WHERE adk_session_id = $1 LIMIT 1`
	err := s.db.GetContext(ctx, &id, query, sessionID)
	if err != nil {
		return "", err
	}
	return id, nil
}

// AddTripCrew records a user as part of a trip's crew.
func (s *SQLStore) AddTripCrew(ctx context.Context, tripID, userID, displayName string) error {
	query := `
		INSERT INTO trip_crew (trip_id, user_id, display_name)
		VALUES ($1, $2, $3)
		ON CONFLICT (trip_id, user_id) 
		DO UPDATE SET display_name = EXCLUDED.display_name
	`
	_, err := s.db.ExecContext(ctx, query, tripID, userID, displayName)
	return err
}

// GetTrip retrieves the trip details.
func (s *SQLStore) GetTrip(ctx context.Context, tripID string) (*models.Trip, error) {
	var trip models.Trip
	query := `SELECT id, adk_session_id, user_id, boat_name, captain_name, departure_time, status, created_at 
	          FROM trip WHERE id = $1 OR adk_session_id = $1 LIMIT 1`
	err := s.db.GetContext(ctx, &trip, query, tripID)
	if err != nil {
		return nil, err
	}
	return &trip, nil
}

// ListUserTrips returns all trips for a given user.
func (s *SQLStore) ListUserTrips(ctx context.Context, userID string) ([]models.Trip, error) {
	var trips []models.Trip
	query := `SELECT * FROM trip WHERE user_id = $1 ORDER BY created_at DESC`
	err := s.db.SelectContext(ctx, &trips, query, userID)
	if err != nil {
		return nil, err
	}
	return trips, nil
}

// GetOrCreateTrip ensures a trip exists for the given ADK session ID and user.
func (s *SQLStore) GetOrCreateTrip(ctx context.Context, adkSessionID, userID, captainName, tripType string) (*models.Trip, error) {
	var trip models.Trip
	query := `SELECT * FROM trip WHERE adk_session_id = $1 LIMIT 1`
	err := s.db.GetContext(ctx, &trip, query, adkSessionID)

	if err == nil {
		// Found it
		if trip.UserID == nil && userID != "" {
			_, _ = s.db.ExecContext(ctx, `UPDATE trip SET user_id = $1 WHERE id = $2`, userID, trip.ID)
			trip.UserID = &userID
		}
		return &trip, nil
	}

	// Create new
	if tripType == "" {
		tripType = "Departing"
	}

	insertQuery := `
		INSERT INTO trip (adk_session_id, user_id, captain_name, trip_type, status, created_at)
		VALUES ($1, $2, $3, $4, 'Draft', $5)
		RETURNING *
	`
	var uid *string
	if userID != "" {
		uid = &userID
	}

	err = s.db.GetContext(ctx, &trip, insertQuery, adkSessionID, uid, captainName, tripType, time.Now())
	if err != nil {
		return nil, fmt.Errorf("failed to create trip: %w", err)
	}
	return &trip, nil
}

// UpdateItemWithAssignment performs a higher-level update including resolving fuzzy matches for assignments.
func (s *SQLStore) UpdateItemWithAssignment(ctx context.Context, tripID, itemName string, isChecked bool, location, photoID, currentUserID, assignedToName string) (*models.ChecklistItem, bool, error) {
	var assignedToUserID *string
	var finalAssignedName *string
	matchFound := true

	if assignedToName != "" {
		// 1. Try DB Fuzzy Match
		match, _ := s.FindCrewMember(ctx, tripID, assignedToName)

		// 2. Fallback to current user if name matches
		currentUserName := ""
		if !strings.HasPrefix(currentUserID, "guest_") {
			u, err := s.GetUser(ctx, currentUserID)
			if err == nil && u != nil && u.Name != nil {
				currentUserName = *u.Name
			}
		}

		if match == "" && currentUserName != "" && strings.EqualFold(assignedToName, currentUserName) {
			match = currentUserName
		}

		if match != "" {
			finalAssignedName = &match
			// If it matches a registered user, try to get their ID
			regUser, err := s.FindUserByName(ctx, match)
			if err == nil && regUser != nil {
				assignedToUserID = &regUser.ID
			} else if strings.EqualFold(match, currentUserName) && !strings.HasPrefix(currentUserID, "guest_") {
				assignedToUserID = &currentUserID
			}
		} else {
			// Assign by name only (for new/guest users)
			finalAssignedName = &assignedToName
			matchFound = false
		}
	}

	var uidPtr *string
	if currentUserID != "" {
		uidPtr = &currentUserID
	}

	item, err := s.UpdateItem(ctx, tripID, itemName, isChecked, location, photoID, uidPtr, currentUserID, assignedToUserID, finalAssignedName)
	return item, matchFound, err
}
