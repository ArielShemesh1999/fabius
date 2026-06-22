//go:build integration

package data

import (
	"context"
	"os"
	"testing"

	_ "github.com/jackc/pgx/v5/stdlib"
	"github.com/jmoiron/sqlx"
)

// setupTestDB connects to the test database and returns the connection.
// It skips the test if the connection fails.
func setupTestDB(t *testing.T) *sqlx.DB {
	t.Helper()
	dsn := os.Getenv("NAVALLIST_DB_CONNECTION_STRING")
	if dsn == "" {
		dsn = "postgres://navallist_user:password@localhost:5432/navallistdb?sslmode=disable"
	}
	db, err := sqlx.Connect("pgx", dsn)
	if err != nil {
		t.Skipf("Skipping integration test: %v", err)
	}
	return db
}

// cleanupData removes data created during tests.
func cleanupData(t *testing.T, db *sqlx.DB, tables ...string) {
	t.Helper()
	ctx := context.Background()
	for _, table := range tables {
		_, err := db.ExecContext(ctx, "DELETE FROM "+table)
		if err != nil {
			t.Logf("Failed to cleanup table %s: %v", table, err)
		}
	}
}