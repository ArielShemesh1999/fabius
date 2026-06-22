package data

import (
	"context"
	"os"
	"testing"

	"github.com/charmbracelet/log"
)

func TestDiskStorage(t *testing.T) {
	// Setup temp dir
	tmpDir, err := os.MkdirTemp("", "storage-test")
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}
	defer func() {
		if err := os.RemoveAll(tmpDir); err != nil {
			log.Error("failed to remove temp dir", "error", err)
		}
	}()

	ds := NewDiskStorage(tmpDir)
	ctx := context.Background()

	filename := "test.txt"
	data := []byte("hello world")
	contentType := "text/plain"

	// 1. Save
	path, err := ds.Save(ctx, filename, data, contentType)
	if err != nil {
		t.Fatalf("Save failed: %v", err)
	}

	// Verify file exists
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Errorf("File was not created at %s", path)
	}

	// 2. Load
	loadedData, err := ds.Load(ctx, path)
	if err != nil {
		t.Fatalf("Load failed: %v", err)
	}
	if string(loadedData) != string(data) {
		t.Errorf("Expected %q, got %q", string(data), string(loadedData))
	}

	// 3. GetPublicURL
	url := ds.GetPublicURL(path)
	if url != "" {
		t.Errorf("Expected empty URL for DiskStorage, got %q", url)
	}
}
