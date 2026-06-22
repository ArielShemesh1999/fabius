package tools

import (
	"context"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/memory"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

type mockToolContext struct {
	context.Context
}

func (m mockToolContext) Actions() *session.EventActions {
	return nil
}

func (m mockToolContext) FunctionCallID() string {
	return "test-call-id"
}

func (m mockToolContext) AgentName() string {
	return "test-agent"
}

func (m mockToolContext) AppName() string {
	return "test-app"
}

func (m mockToolContext) Artifacts() agent.Artifacts {
	return nil
}

func (m mockToolContext) Branch() string {
	return "test-branch"
}

func (m mockToolContext) InvocationID() string {
	return "test-invocation-id"
}

func (m mockToolContext) ReadonlyState() session.ReadonlyState {
	return nil
}

func (m mockToolContext) SearchMemory(ctx context.Context, query string) (*memory.SearchResponse, error) {
	return nil, nil
}

func (m mockToolContext) SessionID() string {
	return "test-session-id"
}

func (m mockToolContext) State() session.State {
	return nil
}

func (m mockToolContext) UserContent() *genai.Content {
	return nil
}

func (m mockToolContext) UserID() string {
	return "test-user-id"
}

func int32Ptr(i int32) *int32 {
	return &i
}
