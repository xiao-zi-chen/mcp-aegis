package domain

type AuditEvent struct {
	EventType   string         `json:"eventType"`
	GeneratedAt string         `json:"generatedAt"`
	SourceFile  string         `json:"sourceFile"`
	Data        map[string]any `json:"data"`
}
