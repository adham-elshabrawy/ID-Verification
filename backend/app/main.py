from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import devices, employees, time_events, embeddings, admin

app = FastAPI(
    title="Kiosk Face Recognition API",
    description="API for employee clock-in/out kiosk system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(devices.router)
app.include_router(employees.router)
app.include_router(time_events.router)
app.include_router(embeddings.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "Kiosk Face Recognition API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

