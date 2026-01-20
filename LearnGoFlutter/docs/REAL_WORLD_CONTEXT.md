# Real World Context: Study vs Production

This document outlines the **intentional simplifications ("corners cut")** made in this project to maximize learning clarity, and how they would differ in a large-scale production system.

## 1. Data Storage

| Feature | **LearnGoFlutter (Study)** | **Production Grade** |
| :--- | :--- | :--- |
| **Strategy** | **In-Memory (`map` + `Mutex`)**. Data is lost when server stops. | **Persistent Database**. (PostgreSQL, MySQL, MongoDB). |
| **Why?** | Zero setup required. Demonstrates Go concurrency primitives (`sync.RWMutex`) directly. | Data persistence, complex queries, ACID transactions, backups. |
| **Upgrade Path** | Replace the `Store` interface implementation with one that talks to `database/sql`. |

## 2. Configuration

| Feature | **LearnGoFlutter (Study)** | **Production Grade** |
| :--- | :--- | :--- |
| **Strategy** | **Hardcoded / Simple Flags**. Ports and hosts are string literals. | **Environment Variables / Config Files**. (Tools: `Viper`, `Godotenv`, `k8s ConfigMaps`). |
| **Why?** | Keeps code readable and "click-to-run" without creating inputs. | Security (secrets), deploying to different environments (Dev/Stage/Prod) without recompiling. |

## 3. Libraries vs Standard Library

| Feature | **LearnGoFlutter (Study)** | **Production Grade** |
| :--- | :--- | :--- |
| **Routing** | **`net/http`**. Go's standard library router. | **Frameworks** (e.g., `Gin`, `Echo`, `Fiber`). |
| **Why?** | Important to learn the core language first. Frameworks hide HTTP mechanics. | Frameworks provide precooked middleware (CORS, Rate Limiting, RequestID) and faster routing trees. |

## 4. Authentication

| Feature | **LearnGoFlutter (Study)** | **Production Grade** |
| :--- | :--- | :--- |
| **Strategy** | **None**. Open API. | **OAuth2 / OIDC / JWT**. |
| **Why?** | Auth adds massive complexity (Tokens, Flows, encryption). We focus on Architecture here. | Identify users, secure resources, role-based access control (RBAC). |

## 5. Logging & Observability

| Feature | **LearnGoFlutter (Study)** | **Production Grade** |
| :--- | :--- | :--- |
| **Strategy** | **`log.Println`**. Standard output. | **Structured Logging** (`slog`, `Zap`) + **Tracing** (OpenTelemetry). |
| **Why?** | Immediate feedback in the console. | Machine-parseable logs for centralized dashboards (Datadog, Grafana, ELK). |

## Summary

This app builds a **Clean Architecture**. The logical separation (Handlers <-> Store <-> Models) is **Production Grade**.
However, the *implementations* of those layers are **Educational Grade** (simplified for readability and zero-dependency).
