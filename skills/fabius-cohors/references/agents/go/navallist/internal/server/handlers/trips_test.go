package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"mime/multipart"
	"navallist/internal/data"
	"navallist/internal/data/models"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestTripsHandler_GetTrip_Unit(t *testing.T) {
	mockStore := &data.MockStore{
		GetTripFunc: func(_ context.Context, tripID string) (*models.Trip, error) {
			if tripID == "trip_123" {
				return &models.Trip{ID: "trip_123", Status: "Draft"}, nil
			}
			return nil, errors.New("not found")
		},
		GetTripReportFunc: func(_ context.Context, _ string) ([]models.ChecklistItem, error) {
			return []models.ChecklistItem{}, nil
		},
	}
	h := NewTripsHandler(mockStore, nil, data.NewDiskStorage("/tmp"))
	tests := []struct {
		name           string
		tripID         string
		expectedStatus int
		validate       func(*testing.T, *httptest.ResponseRecorder)
	}{
		{
			name:           "Success",
			tripID:         "trip_123",
			expectedStatus: http.StatusOK,
			validate: func(t *testing.T, w *httptest.ResponseRecorder) {
				var resp models.UnifiedTrip
				if err := json.NewDecoder(w.Body).Decode(&resp); err != nil {
					t.Fatalf("Failed to decode response: %v", err)
				}
				if resp.Trip == nil || resp.Trip.ID != "trip_123" {
					t.Errorf("Expected Trip ID trip_123, got %v", resp.Trip)
				}
			},
		},
		{
			name:           "NotFound",
			tripID:         "unknown",
			expectedStatus: http.StatusNotFound,
			validate:       func(_ *testing.T, _ *httptest.ResponseRecorder) {},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/api/trips/"+tt.tripID, nil)
			req.SetPathValue("id", tt.tripID)
			w := httptest.NewRecorder()
			h.GetTrip(w, req)
			if w.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, w.Code)
			}
			if tt.validate != nil {
				tt.validate(t, w)
			}
		})
	}
}
func TestTripsHandler_GetArtifact_Unit(t *testing.T) {
	mockStorage := data.NewDiskStorage(t.TempDir())
	ctx := context.Background()
	// Pre-seed storage and get real path
	storagePath, _ := mockStorage.Save(ctx, "photo.jpg", []byte("fake image data"), "image/jpeg")
	mockStore := &data.MockStore{
		GetArtifactByIDFunc: func(_ context.Context, id string) (*models.Artifact, error) {
			if id == "art_123" {
				return &models.Artifact{ID: "art_123", Filename: "photo.jpg", StoragePath: storagePath}, nil
			}
			return nil, errors.New("not found")
		},
		GetArtifactFunc: func(_ context.Context, filename string) (*models.Artifact, error) {
			if filename == "photo.jpg" {
				return &models.Artifact{ID: "art_123", Filename: "photo.jpg", StoragePath: storagePath}, nil
			}
			return nil, errors.New("not found")
		},
	}
	h := NewTripsHandler(mockStore, nil, mockStorage)
	tests := []struct {
		name           string
		pathParam      string
		expectedStatus int
	}{
		{
			name:           "Get by ID",
			pathParam:      "art_123",
			expectedStatus: http.StatusOK,
		},
		{
			name:           "Get by Filename",
			pathParam:      "photo.jpg",
			expectedStatus: http.StatusOK,
		},
		{
			name:           "Get with Version Param",
			pathParam:      "photo.jpg?v=1",
			expectedStatus: http.StatusOK,
		},
		{
			name:           "Not Found",
			pathParam:      "missing.jpg",
			expectedStatus: http.StatusNotFound,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/api/artifacts?path="+tt.pathParam, nil)
			w := httptest.NewRecorder()
			h.GetArtifact(w, req)
			if w.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, w.Code)
			}
		})
	}
}
func TestTripsHandler_UploadItemPhoto_Unit(t *testing.T) {
	mockStore := &data.MockStore{
		CreateArtifactFunc: func(_ context.Context, _, filename, _, _ string) (*models.Artifact, error) {
			return &models.Artifact{ID: "art_new", Filename: filename}, nil
		},
		AddItemPhotoFunc: func(_ context.Context, _, itemName, _ string) (*models.ChecklistItem, error) {
			return &models.ChecklistItem{Name: itemName}, nil
		},
	}
	mockStorage := data.NewDiskStorage(t.TempDir())
	h := NewTripsHandler(mockStore, nil, mockStorage)
	// Create multipart form request
	body := new(bytes.Buffer)
	writer := multipart.NewWriter(body)
	part, _ := writer.CreateFormFile("file", "test.jpg")
	_, _ = part.Write([]byte("image content"))
	_ = writer.Close()
	req := httptest.NewRequest("POST", "/api/trips/trip1/items/item1/photo", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.SetPathValue("id", "trip1")
	req.SetPathValue("itemId", "item1")
	w := httptest.NewRecorder()
	h.UploadItemPhoto(w, req)
	if w.Code != http.StatusOK {
		t.Errorf("Expected 200, got %d: %s", w.Code, w.Body.String())
	}
	var resp map[string]string
	_ = json.NewDecoder(w.Body).Decode(&resp)
	if resp["status"] != "success" {
		t.Errorf("Expected status success, got %s", resp["status"])
	}
}
