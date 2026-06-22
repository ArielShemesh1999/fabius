package handlers

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"path/filepath"
	"strings"
	"time"

	"navallist/internal/agent"
	"navallist/internal/data"
	"navallist/internal/data/models"

	"github.com/charmbracelet/log"
)

// TripsHandler handles trip-related requests.
type TripsHandler struct {
	Store       data.Store
	AgentClient *agent.LocalAgentClient
	Storage     data.BlobStorage
}

// NewTripsHandler initializes a new TripsHandler with the given dependencies.
func NewTripsHandler(store data.Store, agentClient *agent.LocalAgentClient, storage data.BlobStorage) *TripsHandler {
	return &TripsHandler{Store: store, AgentClient: agentClient, Storage: storage}
}

// UploadItemPhoto handles the upload of a photo for a specific checklist item.
func (h *TripsHandler) UploadItemPhoto(w http.ResponseWriter, r *http.Request) {
	tripID := r.PathValue("id")
	itemID := r.PathValue("itemId")

	if tripID == "" || itemID == "" {
		http.Error(w, "Missing trip ID or Item ID", http.StatusBadRequest)
		return
	}

	// 1. Parse File
	// Limit upload size to 10MB
	if err := r.ParseMultipartForm(10 << 20); err != nil {
		http.Error(w, "File too large", http.StatusBadRequest)
		return
	}
	file, handler, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving file", http.StatusBadRequest)
		return
	}
	defer func() {
		if err := file.Close(); err != nil {
			log.Error("failed to close uploaded file", "error", err)
		}
	}()

	fileBytes, err := io.ReadAll(file)

	if err != nil {
		http.Error(w, "Error reading file", http.StatusInternalServerError)
		return
	}

	// 2. Generate Filename
	// photo_{tripID}_{sanitized_item_name}_{timestamp}.jpg
	cleanItemName := strings.ReplaceAll(itemID, " ", "_")
	cleanItemName = strings.ReplaceAll(cleanItemName, "/", "-")
	filename := fmt.Sprintf("photo_%s_%s_%d%s", tripID, cleanItemName, time.Now().Unix(), filepath.Ext(handler.Filename))

	// 3. Save to Storage
	storagePath, err := h.Storage.Save(r.Context(), filename, fileBytes, handler.Header.Get("Content-Type"))
	if err != nil {
		http.Error(w, "Error saving file: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// 4. Create Artifact
	artifact, err := h.Store.CreateArtifact(r.Context(), tripID, filename, handler.Header.Get("Content-Type"), storagePath)
	if err != nil {
		http.Error(w, "Error creating artifact record: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// 5. Link to Item
	_, err = h.Store.AddItemPhoto(r.Context(), tripID, itemID, artifact.ID)
	if err != nil {
		http.Error(w, "Error linking photo to item: "+err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]string{
		"status":      "success",
		"artifact_id": artifact.ID,
	})
}

// UpdateStatus handles the update of a trip's status.
func (h *TripsHandler) UpdateStatus(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		http.Error(w, "Missing trip ID", http.StatusBadRequest)
		return
	}

	var req struct {
		Status string `json:"status"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if err := h.Store.UpdateTripStatus(r.Context(), id, req.Status); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// UpdateType handles the update of a trip's type.
func (h *TripsHandler) UpdateType(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		http.Error(w, "Missing trip ID", http.StatusBadRequest)
		return
	}

	var req struct {
		TripType string `json:"trip_type"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if err := h.Store.UpdateTripType(r.Context(), id, req.TripType); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// GetArtifact handles the retrieval of an artifact's data.
func (h *TripsHandler) GetArtifact(w http.ResponseWriter, r *http.Request) {
	// Query params: path (which is the filename)
	q := r.URL.Query()
	filename := q.Get("path")
	if filename == "" {
		http.Error(w, "Missing path parameter", http.StatusBadRequest)
		return
	}

	// 1. Fetch metadata from DB
	// Heuristic: If it has no dot, assume it might be an ID.
	var art *models.Artifact
	var err error

	if !strings.Contains(filename, ".") {
		art, err = h.Store.GetArtifactByID(r.Context(), filename)
	}

	// If ID lookup failed or wasn't tried, try by filename
	if art == nil || err != nil {
		art, err = h.Store.GetArtifact(r.Context(), filename)
		if err != nil {
			// Try without query params in case ?v=1 is attached
			cleanFilename := filename
			if idx := strings.Index(filename, "?"); idx != -1 {
				cleanFilename = filename[:idx]
			}
			art, err = h.Store.GetArtifact(r.Context(), cleanFilename)
			// If still failing and cleanFilename != filename, try ID again on cleanFilename
			if err != nil && cleanFilename != filename && !strings.Contains(cleanFilename, ".") {
				art, err = h.Store.GetArtifactByID(r.Context(), cleanFilename)
			}

			if err != nil {
				http.Error(w, "Artifact not found", http.StatusNotFound)
				return
			}
		}
	}

	// 2. Serve
	// Check if we can redirect to a public URL (e.g. GCS)
	if pubURL := h.Storage.GetPublicURL(art.StoragePath); pubURL != "" {
		http.Redirect(w, r, pubURL, http.StatusFound)
		return
	}

	// Fallback to loading from storage (e.g. Disk)
	data, err := h.Storage.Load(r.Context(), art.StoragePath)
	if err != nil {
		http.Error(w, "Failed to read artifact from storage", http.StatusInternalServerError)
		return
	}

	if art.MimeType != nil {
		w.Header().Set("Content-Type", *art.MimeType)
	} else {
		w.Header().Set("Content-Type", "application/octet-stream")
	}

	w.Header().Set("Cache-Control", "public, max-age=3600")
	_, _ = w.Write(data)
}

// GetReport handles the generation of a trip's report.
func (h *TripsHandler) GetReport(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		http.Error(w, "Missing trip ID", http.StatusBadRequest)
		return
	}

	items, err := h.Store.GetTripReport(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(items)
}

// ListTrips handles the retrieval of a user's trips.
func (h *TripsHandler) ListTrips(w http.ResponseWriter, r *http.Request) {
	userID := data.GetUserID(r.Context())
	if userID == "" {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	trips, err := h.Store.ListUserTrips(r.Context(), userID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(trips)
}

// CreateTrip handles the creation or joining of a trip.
func (h *TripsHandler) CreateTrip(w http.ResponseWriter, r *http.Request) {
	var req struct {
		SessionID   string `json:"session_id"`
		CaptainName string `json:"captain_name"`
		TripType    string `json:"trip_type"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid body", http.StatusBadRequest)
		return
	}

	// Get User ID if logged in
	userID := data.GetUserID(r.Context())

	// 1. Check if trip exists
	// (Check logic removed: anyone can create/join trips now)

	// 2. Get or Create
	trip, err := h.Store.GetOrCreateTrip(r.Context(), req.SessionID, userID, req.CaptainName, req.TripType)
	if err != nil {
		log.Error("Failed to GetOrCreateTrip", "err", err, "sessionID", req.SessionID, "userID", userID)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	// 3. Record in Trip Crew
	displayName := req.CaptainName
	if displayName == "" && userID != "" {
		u, _ := h.Store.GetUser(r.Context(), userID)
		if u != nil && u.Name != nil {
			displayName = *u.Name
		}
	}

	actualUserID := userID
	if actualUserID == "" && displayName != "" {
		actualUserID = "guest_" + displayName
	}

	if actualUserID != "" {
		_ = h.Store.AddTripCrew(r.Context(), trip.ID, actualUserID, displayName)
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(trip)
}

// DeleteTrip handles the deletion of a trip.
func (h *TripsHandler) DeleteTrip(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		http.Error(w, "Missing trip ID", http.StatusBadRequest)
		return
	}

	if err := h.Store.DeleteTrip(r.Context(), id); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// GetTrip handles the retrieval of a trip's details.
func (h *TripsHandler) GetTrip(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if id == "" {
		http.Error(w, "Missing trip ID", http.StatusBadRequest)
		return
	}

	userID := r.URL.Query().Get("userId")

	// 1. Fetch Trip Metadata
	trip, err := h.Store.GetTrip(r.Context(), id)
	if err != nil {
		http.Error(w, "Trip not found", http.StatusNotFound)
		return
	}

	// 2. Fetch Checklist Items
	items, err := h.Store.GetTripReport(r.Context(), id)
	if err != nil {
		items = []models.ChecklistItem{}
	}

	// 3. Fetch Agent Session State if userId is provided
	var agentState interface{}
	if userID != "" && h.AgentClient != nil {
		session, err := h.AgentClient.GetSession(r.Context(), "navallist_agent", userID, trip.ADKSessionID)
		if err == nil && session != nil {
			agentState = session["state"]
		}
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(models.UnifiedTrip{
		Trip:       trip,
		Items:      items,
		AgentState: agentState,
	})
}

// UpdateItem handles the update of a specific checklist item.
func (h *TripsHandler) UpdateItem(w http.ResponseWriter, r *http.Request) {
	tripID := r.PathValue("id")
	itemID := r.PathValue("itemId") // This is effectively the item name or ID from schema

	if tripID == "" || itemID == "" {
		http.Error(w, "Missing trip ID or Item ID", http.StatusBadRequest)
		return
	}

	var req struct {
		IsChecked        bool    `json:"is_checked"`
		Location         string  `json:"location"`
		Value            string  `json:"value"` // For text/number inputs
		PhotoArtifactID  string  `json:"photo_artifact_id"`
		CompletedByName  string  `json:"completed_by_name"`
		AssignedToUserID *string `json:"assigned_to_user_id"`
		AssignedToName   *string `json:"assigned_to_name"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid body", http.StatusBadRequest)
		return
	}

	valToStore := req.Location
	if req.Value != "" {
		valToStore = req.Value
	}

	// Get User ID if logged in
	var userID *string
	uid := data.GetUserID(r.Context())
	if uid != "" {
		userID = &uid
	}

	item, err := h.Store.UpdateItem(r.Context(), tripID, itemID, req.IsChecked, valToStore, req.PhotoArtifactID, userID, req.CompletedByName, req.AssignedToUserID, req.AssignedToName)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(item)
}
