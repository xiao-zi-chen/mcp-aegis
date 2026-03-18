package httpapi

import (
	"encoding/json"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/xiao-zi-chen/mcp-aegis/apps/control-api/internal/store"
)

type Handler struct {
	store store.Store
}

func New(store store.Store) *Handler {
	return &Handler{store: store}
}

func (h *Handler) Routes() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", h.handleHealth)
	mux.HandleFunc("/readyz", h.handleReady)
	mux.HandleFunc("/api/v1/servers", h.handleServers)
	mux.HandleFunc("/api/v1/servers/", h.handleServerByName)
	mux.HandleFunc("/api/v1/policies", h.handlePolicies)
	mux.HandleFunc("/api/v1/policies/", h.handlePolicyByName)
	return mux
}

func (h *Handler) handleHealth(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{
		"status":    "ok",
		"timestamp": time.Now().UTC(),
	})
}

func (h *Handler) handleReady(w http.ResponseWriter, r *http.Request) {
	_, ok, err := h.store.Snapshot(r.Context())
	if err != nil {
		writeError(w, http.StatusInternalServerError, err.Error())
		return
	}

	if !ok {
		writeError(w, http.StatusServiceUnavailable, "registry snapshot not loaded")
		return
	}

	writeJSON(w, http.StatusOK, map[string]string{"status": "ready"})
}

func (h *Handler) handleServers(w http.ResponseWriter, r *http.Request) {
	servers, ok, err := h.store.ListServers(r.Context())
	if err != nil {
		writeError(w, http.StatusInternalServerError, err.Error())
		return
	}

	if !ok {
		writeJSON(w, http.StatusOK, map[string]any{"servers": []any{}})
		return
	}

	query := strings.TrimSpace(r.URL.Query().Get("q"))
	if query != "" {
		query = strings.ToLower(query)
		filtered := servers[:0]
		for _, server := range servers {
			if strings.Contains(strings.ToLower(server.Name), query) || strings.Contains(strings.ToLower(server.Description), query) {
				filtered = append(filtered, server)
			}
		}
		servers = filtered
	}

	writeJSON(w, http.StatusOK, map[string]any{
		"servers": servers,
		"count":   len(servers),
	})
}

func (h *Handler) handleServerByName(w http.ResponseWriter, r *http.Request) {
	name := strings.TrimPrefix(r.URL.Path, "/api/v1/servers/")
	name, err := url.PathUnescape(name)
	if err != nil || name == "" {
		writeError(w, http.StatusBadRequest, "invalid server name")
		return
	}

	server, ok, err := h.store.GetServer(r.Context(), name)
	if err != nil {
		writeError(w, http.StatusInternalServerError, err.Error())
		return
	}

	if !ok {
		writeError(w, http.StatusNotFound, "server not found")
		return
	}

	writeJSON(w, http.StatusOK, server)
}

func (h *Handler) handlePolicies(w http.ResponseWriter, r *http.Request) {
	policies, err := h.store.ListPolicies(r.Context())
	if err != nil {
		writeError(w, http.StatusInternalServerError, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, map[string]any{
		"policies": policies,
		"count":    len(policies),
	})
}

func (h *Handler) handlePolicyByName(w http.ResponseWriter, r *http.Request) {
	name := strings.TrimPrefix(r.URL.Path, "/api/v1/policies/")
	name, err := url.PathUnescape(name)
	if err != nil || name == "" {
		writeError(w, http.StatusBadRequest, "invalid policy name")
		return
	}

	policy, ok, err := h.store.GetPolicy(r.Context(), name)
	if err != nil {
		writeError(w, http.StatusInternalServerError, err.Error())
		return
	}

	if !ok {
		writeError(w, http.StatusNotFound, "policy not found")
		return
	}

	writeJSON(w, http.StatusOK, policy)
}

func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]any{
		"error": map[string]any{
			"status":  status,
			"message": message,
		},
	})
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}
