from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.services.target_calculator import TargetCalculator
from src.repositories.data_repository import DataRepository

app = FastAPI(title="Sistem Pencatatan Bacaan dan Target Khatam Al-Qur'an")
calculator = TargetCalculator(total_pages=604)
repo = DataRepository()

class ProgressInput(BaseModel):
    pages_read_today: int

class TargetInput(BaseModel):
    target_days: int

# 1. GET (Melihat data & status progres)
@app.get("/")
def get_progress():
    """Mengambil status progres dan analisis target tilawah (GET)"""
    data = repo.load_data()
    status = calculator.calculate_daily_target(
        target_days=data["target_days"],
        current_day=len(data["logs"]) + 1,
        total_pages_read=data["total_pages_read"]
    )
    return {
        "message": "Data progres tilawah berhasil dimuat",
        "current_progress": data,
        "analysis": status
    }

# 2. POST (Menambah catatan bacaan harian)
@app.post("/readings")
def add_reading(input_data: ProgressInput):
    """Menambah catatan halaman bacaan harian (POST)"""
    data = repo.load_data()
    remaining_pages = 604 - data["total_pages_read"]
    
    if input_data.pages_read_today > remaining_pages:
        raise HTTPException(
            status_code=400, 
            detail=f"Sisa halaman hanya {remaining_pages} halaman!"
        )
    if input_data.pages_read_today <= 0:
        raise HTTPException(status_code=400, detail="Minimal baca 1 halaman.")
    
    data["total_pages_read"] += input_data.pages_read_today
    current_day = len(data["logs"]) + 1
    data["logs"].append({
        "day": current_day,
        "pages_added": input_data.pages_read_today,
        "total_accumulated": data["total_pages_read"]
    })
    repo.save_data(data)
    
    status = calculator.calculate_daily_target(
        target_days=data["target_days"],
        current_day=current_day,
        total_pages_read=data["total_pages_read"]
    )
    return {
        "message": "Catatan bacaan berhasil disimpan!",
        "updated_status": status
    }

# 3. PUT (Mengubah target hari)
@app.put("/target")
def update_target(input_data: TargetInput):
    """Mengubah target hari khatam (PUT)"""
    data = repo.load_data()
    data["target_days"] = input_data.target_days
    repo.save_data(data)
    return {
        "message": f"Target berhasil diubah menjadi {input_data.target_days} hari.",
        "current_data": data
    }

# 4. DELETE (Mereset seluruh data dan riwayat kembali ke 0)
@app.delete("/readings")
def reset_all_readings():
    """Mereset seluruh riwayat bacaan dan total halaman kembali ke 0 (DELETE)"""
    initial_data = {
        "target_days": 30,
        "total_pages_read": 0,
        "logs": []
    }
    repo.save_data(initial_data)
    return {
        "message": "Semua riwayat berhasil dihapus dan data dikembalikan ke 0.",
        "current_data": initial_data
    }