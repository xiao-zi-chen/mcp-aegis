package httpapi

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/xiao-zi-chen/mcp-aegis/apps/control-api/internal/domain"
)

type fakeStore struct {
	snapshot domain.Snapshot
	ready    bool
	policies []domain.PolicyBundle
}

func (f fakeStore) Snapshot(context.Context) (domain.Snapshot, bool, error) {
	return f.snapshot, f.ready, nil
}

func (f fakeStore) ListServers(context.Context) ([]domain.ServerSummary, bool, error) {
	return f.snapshot.Servers, f.ready, nil
}

func (f fakeStore) GetServer(_ context.Context, name string) (domain.ServerSummary, bool, error) {
	for _, server := range f.snapshot.Servers {
		if server.Name == name {
			return server, true, nil
		}
	}
	return domain.ServerSummary{}, false, nil
}

func (f fakeStore) ListPolicies(context.Context) ([]domain.PolicyBundle, error) {
	return f.policies, nil
}

func (f fakeStore) GetPolicy(_ context.Context, name string) (domain.PolicyBundle, bool, error) {
	for _, policy := range f.policies {
		if policy.Name == name {
			return policy, true, nil
		}
	}
	return domain.PolicyBundle{}, false, nil
}

func TestHandleServers(t *testing.T) {
	h := New(fakeStore{
		ready: true,
		snapshot: domain.Snapshot{
			GeneratedAt: time.Now(),
			Servers: []domain.ServerSummary{
				{Name: "filesystem", Description: "Read files", Version: "1.0.0"},
				{Name: "github", Description: "GitHub API", Version: "2.0.0"},
			},
		},
	})

	req := httptest.NewRequest(http.MethodGet, "/api/v1/servers?q=git", nil)
	rec := httptest.NewRecorder()
	h.Routes().ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("expected status 200, got %d", rec.Code)
	}

	body := rec.Body.String()
	if !strings.Contains(body, `"github"`) {
		t.Fatalf("expected filtered response to contain github, body=%s", body)
	}
	if strings.Contains(body, `"filesystem"`) {
		t.Fatalf("expected filtered response to exclude filesystem, body=%s", body)
	}
}

func TestHandleReadyNotLoaded(t *testing.T) {
	h := New(fakeStore{})

	req := httptest.NewRequest(http.MethodGet, "/readyz", nil)
	rec := httptest.NewRecorder()
	h.Routes().ServeHTTP(rec, req)

	if rec.Code != http.StatusServiceUnavailable {
		t.Fatalf("expected status 503, got %d", rec.Code)
	}
}
