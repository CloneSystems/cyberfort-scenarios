// CyberGuard SIEM Manager v1.0 — reference manager binary.
//
// This is a minimal stand-in used by the CyberFort cyber-range Scenario 04.
// The goal is to give the CyberFort scanners (Nmap, ZAP) a real HTTP target
// while the trainee focuses on the CRA conformity assessment for a SIEM
// product placed on the EU market. It is not the real CyberGuard code —
// see https://github.com/CyberGuardEU/t4.4_siem_ai_remediation for that.
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

const (
	productName    = "CyberGuard SIEM Manager"
	productVersion = "1.0.0"
)

type versionInfo struct {
	Product       string    `json:"product"`
	Version       string    `json:"version"`
	Build         string    `json:"build"`
	StartedAt     time.Time `json:"started_at"`
	SBOMPublished bool      `json:"sbom_published"`
	CVDContact    string    `json:"coordinated_vulnerability_disclosure"`
}

var startedAt = time.Now().UTC()

func handleVersion(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(versionInfo{
		Product:       productName,
		Version:       productVersion,
		Build:         "reference-lab-build",
		StartedAt:     startedAt,
		SBOMPublished: true,
		CVDContact:    "security@cyberguard.example",
	})
}

func handleAgents(w http.ResponseWriter, r *http.Request) {
	// Small mock endpoint so ZAP has something to spider.
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]any{
		"count":  0,
		"agents": []any{},
		"note":   "This reference build ships without pre-registered agents. See docs/installation.",
	})
}

func handleAlerts(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]any{"alerts": []any{}})
}

func handleHealthz(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_, _ = fmt.Fprintln(w, `{"status":"ok"}`)
}

func main() {
	mux := http.NewServeMux()
	mux.Handle("/", http.FileServer(http.Dir("/srv/static")))
	mux.HandleFunc("/api/version", handleVersion)
	mux.HandleFunc("/api/agents", handleAgents)
	mux.HandleFunc("/api/alerts", handleAlerts)
	mux.HandleFunc("/healthz", handleHealthz)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("%s %s listening on :%s", productName, productVersion, port)
	if err := http.ListenAndServe(":"+port, mux); err != nil {
		log.Fatal(err)
	}
}
