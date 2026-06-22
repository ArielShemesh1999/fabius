package server

import (
	"net/http"

	"navallist/internal/agent"
	"navallist/internal/config"
	"navallist/internal/data"
	"navallist/internal/realtime"
	"navallist/internal/server/handlers"

	"github.com/centrifugal/centrifuge"
)

// Server holds dependencies for the HTTP server.
type Server struct {
	Store       data.Store
	Config      *config.Config
	Mux         *http.ServeMux
	AgentClient *agent.LocalAgentClient
	Storage     data.BlobStorage
	FrontendFS  http.FileSystem
}

// Route definition
type route struct {
	Verb      string
	Path      string
	Handler   http.HandlerFunc
	AuthLevel int
}

// Authorization levels
const (
	// AuthLevelPublic allows access without authentication.
	AuthLevelPublic = 0
)

// NewServer initializes the server with routes.
func NewServer(store data.Store, cfg *config.Config, agentClient *agent.LocalAgentClient, storage data.BlobStorage, frontendFS http.FileSystem) *Server {
	mux := http.NewServeMux()

	s := &Server{
		Mux:         mux,
		Store:       store,
		Config:      cfg,
		AgentClient: agentClient,
		Storage:     storage,
		FrontendFS:  frontendFS,
	}

	s.registerRoutes()
	return s
}

func (s *Server) registerRoutes() {
	// Initialize handlers
	authHandler := handlers.NewAuthHandler(s.Store)
	tripsHandler := handlers.NewTripsHandler(s.Store, s.AgentClient, s.Storage)

	routes := []route{
		// Health
		{Verb: "GET", Path: "/healthz", Handler: func(w http.ResponseWriter, _ *http.Request) {
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte("OK"))
		}, AuthLevel: AuthLevelPublic},

		// Auth Routes (Simplified)
		{Verb: "GET", Path: "/auth/logout", Handler: authHandler.Logout, AuthLevel: AuthLevelPublic},
		{Verb: "GET", Path: "/auth/me", Handler: authHandler.GetMe, AuthLevel: AuthLevelPublic},
		{Verb: "PUT", Path: "/auth/me", Handler: authHandler.UpdateMe, AuthLevel: AuthLevelPublic},

		// Trip Routes
		{Verb: "GET", Path: "/api/trips", Handler: tripsHandler.ListTrips, AuthLevel: AuthLevelPublic},
		{Verb: "POST", Path: "/api/trips", Handler: tripsHandler.CreateTrip, AuthLevel: AuthLevelPublic},
		{Verb: "GET", Path: "/api/trips/{id}", Handler: tripsHandler.GetTrip, AuthLevel: AuthLevelPublic},
		{Verb: "PUT", Path: "/api/trips/{id}/items/{itemId}", Handler: tripsHandler.UpdateItem, AuthLevel: AuthLevelPublic},
		{Verb: "POST", Path: "/api/trips/{id}/items/{itemId}/photo", Handler: tripsHandler.UploadItemPhoto, AuthLevel: AuthLevelPublic},
		{Verb: "DELETE", Path: "/api/trips/{id}", Handler: tripsHandler.DeleteTrip, AuthLevel: AuthLevelPublic},
		{Verb: "GET", Path: "/api/trips/{id}/status", Handler: tripsHandler.UpdateStatus, AuthLevel: AuthLevelPublic},
		{Verb: "PATCH", Path: "/api/trips/{id}/status", Handler: tripsHandler.UpdateStatus, AuthLevel: AuthLevelPublic},
		{Verb: "PATCH", Path: "/api/trips/{id}/type", Handler: tripsHandler.UpdateType, AuthLevel: AuthLevelPublic},
		{Verb: "GET", Path: "/api/trips/{id}/report", Handler: tripsHandler.GetReport, AuthLevel: AuthLevelPublic},
		{Verb: "GET", Path: "/api/artifacts", Handler: tripsHandler.GetArtifact, AuthLevel: AuthLevelPublic},
	}

	for _, r := range routes {
		// Go 1.22+ routing: "METHOD /path"
		pattern := r.Verb + " " + r.Path
		// Wrap with middleware based on AuthLevel
		s.Mux.HandleFunc(pattern, s.AuthMiddleware(r.AuthLevel, r.Handler))
	}

	// Agent Routes
	checklistHandler := handlers.NewChecklistHandler(s.AgentClient, s.Store)

	agentRoutes := []route{
		{Verb: "POST", Path: "/api/agent/sessions", Handler: checklistHandler.CreateSession, AuthLevel: AuthLevelPublic},
		{Verb: "GET", Path: "/api/agent/sessions/{sessionID}", Handler: checklistHandler.GetSession, AuthLevel: AuthLevelPublic},
		{Verb: "POST", Path: "/api/agent/run", Handler: checklistHandler.RunInteraction, AuthLevel: AuthLevelPublic},
	}

	for _, r := range agentRoutes {
		pattern := r.Verb + " " + r.Path
		s.Mux.HandleFunc(pattern, s.AuthMiddleware(r.AuthLevel, r.Handler))
	}

	// Serve Static Frontend
	s.Mux.Handle("/", http.FileServer(s.FrontendFS))
}

func (s *Server) MountWebSocket(rtService *realtime.Service) {
	wsHandler := centrifuge.NewWebsocketHandler(rtService.Node, centrifuge.WebsocketConfig{
		CheckOrigin: func(_ *http.Request) bool {
			return true // Allow all origins for now
		},
	})
	s.Mux.Handle("/connection/websocket", s.PermissiveAuthMiddleware(wsHandler.ServeHTTP))
}
