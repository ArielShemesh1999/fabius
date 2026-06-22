package logging

import (
	"log/slog"
	"os"

	charm "github.com/charmbracelet/log"
)

// InitLogging sets up the global logger based on the environment.
func InitLogging(env string) {
	var handler slog.Handler

	if env == "production" {
		// Production: JSON with Severity mapping
		jsonHandler := slog.NewJSONHandler(os.Stderr, &slog.HandlerOptions{
			AddSource: true,
			ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
				switch a.Key {
				case slog.MessageKey:
					a.Key = "message"
				case slog.SourceKey:
					a.Key = "logging.googleapis.com/sourceLocation"
				case slog.LevelKey:
					a.Key = "severity"
				}
				return a
			},
		})
		handler = &CloudLoggingHandler{Handler: jsonHandler, FormatMessage: false}
	} else {
		// Development: Charmbracelet colorful slog
		chOptions := charm.Options{Prefix: "agent", ReportTimestamp: true, Level: charm.DebugLevel}
		cbLogger := charm.NewWithOptions(os.Stderr, chOptions)
		handler = &CloudLoggingHandler{Handler: cbLogger}
	}

	slog.SetDefault(slog.New(handler))
}
