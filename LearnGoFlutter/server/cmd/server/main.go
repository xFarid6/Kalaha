package main

import (
	"learn-go-flutter/internal/api"
	"learn-go-flutter/internal/store"
	"log"
	"net/http"
	"time"
)

// CORSMiddleware handles Cross-Origin Resource Sharing.
// This is essential for web browsers to allow requests from a frontend on a different port.
func CORSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// allow all origins for study purposes
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

		// If it's an OPTIONS request (pre-flight), return immediately with 200
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

// LoggerMiddleware wraps a handler and logs every request.
func LoggerMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		log.Printf("Started %s %s", r.Method, r.URL.Path)

		next.ServeHTTP(w, r)

		log.Printf("Completed %s %s in %v", r.Method, r.URL.Path, time.Since(start))
	})
}

func main() {
	// 1. Initialize Dependencies
	store := store.NewInMemoryStore()
	handler := api.NewHandler(store)

	// 2. Setup Router (ServeMux)
	mux := http.NewServeMux()

	// 3. Register Routes
	// Note: In Go 1.22+, you can matching methods like "GET /notes" directly in the pattern.
	// But to be safe for older versions we'll check methods in the handler or use distinct paths.
	// Here we used a single function per endpoint strategy in the handler struct.
	mux.HandleFunc("/notes", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			handler.GetNotes(w, r)
		case http.MethodPost:
			handler.CreateNote(w, r)
		case http.MethodDelete:
			handler.DeleteNote(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	// 4. Wrap Global Middleware
	// Order matters: CORSMiddleware usually goes first to handle pre-flights early.
	finalHandler := CORSMiddleware(LoggerMiddleware(mux))

	// 5. Start Server
	port := ":8080"
	log.Printf("Server starting on http://localhost%s", port)
	if err := http.ListenAndServe(port, finalHandler); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
