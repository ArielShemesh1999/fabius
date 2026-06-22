package logging

import (
	"context"
)

type key int

const (
	traceKey key = iota
)

// AddTraceToContext adds the trace to the context
func AddTraceToContext(ctx context.Context, trace string) context.Context {
	return context.WithValue(ctx, traceKey, trace)
}

// GetTraceFromContext returns the trace from the context
func GetTraceFromContext(ctx context.Context) string {
	trace, ok := ctx.Value(traceKey).(string)
	if !ok {
		return ""
	}
	return trace
}
