# LumiQAI Predictive Maintenance Server
# Receives data from Fumax T1 IoT Sensor
# Company: LumiQAI | Hyderabad, India

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI(title="LumiQAI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store last 1000 readings in memory
sensor_data = []

# Fumax T1 JSON format
class SensorReading(BaseModel):
    device_id: Optional[str] = "lumiqai-001"
    timestamp: Optional[int] = None
    accel_x: Optional[float] = 0.0
    accel_y: Optional[float] = 0.0
    accel_z: Optional[float] = 0.0
    vibration_rms: Optional[float] = 0.0
    temp_onboard: Optional[float] = 0.0
    temp_external: Optional[float] = 0.0
    current: Optional[float] = 0.0
    humidity: Optional[float] = 0.0
    pressure: Optional[float] = 0.0
    light: Optional[float] = 0.0
    battery: Optional[float] = 100.0

# Receive data from Fumax T1
@app.post("/api/sensor-data")
async def receive_data(reading: SensorReading):
    if not reading.timestamp:
        reading.timestamp = int(datetime.now().timestamp())
    data = reading.dict()
    sensor_data.append(data)
    if len(sensor_data) > 1000:
        sensor_data.pop(0)
    alerts = check_alerts(data)
    print(f"LumiQAI Data Received — "
          f"Temp: {data['temp_external']}°C | "
          f"Vibration RMS: {data['vibration_rms']} | "
          f"Current: {data['current']}A")
    return {
        "status": "success",
        "message": "Data received by LumiQAI server",
        "alerts": alerts
    }

# Send last 100 readings to dashboard
@app.get("/api/sensor-data")
async def get_data():
    return {
        "status": "success",
        "count": len(sensor_data),
        "readings": sensor_data[-100:]
    }

# Get only the latest reading
@app.get("/api/latest")
async def get_latest():
    if not sensor_data:
        return {"status": "no data yet", "readings": []}
    return {
        "status": "success",
        "latest": sensor_data[-1]
    }

# Health check
@app.get("/")
async def health_check():
    return {
        "status": "LumiQAI server is running",
        "company": "LumiQAI",
        "total_readings": len(sensor_data),
        "timestamp": datetime.now().isoformat()
    }

# Alert logic
def check_alerts(data):
    alerts = []
    if data["temp_external"] > 45.0:
        alerts.append({
            "type": "HIGH_TEMPERATURE",
            "message": f"Machine temperature is {data['temp_external']}°C — above normal",
            "severity": "WARNING"
        })
    if data["vibration_rms"] > 15.0:
        alerts.append({
            "type": "HIGH_VIBRATION",
            "message": f"Vibration RMS is {data['vibration_rms']} — above normal",
            "severity": "WARNING"
        })
    if data["current"] > 10.0:
        alerts.append({
            "type": "HIGH_CURRENT",
            "message": f"Current is {data['current']}A — above normal",
            "severity": "WARNING"
        })
    return alerts
