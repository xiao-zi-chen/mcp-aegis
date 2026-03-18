package store

import (
	"context"

	"github.com/xiao-zi-chen/mcp-aegis/apps/control-api/internal/domain"
)

type Store interface {
	Snapshot(ctx context.Context) (domain.Snapshot, bool, error)
	ListServers(ctx context.Context) ([]domain.ServerSummary, bool, error)
	GetServer(ctx context.Context, name string) (domain.ServerSummary, bool, error)
	ListPolicies(ctx context.Context) ([]domain.PolicyBundle, error)
	GetPolicy(ctx context.Context, name string) (domain.PolicyBundle, bool, error)
}
