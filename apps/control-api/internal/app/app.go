package app

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/xiao-zi-chen/mcp-aegis/apps/control-api/internal/config"
	"github.com/xiao-zi-chen/mcp-aegis/apps/control-api/internal/httpapi"
	"github.com/xiao-zi-chen/mcp-aegis/apps/control-api/internal/store/filestore"
)

type App struct {
	server *http.Server
	grace  time.Duration
}

func New(cfg config.Config) (*App, error) {
	store := filestore.New(cfg.SnapshotPath, cfg.PoliciesDir)
	handler := httpapi.New(store)

	server := &http.Server{
		Addr:         cfg.Address,
		Handler:      handler.Routes(),
		ReadTimeout:  cfg.ReadTimeout,
		WriteTimeout: cfg.WriteTimeout,
	}

	return &App{server: server, grace: cfg.ShutdownGrace}, nil
}

func (a *App) Run(ctx context.Context) error {
	errCh := make(chan error, 1)

	go func() {
		slog.Info("starting control-api", "address", a.server.Addr)
		if err := a.server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- fmt.Errorf("listen: %w", err)
			return
		}
		errCh <- nil
	}()

	select {
	case <-ctx.Done():
		shutdownCtx, cancel := context.WithTimeout(context.Background(), a.grace)
		defer cancel()
		return a.server.Shutdown(shutdownCtx)
	case err := <-errCh:
		return err
	}
}
