# Setup and Testing Guide

## Backend Setup (Local Testing)

### Prerequisites
- Python 3.9+ installed
- PostgreSQL installed and running
- (Optional) PostgreSQL client tools

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Database

1. Create a PostgreSQL database:
```sql
CREATE DATABASE kiosk_db;
```

2. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

3. Edit `.env` with your database credentials:
```env
DATABASE_URL=postgresql://your_user:your_password@localhost/kiosk_db
SECRET_KEY=your-32-byte-random-key-here-change-in-production
SENDGRID_API_KEY=your_sendgrid_api_key_here
LOG_LEVEL=INFO
ENCRYPTION_KEY_ID=v1
```

Generate a secure SECRET_KEY:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Step 3: Run Database Migrations

```bash
cd backend
alembic upgrade head
```

If migrations don't exist yet, create initial migration:
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Step 4: Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Step 5: Test the Backend

#### Option A: Using the Interactive API Docs
1. Open http://localhost:8000/docs in your browser
2. Try the `/health` endpoint first
3. Register a test device using `POST /api/devices/register`

#### Option B: Using curl
```bash
# Health check
curl http://localhost:8000/health

# Register a device
curl -X POST "http://localhost:8000/api/devices/register" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device-001",
    "location_name": "Test Location",
    "name": "Test Tablet"
  }'
```

## Android App Setup

### Option 1: Android Studio Emulator (Recommended for Testing)

1. **Install Android Studio**
   - Download from https://developer.android.com/studio
   - Install with Android SDK and emulator support

2. **Create an Android Virtual Device (AVD)**
   - Open Android Studio
   - Tools → Device Manager
   - Create Virtual Device
   - Choose a tablet device (e.g., Pixel Tablet or Nexus 10)
   - Select a system image (API 26+ recommended)
   - Finish setup

3. **Configure the App**
   - Open the `android/` folder in Android Studio
   - Update `ApiClient.kt` with your backend URL:
     ```kotlin
     private const val BASE_URL = "http://10.0.2.2:8000/api/"  // 10.0.2.2 is emulator's localhost
     ```
   
   For a physical device on the same network:
   ```kotlin
   private const val BASE_URL = "http://YOUR_LAPTOP_IP:8000/api/"
   ```

4. **Build and Run**
   - Click Run or press Shift+F10
   - Select your emulator
   - App will install and launch

### Option 2: Physical Android Device

1. **Enable Developer Options**
   - Settings → About Phone
   - Tap "Build Number" 7 times
   - Developer options will appear

2. **Enable USB Debugging**
   - Settings → Developer Options
   - Enable "USB Debugging"

3. **Connect Device**
   - Connect via USB
   - Accept debugging prompt on device

4. **Configure Network**
   - Update `ApiClient.kt` with your laptop's IP:
     ```kotlin
     private const val BASE_URL = "http://YOUR_LAPTOP_IP:8000/api/"
     ```
   - Find your IP: 
     - Windows: `ipconfig` (look for IPv4 Address)
     - Mac/Linux: `ifconfig` or `ip addr`

5. **Run from Android Studio**
   - Select your physical device
   - Click Run

### Option 3: APK Build (For Testing on Any Device)

Build an APK for manual installation:

```bash
cd android
./gradlew assembleDebug
```

APK will be at: `android/app/build/outputs/apk/debug/app-debug.apk`

Install on device:
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Testing Workflow

### 1. Backend Testing (API)

Test the complete flow using the API docs:

1. **Register Device**
   - POST `/api/devices/register`
   - Save the returned `api_key`

2. **Create Employee**
   - Use the API key in header: `X-Device-API-Key: your_api_key`
   - POST `/api/employees`
   - Create a test employee

3. **Store Face Embedding** (You'll need to generate test embeddings)
   - POST `/api/employees/{id}/embedding`

4. **Create Time Event**
   - POST `/api/time-events`
   - Test clock in/out

### 2. Android App Testing

1. **First Launch**
   - App should prompt for device registration
   - Enter location name
   - Device registers with backend

2. **Clock In/Out Flow**
   - Tap "Clock In" or "Clock Out"
   - Camera opens
   - Capture face (or skip if no face model)
   - Confirm action

3. **Admin Mode**
   - Long press on home screen
   - Enter manager PIN
   - Access admin features

## Quick Test Script

Create a simple Python test script:

```python
# test_backend.py
import requests

BASE_URL = "http://localhost:8000"

# 1. Health check
response = requests.get(f"{BASE_URL}/health")
print("Health:", response.json())

# 2. Register device
response = requests.post(
    f"{BASE_URL}/api/devices/register",
    json={
        "device_id": "test-device-001",
        "location_name": "Test Office",
        "name": "Test Tablet"
    }
)
print("Device Registration:", response.json())
api_key = response.json()["api_key"]

# 3. Get device info
headers = {"X-Device-API-Key": api_key}
response = requests.get(f"{BASE_URL}/api/devices/me", headers=headers)
print("Device Info:", response.json())
```

Run it:
```bash
pip install requests
python test_backend.py
```

## Troubleshooting

### Backend Issues

**Database connection errors:**
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists

**Port already in use:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# Change port:
uvicorn app.main:app --port 8001
```

### Android Issues

**Cannot connect to backend:**
- Check firewall settings (allow port 8000)
- For emulator: use `10.0.2.2` instead of `localhost`
- For physical device: use laptop's local IP address
- Ensure backend is running

**Build errors:**
- Sync Gradle files in Android Studio
- Clean and rebuild: Build → Clean Project, then Build → Rebuild Project

**Camera not working:**
- Emulator: Camera might not be available, use physical device
- Physical device: Grant camera permissions

## Next Steps

1. Test backend API endpoints using the interactive docs
2. Set up Android emulator or connect physical device
3. Test device registration flow
4. Test clock in/out functionality
5. Test admin features

For production deployment, see `docs/DEPLOYMENT.md` (to be created).

