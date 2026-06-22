package logging

import (
	"context"
	"fmt"
	"log/slog"
	"strings"
)

type CloudLoggingHandler struct {
	Handler       slog.Handler
	FormatMessage bool
}

var _ slog.Handler = (*CloudLoggingHandler)(nil)

func (h *CloudLoggingHandler) Enabled(ctx context.Context, level slog.Level) bool {
	return h.Handler.Enabled(ctx, level)
}

func (h *CloudLoggingHandler) Handle(ctx context.Context, r slog.Record) error {
	// Format Message if enabled (before adding technical attributes like trace)
	if h.FormatMessage {
		var sb strings.Builder
		sb.WriteString(r.Message)
		r.Attrs(func(a slog.Attr) bool {
			sb.WriteString(" ")
			sb.WriteString(a.Key)
			sb.WriteString("=")
			sb.WriteString(fmt.Sprintf("%v", a.Value.Any()))
			return true
		})
		r.Message = sb.String()
	}

	if trace := GetTraceFromContext(ctx); trace != "" {
		r.Add("logging.googleapis.com/trace", slog.StringValue(trace))
	}
	return h.Handler.Handle(ctx, r)
}

func (h *CloudLoggingHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
	return &CloudLoggingHandler{Handler: h.Handler.WithAttrs(attrs), FormatMessage: h.FormatMessage}
}

func (h *CloudLoggingHandler) WithGroup(name string) slog.Handler {
	return &CloudLoggingHandler{Handler: h.Handler.WithGroup(name), FormatMessage: h.FormatMessage}
}
