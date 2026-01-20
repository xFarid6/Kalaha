# Study Guide: LearnGoFlutter

Welcome to your study companion. This document explains the "Why" and "How" of this project.

---

## 1. Philosophies

### Go (The Backend)
**"Clear is better than clever."**
*   **Simplicity**: Go has very few keywords. Notice how `server/cmd/server/main.go` reads line-by-line without complex decorators or hidden magic.
*   **Explicit Error Handling**: We check `if err != nil` everywhere. This forces you to decide what to do when things fail, leading to robust software.
*   **Concurrency**: Go was built for the cloud. The `sync.Mutex` in `internal/store/memory.go` is a primitive that allows safe parallel execution, simpler than Java's synchronized blocks or JS's event loop microtasks.

### Flutter (The Frontend)
**"Everything is a Widget."**
*   **Composition**: Instead of inheritance trees, we compose small widgets (Text, Padding, Column) to build complex UIs. see `mobile/lib/screens/home_screen.dart`.
*   **Declarative UI**: You don't say "remove this row". You change the state (`_notes` list), and Flutter *rebuilds* the UI to match the new state.

---

## 2. Architecture Patterns

### The MVVM Pattern (Frontend)
We use `Provider` to implement Model-View-ViewModel.

1.  **View (`home_screen.dart`)**: The UI. It listens to the Provider.
2.  **ViewModel (`notes_provider.dart`)**: Holds the `List<Note>` and `isLoading` bool. It exposes methods like `fetchNotes()`.
3.  **Model (`note.dart`)**: Pure data structure.

**Why?**
Separation of concerns. The UI doesn't know how HTTP works. The Provider doesn't know what colors the UI uses.

### The Standard Library Pattern (Backend)
We avoided frameworks like Gin or Echo.

1.  **Handlers (`internal/api`)**: Translates HTTP (JSON body) -> Go Structs.
2.  **Store (`internal/store`)**: Handles data logic.

**Why?**
Learning the standard library `net/http` gives you a deeper understanding of HTTP mechanics before using heavy frameworks.

---

## 3. Interaction Mechanics

How do they talk?

1.  **Flutter Request**:
    *   `ApiService` creates a POST request using `http` package.
    *   It parses the Dart Object into a JSON string using `jsonEncode`.
    *   Sends it to `http://localhost:8080/notes`.

2.  **Go Response**:
    *   `Handler` receives the request. `json.NewDecoder` reads the stream.
    *   It validates the data.
    *   It calls `Store.Create`.
    *   It writes back a `201 Created` status and the new JSON object.

3.  **Flutter Update**:
    *   `ApiService` waits for the response `await`.
    *   It returns the new `Note` object.
    *   `NotesProvider` adds it to the list `_notes.add(newNote)`.
    *   `notifyListeners()` triggers the UI to redraw.

---

## 4. Idiomatic Expressions

### Go Idioms
*   **Constructor Functions**: `NewHandler(s store.Store)`. Go doesn't have classes, so we use functions that return pointers to structs.
*   **Interface Injection**: `type Handler struct { Store store.Store }`. We depend on an interface, not a concrete struct. This acts like "Dependency Injection" without a framework.

### Dart Idioms
*   **Async/Await**: `Future<void> fetchNotes() async`. Handles non-blocking I/O.
*   **Null Safety**: `String? _error`. The `?` means it can be null. Dart forces us to check for nulls before using it.
---

## 5. Web Development & CORS

When building for the Web, you will encounter **CORS (Cross-Origin Resource Sharing)**.
*   **The Problem**: A browser at `localhost:8081` (Flutter) is not allowed to talk to `localhost:8080` (Go) unless the server explicitly gives permission.
*   **The Solution**: We added a `CORSMiddleware` in `server/cmd/server/main.go` that adds the `Access-Control-Allow-Origin: *` header.
*   **Production Tip**: In a real app, you would replace `*` with your actual frontend domain for security.
