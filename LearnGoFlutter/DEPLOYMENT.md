# Deployment & Porting Guide

This document explains how to take the source code of **LearnGoFlutter** and build it for different platforms (Mobile, Desktop, Web).

## 1. Code Reuse Analysis

*   **Go Backend**: 100% Reusable logic.
    *   *Changes needed*: configuration (e.g., listening on `0.0.0.0` instead of `localhost` for remote access).
*   **Flutter Frontend**: 95% Reusable code.
    *   *Shared*: All business logic, UI layouts, State management.
    *   *Specifics*: App icons, Permission configurations (`Info.plist` for iOS, `AndroidManifest.xml` for Android).

---

## 2. Building the Backend (Go)

Go is famous for its **Cross-Compilation**. You can build a binary for any OS *from* any OS.

### Build specific artifacts
From the `server/` directory:

**For Windows (Executable .exe)**
```powershell
go build -o server.exe ./cmd/server/main.go
```

**For Linux (e.g., to run on a cheap cloud VPS)**
```powershell
$env:GOOS = "linux"
$env:GOARCH = "amd64"
go build -o server-linux ./cmd/server/main.go
# Then upload 'server-linux' to your VPS.
```

**For macOS (Apple Silicon)**
```powershell
$env:GOOS = "darwin"
$env:GOARCH = "arm64"
go build -o server-mac ./cmd/server/main.go
```

---

## 3. Building the Frontend (Flutter)

Flutter compiles to native machine code for each platform.

### A. Android (.apk)
1.  Ensure you have the Android SDK installed.
2.  Run:
    ```powershell
    flutter build apk --release
    ```
3.  **Output**: `build/app/outputs/flutter-apk/app-release.apk`
4.  *Usage*: Copy this file to any Android phone and install it.

### B. Windows Desktop (.exe)
1.  Enable Windows support: `flutter config --enable-windows-desktop`
2.  Run:
    ```powershell
    flutter build windows --release
    ```
3.  **Output**: `build/windows/runner/Release/`
4.  *Usage*: You need the entire folder, not just the .exe, as it contains DLLs and assets.

### C. Web (SPA)
1.  Run:
    ```powershell
    flutter build web --release
    ```
2.  **Output**: `build/web/`
3.  *Usage*: Upload this folder to any static host (Netlify, Vercel, GitHub Pages).

### D. iOS (.ipa)
*Requirement*: You **must** rely on a macOS machine with Xcode installed. You cannot build iOS apps from Windows.
1.  Run `flutter build ios --release` on a Mac.

---

## 4. Connecting the Pieces

When you deploy:
1.  **Host the Go Server**: Put the Linux binary on a cloud provider (AWS, DigitalOcean, Google Cloud) or use a container (Docker).
2.  **Update the URL**: In the Flutter app (`api_service.dart`), change `localhost` to your cloud server's public IP or Domain (e.g., `https://api.myapp.com`).
3.  **Distribute the App**: Send the APK/Exe to users.

> **Note on Localhost**:
> *   `localhost` on Windows = Your PC.
> *   `localhost` on Android Emulator = The Emulator itself.
> *   To access your PC from Android Emulator, use **`10.0.2.2`**.
> *   To access your PC from a Real Phone, ensure both are on the same Wi-Fi and use your PC's local IP (e.g., `192.168.1.5`).
