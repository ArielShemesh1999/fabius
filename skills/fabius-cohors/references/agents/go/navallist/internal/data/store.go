package data

import (
	"context"
	"errors"
	"navallist/internal/data/models"
)

var ErrNotFound = errors.New("not found")

// Store defines the interface for data persistence.
// It consolidates all data access methods required by the agent and the server.
type Store interface {
	// User operations
	GetUser(ctx context.Context, id string) (*models.User, error)
	FindUserByName(ctx context.Context, name string) (*models.User, error)
	UpdateUser(ctx context.Context, id, name string) error

	// Trip operations
	GetOrCreateTrip(ctx context.Context, adkSessionID, userID, captainName, tripType string) (*models.Trip, error)
	GetTripIDBySessionID(ctx context.Context, sessionID string) (string, error)
	GetTrip(ctx context.Context, tripID string) (*models.Trip, error)
	AddTripCrew(ctx context.Context, tripID, userID, displayName string) error
	GetActiveCrewNames(ctx context.Context, tripID string) ([]string, error)
	FindCrewMember(ctx context.Context, tripID, query string) (string, error)
	ListUserTrips(ctx context.Context, userID string) ([]models.Trip, error)
	UpdateTripStatus(ctx context.Context, tripID string, status string) error
	UpdateTripType(ctx context.Context, tripID string, tripType string) error
	DeleteTrip(ctx context.Context, tripID string) error
	GetTripReport(ctx context.Context, tripID string) ([]models.ChecklistItem, error)
	UpdateTripMetadata(ctx context.Context, adkSessionID string, boatName *string, captainName *string) (*models.Trip, error)

	// Checklist operations
	UpdateItem(ctx context.Context, tripID, itemName string, isChecked bool, location string, photoArtifactID string, userID *string, completedByName string, assignedToUserID *string, assignedToName *string) (*models.ChecklistItem, error)
	UpdateItemWithAssignment(ctx context.Context, tripID, itemName string, isChecked bool, location, photoID, currentUserID, assignedToName string) (*models.ChecklistItem, bool, error)
	AddItemPhoto(ctx context.Context, tripID, itemName string, photoArtifactID string) (*models.ChecklistItem, error)

	// Artifact operations
	CreateArtifact(ctx context.Context, tripID, filename, mimeType, storagePath string) (*models.Artifact, error)
	GetArtifact(ctx context.Context, filename string) (*models.Artifact, error)
	GetArtifactByID(ctx context.Context, id string) (*models.Artifact, error)
}
