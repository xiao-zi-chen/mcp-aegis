package filestore

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"github.com/xiao-zi-chen/mcp-aegis/apps/control-api/internal/domain"
	"github.com/xiao-zi-chen/mcp-aegis/apps/control-api/internal/store"
)

var _ store.Store = (*Store)(nil)

type Store struct {
	snapshotPath string
	policiesDir  string
	reportsDir   string
}

func New(snapshotPath, policiesDir, reportsDir string) *Store {
	return &Store{
		snapshotPath: snapshotPath,
		policiesDir:  policiesDir,
		reportsDir:   reportsDir,
	}
}

func (s *Store) Snapshot(_ context.Context) (domain.Snapshot, bool, error) {
	bytes, err := os.ReadFile(s.snapshotPath)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return domain.Snapshot{}, false, nil
		}
		return domain.Snapshot{}, false, fmt.Errorf("read snapshot: %w", err)
	}

	var snapshot domain.Snapshot
	if err := json.Unmarshal(bytes, &snapshot); err != nil {
		return domain.Snapshot{}, false, fmt.Errorf("decode snapshot: %w", err)
	}

	sort.Slice(snapshot.Servers, func(i, j int) bool {
		return snapshot.Servers[i].Name < snapshot.Servers[j].Name
	})

	return snapshot, true, nil
}

func (s *Store) ListServers(ctx context.Context) ([]domain.ServerSummary, bool, error) {
	snapshot, ok, err := s.Snapshot(ctx)
	if err != nil || !ok {
		return nil, ok, err
	}

	return snapshot.Servers, true, nil
}

func (s *Store) GetServer(ctx context.Context, name string) (domain.ServerSummary, bool, error) {
	servers, ok, err := s.ListServers(ctx)
	if err != nil || !ok {
		return domain.ServerSummary{}, ok, err
	}

	for _, server := range servers {
		if server.Name == name {
			return server, true, nil
		}
	}

	return domain.ServerSummary{}, false, nil
}

func (s *Store) ListPolicies(_ context.Context) ([]domain.PolicyBundle, error) {
	entries, err := os.ReadDir(s.policiesDir)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, nil
		}
		return nil, fmt.Errorf("read policies dir: %w", err)
	}

	policies := make([]domain.PolicyBundle, 0, len(entries))
	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}

		if !strings.HasSuffix(entry.Name(), ".yaml") && !strings.HasSuffix(entry.Name(), ".yml") {
			continue
		}

		policy, err := loadPolicy(filepath.Join(s.policiesDir, entry.Name()))
		if err != nil {
			return nil, err
		}
		policies = append(policies, policy)
	}

	sort.Slice(policies, func(i, j int) bool {
		return policies[i].Name < policies[j].Name
	})

	return policies, nil
}

func (s *Store) GetPolicy(ctx context.Context, name string) (domain.PolicyBundle, bool, error) {
	policies, err := s.ListPolicies(ctx)
	if err != nil {
		return domain.PolicyBundle{}, false, err
	}

	for _, policy := range policies {
		if policy.Name == name {
			return policy, true, nil
		}
	}

	return domain.PolicyBundle{}, false, nil
}

func (s *Store) ListAssessments(_ context.Context) ([]domain.Assessment, error) {
	entries, err := os.ReadDir(s.reportsDir)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, nil
		}
		return nil, fmt.Errorf("read reports dir: %w", err)
	}

	assessments := make([]domain.Assessment, 0, len(entries))
	for _, entry := range entries {
		if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".json") {
			continue
		}

		assessment, ok, err := loadAssessment(filepath.Join(s.reportsDir, entry.Name()))
		if err != nil {
			return nil, err
		}
		if !ok {
			continue
		}
		assessments = append(assessments, assessment)
	}

	sort.Slice(assessments, func(i, j int) bool {
		if assessments[i].Server.Name == assessments[j].Server.Name {
			return assessments[i].GeneratedAt.After(assessments[j].GeneratedAt)
		}
		return assessments[i].Server.Name < assessments[j].Server.Name
	})

	return assessments, nil
}

func (s *Store) GetAssessment(ctx context.Context, serverName string) (domain.Assessment, bool, error) {
	assessments, err := s.ListAssessments(ctx)
	if err != nil {
		return domain.Assessment{}, false, err
	}

	for _, assessment := range assessments {
		if assessment.Server.Name == serverName {
			return assessment, true, nil
		}
	}

	return domain.Assessment{}, false, nil
}

func loadPolicy(path string) (domain.PolicyBundle, error) {
	bytes, err := os.ReadFile(path)
	if err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return domain.PolicyBundle{}, nil
		}
		return domain.PolicyBundle{}, fmt.Errorf("read policy %s: %w", path, err)
	}

	apiVersion, kind, name, version, description := extractPolicyMetadata(string(bytes))

	return domain.PolicyBundle{
		Name:        name,
		Version:     version,
		Description: description,
		APIVersion:  apiVersion,
		Kind:        kind,
		SourcePath:  path,
		RawDocument: string(bytes),
	}, nil
}

func loadAssessment(path string) (domain.Assessment, bool, error) {
	bytes, err := os.ReadFile(path)
	if err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return domain.Assessment{}, false, nil
		}
		return domain.Assessment{}, false, fmt.Errorf("read assessment %s: %w", path, err)
	}

	var assessment domain.Assessment
	if err := json.Unmarshal(bytes, &assessment); err != nil {
		return domain.Assessment{}, false, fmt.Errorf("decode assessment %s: %w", path, err)
	}

	if assessment.Server.Name == "" {
		return domain.Assessment{}, false, nil
	}

	return assessment, true, nil
}

func extractPolicyMetadata(document string) (apiVersion, kind, name string, version int, description string) {
	lines := strings.Split(document, "\n")
	inMetadata := false

	for _, rawLine := range lines {
		line := strings.TrimRight(rawLine, "\r")
		trimmed := strings.TrimSpace(line)
		if trimmed == "" || strings.HasPrefix(trimmed, "#") {
			continue
		}

		if !strings.HasPrefix(line, " ") && !strings.HasPrefix(line, "\t") {
			inMetadata = trimmed == "metadata:"
			if key, value, ok := splitKeyValue(trimmed); ok {
				switch key {
				case "apiVersion":
					apiVersion = value
				case "kind":
					kind = value
				}
			}
			continue
		}

		if !inMetadata {
			continue
		}

		if key, value, ok := splitKeyValue(trimmed); ok {
			switch key {
			case "name":
				name = value
			case "version":
				parsed, err := strconv.Atoi(value)
				if err == nil {
					version = parsed
				}
			case "description":
				description = value
			}
		}
	}

	return apiVersion, kind, name, version, description
}

func splitKeyValue(line string) (key, value string, ok bool) {
	parts := strings.SplitN(line, ":", 2)
	if len(parts) != 2 {
		return "", "", false
	}

	key = strings.TrimSpace(parts[0])
	value = strings.Trim(strings.TrimSpace(parts[1]), `"'`)
	return key, value, true
}
