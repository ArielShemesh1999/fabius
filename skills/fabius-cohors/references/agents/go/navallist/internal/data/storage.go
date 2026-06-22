package data

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
)

// BlobStorage defines the interface for saving and retrieving files.
type BlobStorage interface {
	// Save stores the data and returns a reference path (or URL) to it.
	Save(ctx context.Context, filename string, data []byte, contentType string) (string, error)
	// Load retrieves the data given the reference path.
	Load(ctx context.Context, path string) ([]byte, error)
	// GetPublicURL returns a public URL for the file if supported.
	GetPublicURL(path string) string
}

// DiskStorage implements BlobStorage using the local filesystem.
type DiskStorage struct {
	BaseDir string
}

// NewDiskStorage creates a new DiskStorage with the given base directory.
func NewDiskStorage(baseDir string) *DiskStorage {
	if err := os.MkdirAll(baseDir, 0755); err != nil {
		fmt.Printf("Warning: failed to create storage directory %s: %v\n", baseDir, err)
	}
	return &DiskStorage{BaseDir: baseDir}
}

// Save stores the data to the local disk.
func (s *DiskStorage) Save(_ context.Context, filename string, data []byte, _ string) (string, error) {
	filePath := filepath.Join(s.BaseDir, filename)
	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return "", fmt.Errorf("failed to write to disk: %w", err)
	}
	// Return absolute path so os.ReadFile works
	absPath, err := filepath.Abs(filePath)
	if err != nil {
		return filePath, nil // Fallback to relative
	}
	return absPath, nil
}

// Load retrieves the data from the local disk.
func (s *DiskStorage) Load(_ context.Context, path string) ([]byte, error) {
	return os.ReadFile(path)
}

// GetPublicURL for local disk returns an empty string as it is not supported.
func (s *DiskStorage) GetPublicURL(_ string) string {
	return ""
}
