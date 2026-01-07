# Quick Start Guide - Testing on Your Laptop

## Step 1: Test the Backend API

### Prerequisites
- Python 3.9+ installed
- PostgreSQL installed and running

### Setup Backend

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set up PostgreSQL:**
   - Install PostgreSQL if not already installed
   - Create database:
     ```sql
     CREATE DATABASE kiosk_db;
     ```

3. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Edit `.env` and set your database credentials:
     ```
     DATABASE_URL=postgresql://postgres:your_password@localhost/kiosk_db
     SECRET_KEY=your-32-byte-random-key-here
     LOG_LEVEL=INFO
     ```
   - Generate SECRET_KEY:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```

4. **Initialize database:**
```bash
cd backend
alembic upgrade head
```

If this fails (no migrations yet), create the initial migration:
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

5. **Start the server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Test the API:**
   - Open browser: http://localhost:8000/docs
   - Or run the test script: `python test_backend.py`

The interactive API docs at `/docs` let you test all endpoints directly in your browser!

## Step 2: Test the Android App

### Option A: Android Studio Emulator (Easiest)

1. **Install Android Studio**
   - Download: https://developer.android.com/studio
   - Install with default settings

2. **Create Emulator:**
   - Open Android Studio
   - Tools → Device Manager
   - Create Virtual Device
   - Choose "Tablet" → "Pixel Tablet" or "Nexus 10"
   - System Image: API 26 or higher
   - Finish

3. **Configure App:**
   - Open `android/` folder in Android Studio
   - Edit `app/src/main/java/com/kiosk/network/ApiClient.kt`
   - Change line with BASE_URL to:
     ```kotlin
     private const val BASE_URL = "http://10.0.2.2:8000/api/"
     ```
   - (10.0.2.2 is the emulator's way to access your laptop's localhost)

4. **Run:**
   - Click the green "Run" button
   - Select your emulator
   - App will install and launch

### Option B: Physical Android Device

1. **Enable Developer Mode:**
   - Settings → About Phone
   - Tap "Build Number" 7 times
   - Settings → Developer Options → Enable "USB Debugging"

2. **Connect Device:**
   - Connect via USB
   - Accept debugging prompt on phone/tablet

3. **Configure Network:**
   - Find your laptop's IP address:
     - Windows: Open CMD, run `ipconfig`, look for "IPv4 Address"
     - Mac/Linux: Run `ifconfig` or `ip addr`
   - Edit `ApiClient.kt`:
     ```kotlin
     private const val BASE_URL = "http://192.168.1.XXX:8000/api/"
     ```
     (Replace XXX with your actual IP)

4. **Run:**
   - In Android Studio, select your device
   - Click Run

## Testing Checklist

### Backend API Testing (via Browser)
1. ✅ Open http://localhost:8000/docs
2. ✅ Test `/health` endpoint
3. ✅ Register a device: `POST /api/devices/register`
4. ✅ Copy the API key from response
5. ✅ Click "Authorize" button (top right)
6. ✅ Enter: `Bearer YOUR_API_KEY` (or just `YOUR_API_KEY`)
7. ✅ Create an employee: `POST /api/employees`
8. ✅ Create a time event: `POST /api/time-events`
9. ✅ Check clocked-in employees: `GET /api/time-events/clocked-in`

### Android App Testing
1. ✅ Launch app
2. ✅ Device registration screen appears
3. ✅ Enter location name, register
4. ✅ Home screen with Clock In/Out buttons
5. ✅ Tap Clock In → Camera opens
6. ✅ Test camera capture
7. ✅ Long press for admin mode

## Troubleshooting

### Backend won't start
- **Port 8000 in use?** Change port: `--port 8001`
- **Database error?** Check PostgreSQL is running and DATABASE_URL is correct
- **Import errors?** Make sure you're in the `backend/` directory

### Android can't connect to backend
- **Emulator:** Must use `10.0.2.2` not `localhost`
- **Physical device:** Use your laptop's IP address, ensure both devices on same WiFi
- **Firewall:** Allow port 8000 in Windows Firewall
- **Backend not accessible?** Use `--host 0.0.0.0` when starting uvicorn

### Build errors in Android Studio
- File → Sync Project with Gradle Files
- Build → Clean Project
- Build → Rebuild Project

## What to Test

1. **Device Registration Flow**
   - First launch should prompt for registration
   - Register with location name
   - API key stored securely

2. **Clock In/Out Flow**
   - Tap Clock In button
   - Camera activates
   - Capture face (or skip if model not available)
   - Confirmation screen
   - Event created in backend

3. **Admin Features**
   - Long press to access admin
   - View employees
   - Create employees
   - View time events

## Next Steps

Once basic functionality works:
- Add face recognition model (MobileFaceNet TFLite)
- Configure SendGrid for email exports
- Set up production database
- Deploy backend to cloud (Heroku, AWS, etc.)

For detailed setup, see [docs/SETUP.md](docs/SETUP.md)

