package domain

import "time"

type Assessment struct {
	ReportVersion       string           `json:"reportVersion"`
	GeneratedAt         time.Time        `json:"generatedAt"`
	ScannerName         string           `json:"scannerName"`
	ScannerVersion      string           `json:"scannerVersion"`
	Server              AssessmentServer `json:"server"`
	ScanReport          ScanReport       `json:"scanReport"`
	RiskScore           RiskScore        `json:"riskScore"`
	PolicyDecision      PolicyDecision   `json:"policyDecision"`
	RuntimePlan         map[string]any   `json:"runtimePlan"`
	RuntimeCapabilities map[string]any   `json:"runtimeCapabilities"`
	SandboxSpec         map[string]any   `json:"sandboxSpec"`
	LaunchAuditEvent    map[string]any   `json:"launchAuditEvent"`
	LaunchResult        map[string]any   `json:"launchResult"`
	RuntimeLaunchEvent  map[string]any   `json:"runtimeLaunchEvent"`
	RecommendedActions  []string         `json:"recommendedActions"`
}

type AssessmentServer struct {
	Name              string   `json:"name"`
	Version           string   `json:"version,omitempty"`
	Registry          string   `json:"registry,omitempty"`
	TargetPath        string   `json:"targetPath,omitempty"`
	Transport         []string `json:"transport,omitempty"`
	OwnershipVerified bool     `json:"ownershipVerified"`
	RemoteURL         string   `json:"remoteUrl,omitempty"`
}

type ScanReport struct {
	TargetPath   string        `json:"targetPath"`
	FindingCount int           `json:"findingCount"`
	Findings     []ScanFinding `json:"findings"`
}

type ScanFinding struct {
	FindingKey  string         `json:"finding_key"`
	Severity    string         `json:"severity"`
	Confidence  string         `json:"confidence"`
	Category    string         `json:"category"`
	Title       string         `json:"title"`
	Detail      string         `json:"detail"`
	FilePath    string         `json:"file_path"`
	Line        int            `json:"line"`
	Evidence    map[string]any `json:"evidence"`
	Remediation string         `json:"remediation"`
}

type RiskScore struct {
	Score          float64        `json:"score"`
	DecisionClass  string         `json:"decisionClass"`
	EvidenceCount  int            `json:"evidenceCount"`
	SeverityCounts map[string]int `json:"severityCounts"`
	CategoryCounts map[string]int `json:"categoryCounts"`
}

type PolicyDecision struct {
	Bundle           string   `json:"bundle"`
	BundleVersion    int      `json:"bundleVersion"`
	Decision         string   `json:"decision"`
	RuntimeProfile   string   `json:"runtimeProfile"`
	RemoteAccess     string   `json:"remoteAccess"`
	RequireDigestPin bool     `json:"requireDigestPin"`
	MatchedRules     []string `json:"matchedRules"`
	Reasons          []string `json:"reasons"`
}
