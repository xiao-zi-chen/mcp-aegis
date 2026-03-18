package config

import (
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"time"
)

type Config struct {
	Address       string
	ReadTimeout   time.Duration
	WriteTimeout  time.Duration
	ShutdownGrace time.Duration
	SnapshotPath  string
	PoliciesDir   string
}

func Load() (Config, error) {
	cfg := Config{
		Address:       envOrDefault("MCP_AEGIS_API_ADDRESS", ":8080"),
		ReadTimeout:   5 * time.Second,
		WriteTimeout:  10 * time.Second,
		ShutdownGrace: 10 * time.Second,
		SnapshotPath:  envOrDefault("MCP_AEGIS_SNAPSHOT_PATH", "services/registry-sync/examples/latest.json"),
		PoliciesDir:   envOrDefault("MCP_AEGIS_POLICIES_DIR", "packages/policy-spec/examples"),
	}

	if value := os.Getenv("MCP_AEGIS_API_READ_TIMEOUT_SECONDS"); value != "" {
		seconds, err := strconv.Atoi(value)
		if err != nil {
			return Config{}, fmt.Errorf("invalid MCP_AEGIS_API_READ_TIMEOUT_SECONDS: %w", err)
		}
		cfg.ReadTimeout = time.Duration(seconds) * time.Second
	}

	if value := os.Getenv("MCP_AEGIS_API_WRITE_TIMEOUT_SECONDS"); value != "" {
		seconds, err := strconv.Atoi(value)
		if err != nil {
			return Config{}, fmt.Errorf("invalid MCP_AEGIS_API_WRITE_TIMEOUT_SECONDS: %w", err)
		}
		cfg.WriteTimeout = time.Duration(seconds) * time.Second
	}

	cfg.SnapshotPath = resolveRepoPath(cfg.SnapshotPath)
	cfg.PoliciesDir = resolveRepoPath(cfg.PoliciesDir)

	return cfg, nil
}

func envOrDefault(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}

	return fallback
}

func resolveRepoPath(target string) string {
	if filepath.IsAbs(target) {
		return target
	}

	if _, err := os.Stat(target); err == nil {
		return target
	}

	workingDir, err := os.Getwd()
	if err != nil {
		return target
	}

	dir := workingDir
	for {
		candidate := filepath.Join(dir, target)
		if _, err := os.Stat(candidate); err == nil {
			return candidate
		}

		if _, err := os.Stat(filepath.Join(dir, ".git")); err == nil {
			return candidate
		}

		parent := filepath.Dir(dir)
		if parent == dir {
			return target
		}
		dir = parent
	}
}
