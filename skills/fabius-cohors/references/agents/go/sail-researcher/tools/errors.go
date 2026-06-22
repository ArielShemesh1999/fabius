package tools

import "errors"

var (
	// ErrNotFound is returned when a requested resource (like a tide station or place) cannot be found.
	ErrNotFound = errors.New("resource not found")
	// ErrInvalidDate is returned when a date string is provided in an incorrect format.
	ErrInvalidDate = errors.New("invalid date format")
	// ErrAPIUnavailable is returned when an external API call fails.
	ErrAPIUnavailable = errors.New("external API error")
)
