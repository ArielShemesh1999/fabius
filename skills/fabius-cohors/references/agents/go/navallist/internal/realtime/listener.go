package realtime

import (
	"context"
	"encoding/json"
	"time"

	"github.com/charmbracelet/log"
	"github.com/jackc/pgx/v5"
)

// DBEvent represents an event received from the database.
type DBEvent struct {
	Table  string          `json:"table"`
	Action string          `json:"action"`
	Data   json.RawMessage `json:"data"`
	TripID string          `json:"trip_id"`
}

// ListenToDB starts a loop to listen for database notifications and publish them to Centrifuge.
func (s *Service) ListenToDB(ctx context.Context, connStr string) {
	// Loop to handle reconnection
	for {
		select {
		case <-ctx.Done():
			log.Info("Stopping DB listener")
			return
		default:
			err := s.listenLoop(ctx, connStr)
			if err != nil {
				log.Error("DB Listener failed, retrying in 5s", "error", err)
				time.Sleep(5 * time.Second)
			}
		}
	}
}

func (s *Service) listenLoop(ctx context.Context, connStr string) error {
	conn, err := pgx.Connect(ctx, connStr)
	if err != nil {
		return err
	}
	defer func() {
		if err := conn.Close(ctx); err != nil {
			log.Error("failed to close database connection", "error", err)
		}
	}()

	_, err = conn.Exec(ctx, "LISTEN db_events")
	if err != nil {
		return err
	}

	log.Info("Listening for Postgres notifications on channel 'db_events'")

	for {
		notification, err := conn.WaitForNotification(ctx)
		if err != nil {
			return err
		}

		var event DBEvent
		if err := json.Unmarshal([]byte(notification.Payload), &event); err != nil {
			log.Error("Failed to parse notification", "payload", notification.Payload, "error", err)
			continue
		}

		// We only care about events with a TripID
		if event.TripID == "" {
			continue
		}

		channel := "trip:" + event.TripID

		_, err = s.Node.Publish(channel, []byte(notification.Payload))
		if err != nil {
			log.Error("Failed to publish to Centrifuge", "channel", channel, "error", err)
		}
	}
}
