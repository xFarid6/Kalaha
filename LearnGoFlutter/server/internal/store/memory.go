package store

import (
	"errors"
	"learn-go-flutter/internal/models"
	"sync"

	"github.com/google/uuid"
)

var (
	ErrNotFound = errors.New("note not found")
)

// Store defines the behavior we expect from our data layer.
// By using an interface, we can easily swap this In-Memory
// version for a SQL version later.
type Store interface {
	GetAll() ([]models.Note, error)
	Create(note models.Note) (models.Note, error)
	Delete(id string) error
}

// InMemoryStore is an implementation of Store that keeps data in RAM.
// It uses a Mutex because a web server handles requests concurrently.
type InMemoryStore struct {
	// RWMutex allows multiple readers OR one writer.
	// Perfect for "Read frequent, Write occasional" APIs.
	mu    sync.RWMutex
	notes map[string]models.Note
}

// NewInMemoryStore initializes the map.
func NewInMemoryStore() *InMemoryStore {
	return &InMemoryStore{
		notes: make(map[string]models.Note),
	}
}

func (s *InMemoryStore) GetAll() ([]models.Note, error) {
	s.mu.RLock()         // Lock for Reading (allows other readers)
	defer s.mu.RUnlock() // Unlock when function exits

	// Convert map to slice
	list := make([]models.Note, 0, len(s.notes))
	for _, note := range s.notes {
		list = append(list, note)
	}
	return list, nil
}

func (s *InMemoryStore) Create(note models.Note) (models.Note, error) {
	s.mu.Lock() // Lock for Writing (blocks everyone else)
	defer s.mu.Unlock()

	// Simple ID generation
	note.ID = uuid.New().String()
	s.notes[note.ID] = note
	return note, nil
}

func (s *InMemoryStore) Delete(id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.notes[id]; !exists {
		return ErrNotFound
	}
	delete(s.notes, id)
	return nil
}
