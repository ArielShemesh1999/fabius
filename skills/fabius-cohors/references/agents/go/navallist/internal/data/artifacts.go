package data

import (
	"context"
	"fmt"
	"time"

	"navallist/internal/data/models"
)

// CreateArtifact saves artifact metadata to the database.
func (s *SQLStore) CreateArtifact(ctx context.Context, tripID, filename, mimeType, storagePath string) (*models.Artifact, error) {
	query := `
		INSERT INTO artifact (trip_id, filename, mime_type, storage_path, created_at)
		VALUES (NULLIF($1, ''), $2, $3, $4, $5)
		RETURNING id, trip_id, filename, mime_type, storage_path, created_at
	`
	var a models.Artifact
	err := s.db.QueryRowxContext(ctx, query, tripID, filename, mimeType, storagePath, time.Now()).StructScan(&a)
	if err != nil {
		return nil, fmt.Errorf("failed to create artifact: %w", err)
	}
	return &a, nil
}

// GetArtifact retrieves artifact metadata by filename.
func (s *SQLStore) GetArtifact(ctx context.Context, filename string) (*models.Artifact, error) {
	query := `SELECT id, trip_id, filename, mime_type, storage_path, created_at FROM artifact WHERE filename = $1 LIMIT 1`
	var a models.Artifact
	err := s.db.GetContext(ctx, &a, query, filename)
	if err != nil {
		return nil, fmt.Errorf("artifact not found: %w", err)
	}
	return &a, nil
}

// GetArtifactByID retrieves artifact metadata by ID.
func (s *SQLStore) GetArtifactByID(ctx context.Context, id string) (*models.Artifact, error) {
	query := `SELECT id, trip_id, filename, mime_type, storage_path, created_at FROM artifact WHERE id = $1 LIMIT 1`
	var a models.Artifact
	err := s.db.GetContext(ctx, &a, query, id)
	if err != nil {
		return nil, fmt.Errorf("artifact not found: %w", err)
	}
	return &a, nil
}
