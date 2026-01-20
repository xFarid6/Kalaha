package models

// Note represents a single item in our notebook.
// We use struct tags (backticks) to tell Go's JSON encoder
// how to name the fields.
type Note struct {
	ID    string `json:"id"`
	Title string `json:"title"`
	Body  string `json:"body"`
}
