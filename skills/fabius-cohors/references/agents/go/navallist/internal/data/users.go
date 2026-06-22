package data

import (
	"context"

	"navallist/internal/data/models"
)

// GetUser retrieves a user by ID.
func (s *SQLStore) GetUser(ctx context.Context, id string) (*models.User, error) {
	user := &models.User{}
	query := `SELECT * FROM users WHERE id = $1`
	err := s.db.GetContext(ctx, user, query, id)
	if err != nil {
		return nil, err
	}
	return user, nil
}

// FindUserByName retrieves a user by their name (case-insensitive).
func (s *SQLStore) FindUserByName(ctx context.Context, name string) (*models.User, error) {
	user := &models.User{}
	query := `SELECT * FROM users WHERE LOWER(name) = LOWER($1) LIMIT 1`
	err := s.db.GetContext(ctx, user, query, name)
	if err != nil {
		return nil, err
	}
	return user, nil
}

// UpdateUser updates the user's name.
func (s *SQLStore) UpdateUser(ctx context.Context, id, name string) error {
	query := `UPDATE users SET name = $1 WHERE id = $2`
	_, err := s.db.ExecContext(ctx, query, name, id)
	return err
}
