package data

import (
	"context"

	"navallist/internal/data/models"
)

// MockStore is a mock implementation of Store for testing.
type MockStore struct {
	GetUserFunc                  func(ctx context.Context, id string) (*models.User, error)
	UpdateUserFunc               func(ctx context.Context, id, name string) error
	GetOrCreateTripFunc          func(ctx context.Context, adkSessionID, userID, captainName, tripType string) (*models.Trip, error)
	GetTripFunc                  func(ctx context.Context, tripID string) (*models.Trip, error)
	ListUserTripsFunc            func(ctx context.Context, userID string) ([]models.Trip, error)
	UpdateTripStatusFunc         func(ctx context.Context, tripID string, status string) error
	UpdateTripTypeFunc           func(ctx context.Context, tripID string, tripType string) error
	DeleteTripFunc               func(ctx context.Context, tripID string) error
	GetTripReportFunc            func(ctx context.Context, tripID string) ([]models.ChecklistItem, error)
	UpdateItemFunc               func(ctx context.Context, tripID, itemName string, isChecked bool, location string, photoArtifactID string, userID *string, completedByName string, assignedToUserID *string, assignedToName *string) (*models.ChecklistItem, error)
	AddItemPhotoFunc             func(ctx context.Context, tripID, itemName string, photoArtifactID string) (*models.ChecklistItem, error)
	CreateArtifactFunc           func(ctx context.Context, tripID, filename, mimeType, storagePath string) (*models.Artifact, error)
	GetArtifactFunc              func(ctx context.Context, filename string) (*models.Artifact, error)
	GetArtifactByIDFunc          func(ctx context.Context, id string) (*models.Artifact, error)
	FindUserByNameFunc           func(ctx context.Context, name string) (*models.User, error)
	GetActiveCrewNamesFunc       func(ctx context.Context, tripID string) ([]string, error)
	FindCrewMemberFunc           func(ctx context.Context, tripID, query string) (string, error)
	GetTripIDBySessionIDFunc     func(ctx context.Context, sessionID string) (string, error)
	AddTripCrewFunc              func(ctx context.Context, tripID, userID, displayName string) error
	UpdateTripMetadataFunc       func(ctx context.Context, adkSessionID string, boatName *string, captainName *string) (*models.Trip, error)
	UpdateItemWithAssignmentFunc func(ctx context.Context, tripID, itemName string, isChecked bool, location, photoID, currentUserID, assignedToName string) (*models.ChecklistItem, bool, error)
}

var _ Store = (*MockStore)(nil)

func (m *MockStore) UpdateTripMetadata(ctx context.Context, adkSessionID string, boatName *string, captainName *string) (*models.Trip, error) {
	return m.UpdateTripMetadataFunc(ctx, adkSessionID, boatName, captainName)
}

func (m *MockStore) UpdateItemWithAssignment(ctx context.Context, tripID, itemName string, isChecked bool, location, photoID, currentUserID, assignedToName string) (*models.ChecklistItem, bool, error) {
	return m.UpdateItemWithAssignmentFunc(ctx, tripID, itemName, isChecked, location, photoID, currentUserID, assignedToName)
}

func (m *MockStore) GetTripIDBySessionID(ctx context.Context, sessionID string) (string, error) {
	return m.GetTripIDBySessionIDFunc(ctx, sessionID)
}

func (m *MockStore) AddTripCrew(ctx context.Context, tripID, userID, displayName string) error {
	return m.AddTripCrewFunc(ctx, tripID, userID, displayName)
}

func (m *MockStore) FindUserByName(ctx context.Context, name string) (*models.User, error) {
	return m.FindUserByNameFunc(ctx, name)
}

func (m *MockStore) FindCrewMember(ctx context.Context, tripID, query string) (string, error) {
	return m.FindCrewMemberFunc(ctx, tripID, query)
}

func (m *MockStore) GetActiveCrewNames(ctx context.Context, tripID string) ([]string, error) {
	return m.GetActiveCrewNamesFunc(ctx, tripID)
}

func (m *MockStore) GetUser(ctx context.Context, id string) (*models.User, error) {
	return m.GetUserFunc(ctx, id)
}

func (m *MockStore) UpdateUser(ctx context.Context, id, name string) error {
	return m.UpdateUserFunc(ctx, id, name)
}

func (m *MockStore) GetOrCreateTrip(ctx context.Context, adkSessionID, userID, captainName, tripType string) (*models.Trip, error) {
	return m.GetOrCreateTripFunc(ctx, adkSessionID, userID, captainName, tripType)
}

func (m *MockStore) GetTrip(ctx context.Context, tripID string) (*models.Trip, error) {
	return m.GetTripFunc(ctx, tripID)
}

func (m *MockStore) ListUserTrips(ctx context.Context, userID string) ([]models.Trip, error) {
	return m.ListUserTripsFunc(ctx, userID)
}

func (m *MockStore) UpdateTripStatus(ctx context.Context, tripID string, status string) error {
	return m.UpdateTripStatusFunc(ctx, tripID, status)
}

func (m *MockStore) UpdateTripType(ctx context.Context, tripID string, tripType string) error {
	return m.UpdateTripTypeFunc(ctx, tripID, tripType)
}

func (m *MockStore) DeleteTrip(ctx context.Context, tripID string) error {
	return m.DeleteTripFunc(ctx, tripID)
}

func (m *MockStore) GetTripReport(ctx context.Context, tripID string) ([]models.ChecklistItem, error) {
	return m.GetTripReportFunc(ctx, tripID)
}

func (m *MockStore) UpdateItem(ctx context.Context, tripID, itemName string, isChecked bool, location string, photoArtifactID string, userID *string, completedByName string, assignedToUserID *string, assignedToName *string) (*models.ChecklistItem, error) {
	return m.UpdateItemFunc(ctx, tripID, itemName, isChecked, location, photoArtifactID, userID, completedByName, assignedToUserID, assignedToName)
}

func (m *MockStore) AddItemPhoto(ctx context.Context, tripID, itemName string, photoArtifactID string) (*models.ChecklistItem, error) {
	return m.AddItemPhotoFunc(ctx, tripID, itemName, photoArtifactID)
}

func (m *MockStore) CreateArtifact(ctx context.Context, tripID, filename, mimeType, storagePath string) (*models.Artifact, error) {
	return m.CreateArtifactFunc(ctx, tripID, filename, mimeType, storagePath)
}

func (m *MockStore) GetArtifact(ctx context.Context, filename string) (*models.Artifact, error) {
	return m.GetArtifactFunc(ctx, filename)
}

func (m *MockStore) GetArtifactByID(ctx context.Context, id string) (*models.Artifact, error) {
	return m.GetArtifactByIDFunc(ctx, id)
}
