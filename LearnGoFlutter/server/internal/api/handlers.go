package api

import (
	"encoding/json"
	"learn-go-flutter/internal/models"
	"learn-go-flutter/internal/store"
	"net/http"
)

// Handler holds dependencies for our HTTP endpoints.
// We inject the Store interface so we can easily test with mocks later.
type Handler struct {
	Store store.Store
}

func NewHandler(s store.Store) *Handler {
	return &Handler{Store: s}
}

// GetNotes handles GET /notes.
// usage: curl http://localhost:8080/notes
func (h *Handler) GetNotes(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	notes, err := h.Store.GetAll()
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	// json.NewEncoder streams data directly to the writer
	// (memory efficient)
	json.NewEncoder(w).Encode(notes)
}

// CreateNote handles POST /notes.
// usage: curl -X POST -d '{"title":"Hi","body":"World"}' http://localhost:8080/notes
func (h *Handler) CreateNote(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var note models.Note
	// Decode the incoming JSON body into our struct
	if err := json.NewDecoder(r.Body).Decode(&note); err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	if note.Title == "" {
		http.Error(w, "Title is required", http.StatusBadRequest)
		return
	}

	createdNote, err := h.Store.Create(note)
	if err != nil {
		http.Error(w, "Failed to create note", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(createdNote)
}

// DeleteNote handles DELETE /notes?id=...
func (h *Handler) DeleteNote(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodDelete {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	id := r.URL.Query().Get("id")
	if id == "" {
		http.Error(w, "Missing 'id' query parameter", http.StatusBadRequest)
		return
	}

	err := h.Store.Delete(id)
	if err == store.ErrNotFound {
		http.Error(w, "Note not found", http.StatusNotFound)
		return
	}
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}
