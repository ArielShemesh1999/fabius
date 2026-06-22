package realtime

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"

	"navallist/internal/data"

	"github.com/centrifugal/centrifuge"
	"github.com/charmbracelet/log"
)

// Service handles real-time communication via Centrifuge.
type Service struct {
	Node  *centrifuge.Node
	Store data.Store
}

// NewService initializes a new real-time service with the given store.
func NewService(store data.Store) (*Service, error) {
	node, err := centrifuge.New(centrifuge.Config{
		LogLevel: centrifuge.LogLevelDebug,
		LogHandler: func(entry centrifuge.LogEntry) {
			// Using fmt to ensure it prints to stdout/stderr visible in logs
			log.Infof("centrifuge: %s %v", entry.Message, entry.Fields)
		},
	})
	if err != nil {
		return nil, err
	}

	service := &Service{
		Node:  node,
		Store: store,
	}

	// OnConnecting is where we authenticate the user based on the context populated by middleware
	node.OnConnecting(service.HandleConnect)

	// OnConnect is called after successful authentication
	node.OnConnect(func(client *centrifuge.Client) {
		log.Info("Realtime: OnConnect called", "user", client.UserID())

		client.OnSubscribe(func(e centrifuge.SubscribeEvent, cb centrifuge.SubscribeCallback) {
			// Channel format: "trip:{trip_id}"
			if !strings.HasPrefix(e.Channel, "trip:") {
				cb(centrifuge.SubscribeReply{}, fmt.Errorf("invalid channel format"))
				return
			}

			tripID := strings.TrimPrefix(e.Channel, "trip:")

			// Verify access using the store
			trip, err := store.GetTrip(context.Background(), tripID)
			if err != nil {
				cb(centrifuge.SubscribeReply{}, centrifuge.ErrorPermissionDenied)
				return
			}

			// If trip exists, allow subscription.
			_ = trip // unused variable for now

			// Try to fetch initial presence list from server-side to bypass potential client-side restriction
			var initialPresence []byte
			res, err := node.Presence(e.Channel)
			if err == nil {
				// We need to marshal just the map to match client expectation
				if res.Presence == nil {
					initialPresence = []byte("{}")
				} else {
					initialPresence, _ = json.Marshal(res.Presence)
				}
			} else {
				log.Warn("Failed to fetch initial presence on server", "error", err)
				initialPresence = []byte("{}")
			}

			cb(centrifuge.SubscribeReply{
				Options: centrifuge.SubscribeOptions{
					EmitPresence:  true,
					EmitJoinLeave: true,
					PushJoinLeave: true,
					Data:          initialPresence,
				},
			}, nil)
		})
	})

	if err := node.Run(); err != nil {
		return nil, err
	}

	return service, nil
}

// HandleConnect authenticates the user based on the context populated by middleware.
func (s *Service) HandleConnect(ctx context.Context, e centrifuge.ConnectEvent) (centrifuge.ConnectReply, error) {
	userID := data.GetUserID(ctx)
	guestName := data.GetGuestName(ctx)

	transportName := "unknown"
	if e.Transport != nil {
		transportName = e.Transport.Name()
	}

	log.Info("Realtime: OnConnecting called",
		"transport", transportName,
		"userID", userID,
		"guestName", guestName)

	if userID == "" && guestName == "" {
		log.Info("Realtime: Anonymous connection", "transport", transportName)
		// Return empty credentials for anonymous access
		return centrifuge.ConnectReply{
			Credentials: &centrifuge.Credentials{
				UserID: "",
			},
		}, nil
	}

	var userData []byte

	// If Guest
	if userID == "" && guestName != "" {
		// Ensure we don't double-prefix if guestName already has it
		cleanName := strings.TrimPrefix(guestName, "guest_")
		guestID := "guest_" + cleanName

		info := map[string]string{"name": cleanName}
		userData, _ = json.Marshal(info)

		return centrifuge.ConnectReply{
			Credentials: &centrifuge.Credentials{
				UserID: guestID,
				Info:   userData,
			},
		}, nil
	}

	// Fetch User Name to send as Client Info
	user, err := s.Store.GetUser(context.Background(), userID)
	if err == nil && user.Name != nil {
		// Format: {"name": "Captain Steve"}
		info := map[string]string{"name": *user.Name}
		userData, _ = json.Marshal(info)
	} else {
		// Fallback to ID if name not found or error
		info := map[string]string{"name": userID}
		userData, _ = json.Marshal(info)
	}

	return centrifuge.ConnectReply{
		Credentials: &centrifuge.Credentials{
			UserID: userID,
			Info:   userData,
		},
	}, nil
}
