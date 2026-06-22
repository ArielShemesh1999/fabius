package models

import (
	"time"
)

// Trip represents a checklist session.
type Trip struct {
	ID            string     `db:"id" json:"id"`
	ADKSessionID  string     `db:"adk_session_id" json:"adk_session_id"`
	UserID        *string    `db:"user_id" json:"user_id,omitempty"`
	BoatName      *string    `db:"boat_name" json:"boat_name,omitempty"`
	CaptainName   *string    `db:"captain_name" json:"captain_name,omitempty"`
	TripType      string     `db:"trip_type" json:"trip_type"`
	DepartureTime *time.Time `db:"departure_time" json:"departure_time,omitempty"`
	Status        string     `db:"status" json:"status"`
	CreatedAt     time.Time  `db:"created_at" json:"created_at"`
}

// ChecklistItem represents a specific task or item in the checklist.
type ChecklistItem struct {
	ID                  string     `db:"id" json:"id"`
	TripID              string     `db:"trip_id" json:"trip_id"`
	Category            string     `db:"category" json:"category"`
	Name                string     `db:"name" json:"name"`
	ItemType            *string    `db:"item_type" json:"item_type,omitempty"`
	IsChecked           bool       `db:"is_checked" json:"is_checked"`
	CountValue          int        `db:"count_value" json:"count_value"`
	LocationText        *string    `db:"location_text" json:"location_text,omitempty"`
	Photos              []Artifact `db:"-" json:"photos,omitempty"` // Populated manually
	FlaggedIssue        *string    `db:"flagged_issue" json:"flagged_issue,omitempty"`
	CompletedByUserID   *string    `db:"completed_by_user_id" json:"completed_by_user_id,omitempty"`
	CompletedByName     *string    `db:"completed_by_name" json:"completed_by_name,omitempty"`
	CompletedByUserName *string    `db:"completed_by_user_name" json:"completed_by_user_name,omitempty"`
	AssignedToUserID    *string    `db:"assigned_to_user_id" json:"assigned_to_user_id,omitempty"`
	AssignedToName      *string    `db:"assigned_to_name" json:"assigned_to_name,omitempty"`
	UpdatedAt           time.Time  `db:"updated_at" json:"updated_at"`
}

// Artifact represents a file (photo/audio) stored related to a trip.
type Artifact struct {
	ID              string    `db:"id" json:"id"`
	TripID          *string   `db:"trip_id" json:"trip_id,omitempty"`
	ChecklistItemID *string   `db:"checklist_item_id" json:"checklist_item_id,omitempty"`
	Filename        string    `db:"filename" json:"filename"`
	MimeType        *string   `db:"mime_type" json:"mime_type,omitempty"`
	StoragePath     string    `db:"storage_path" json:"storage_path"`
	CreatedAt       time.Time `db:"created_at" json:"created_at"`
}

// UnifiedTrip represents the combined state of a trip, including metadata, items, and agent session state.
type UnifiedTrip struct {
	Trip       *Trip           `json:"trip"`
	Items      []ChecklistItem `json:"items"`
	AgentState interface{}     `json:"agent_state,omitempty"`
}

// User represents a registered user via Google OAuth.
type User struct {
	ID        string    `db:"id" json:"id"`
	Email     string    `db:"email" json:"email"`
	GoogleSub string    `db:"google_sub" json:"google_sub"`
	Name      *string   `db:"name" json:"name,omitempty"`
	Picture   *string   `db:"picture" json:"picture,omitempty"`
	CreatedAt time.Time `db:"created_at" json:"created_at"`
}
