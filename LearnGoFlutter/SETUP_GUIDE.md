# Setup Guide: LearnGoFlutter

This guide will help you set up your development environment to run the Go backend and Flutter frontend.

## 1. Prerequisites

### Install Go (Backend)
1.  **Download**: Visit the official [Go Download Page](https://go.dev/dl/).
2.  **OS**: Choose the **Microsoft Windows** installer MSI (e.g., `go1.22.x.windows-amd64.msi`).
3.  **Install**: Run the installer and follow the prompts.
4.  **Verify**: Open a **new** PowerShell terminal and run:
    ```powershell
    go version
    ```
    *Output should look like: `go version go1.22.0 windows/amd64`*

### Install Flutter (Frontend)
1.  **Download**: Visit the [Flutter Install for Windows](https://docs.flutter.dev/get-started/install/windows/mobile).
2.  **Extract**: Download the zip and extract it to a valid path (e.g., `C:\src\flutter`). **Do not** install it in `C:\Program Files`.
3.  **Path**: Add the `flutter\bin` directory to your User Path environment variable.
4.  **Verify**: Open a **new** PowerShell terminal and run:
    ```powershell
    flutter doctor
    ```
    *This will check for dependencies like Android Studio or Visual Studio components.*

### VSCode Extensions
For the best experience, install these extensions:
1.  **Go** (golang.go) - For Go language support.
2.  **Flutter** (Dart-Code.flutter) - For Flutter and Dart support.
3.  **Dart** (Dart-Code.dart-code) - Included with the Flutter extension.

## 2. Running the Application

### 1. Start the Backend (Go)
Open a terminal in the `server/` directory:
```powershell
cd server
go run ./cmd/server/main.go
```
*The server will start on http://localhost:8080*

### 2. Start the Frontend (Mobile)
Open a terminal in the `mobile/` directory:
```powershell
cd mobile
flutter run
```
*You will be asked to select a device (Windows Desktop, Chrome, or an Android Emulator).*

## 3. Emulators vs Real Devices
- **Windows Desktop**: Easiest to test. Just choose "Windows" when `flutter run` asks.
- **Android Emulator**: Requires Android Studio. Good for testing mobile UI.
- **Real Device**:
    1.  Enable "Developer Options" & "USB Debugging" on your Android phone.
    2.  Connect via USB.
    3.  Run `flutter devices` to see its ID.
    4.  Run `flutter run -d <DeviceId>`.
