# Android Kiosk Face Recognition System

Employee clock-in/clock-out system using automatic face recognition for Android tablets in kiosk mode.

## Project Structure

- `backend/` - Python FastAPI backend with PostgreSQL
- `android/` - Android tablet kiosk application

## Quick Start (Testing on Laptop)

### Backend Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set up database:**
   - Install PostgreSQL
   - Create database: `CREATE DATABASE kiosk_db;`
   - Copy `.env.example` to `.env` and configure

3. **Run migrations:**
```bash
alembic upgrade head
```

4. **Start server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Test the API:**
   - Open http://localhost:8000/docs (interactive API docs)
   - Or run: `python test_backend.py`

### Android App Testing

**Option 1: Android Studio Emulator**
1. Install Android Studio
2. Create tablet emulator (API 26+)
3. Open `android/` in Android Studio
4. Update `ApiClient.kt`: `BASE_URL = "http://10.0.2.2:8000/api/"`
5. Run on emulator

**Option 2: Physical Device**
1. Enable USB debugging on device
2. Find your laptop's IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
3. Update `ApiClient.kt`: `BASE_URL = "http://YOUR_IP:8000/api/"`
4. Connect device and run

See [docs/SETUP.md](docs/SETUP.md) for detailed setup instructions.

## Features

- Automatic face recognition for employee identification
- Clock in/out functionality
- PIN fallback authentication
- Admin mode for employee management
- Daily CSV exports via email
- Offline support with sync
- Kiosk/lock-task mode

## Security

- Encrypted face embeddings (AES-256-GCM)
- API key authentication
- TLS for all communication
- Android Keystore for secure key storage

## License

Proprietary

