package domain

import "time"

type Snapshot struct {
	GeneratedAt time.Time       `json:"generatedAt"`
	Source      SnapshotSource  `json:"source"`
	Servers     []ServerSummary `json:"servers"`
}

type SnapshotSource struct {
	Registry string `json:"registry"`
	BaseURL  string `json:"baseUrl"`
}

type ServerSummary struct {
	ID          string       `json:"id"`
	Name        string       `json:"name"`
	Description string       `json:"description"`
	Version     string       `json:"version"`
	SchemaURL   string       `json:"schemaUrl"`
	WebsiteURL  string       `json:"websiteUrl,omitempty"`
	Repository  Repository   `json:"repository"`
	Transports  []Transport  `json:"transports"`
	Registry    RegistryMeta `json:"registry"`
}

type Repository struct {
	URL       string `json:"url,omitempty"`
	Source    string `json:"source,omitempty"`
	ID        string `json:"id,omitempty"`
	Subfolder string `json:"subfolder,omitempty"`
}

type Transport struct {
	Type string `json:"type"`
	URL  string `json:"url,omitempty"`
}

type RegistryMeta struct {
	Status          string     `json:"status"`
	PublishedAt     *time.Time `json:"publishedAt,omitempty"`
	UpdatedAt       *time.Time `json:"updatedAt,omitempty"`
	StatusChangedAt *time.Time `json:"statusChangedAt,omitempty"`
	IsLatest        bool       `json:"isLatest"`
}

type PolicyBundle struct {
	Name        string `json:"name"`
	Version     int    `json:"version"`
	Description string `json:"description,omitempty"`
	APIVersion  string `json:"apiVersion"`
	Kind        string `json:"kind"`
	SourcePath  string `json:"sourcePath"`
	RawDocument string `json:"rawDocument"`
}
