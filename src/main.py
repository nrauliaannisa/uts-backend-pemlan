from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from src.services.target_calculator import TargetCalculator
from src.repositories.data_repository import DataRepository

app = FastAPI(title="Sistem Pencatatan Bacaan dan Target Khatam Al-Qur'an")
calculator = TargetCalculator(total_pages=604)
repo = DataRepository()

class ProgressInput(BaseModel):
    pages_read_today: int

@app.get("/")
def read_root():
    data = repo.load_data()
    status = calculator.calculate_daily_target(
        target_days=data["target_days"],
        current_day=len(data["logs"]) + 1,
        total_pages_read=data["total_pages_read"]
    )
    return {
        "message": "Selamat datang di API Pencatatan Target Khatam Al-Qur'an",
        "current_progress": data,
        "analysis": status
    }

@app.post("/log-reading")
def log_reading(input_data: ProgressInput):
    data = repo.load_data()
    
    remaining_pages = 604 - data["total_pages_read"]
    if input_data.pages_read_today > remaining_pages:
        raise HTTPException(
            status_code=400, 
            detail=f"Jumlah halaman terlalu besar! Sisa halaman yang belum dibaca hanya {remaining_pages} halaman."
        )
    
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
        "message": "Catatan bacaan harian berhasil disimpan!",
        "updated_status": status
    }

@app.post("/dashboard-submit")
def dashboard_submit(pages_read_today: int = Form(...)):
    data = repo.load_data()
    
    remaining_pages = 604 - data["total_pages_read"]
    if pages_read_today > remaining_pages:
        raise HTTPException(
            status_code=400, 
            detail=f"Jumlah halaman terlalu besar! Sisa halaman yang belum dibaca hanya {remaining_pages} halaman."
        )
    
    if pages_read_today <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Jumlah halaman yang dibaca minimal 1 halaman."
        )

    data["total_pages_read"] += pages_read_today
    
    current_day = len(data["logs"]) + 1
    data["logs"].append({
        "day": current_day,
        "pages_added": pages_read_today,
        "total_accumulated": data["total_pages_read"]
    })
    
    repo.save_data(data)
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/dashboard-reset")
def dashboard_reset():
    """Mereset data kembali ke nol (0)"""
    initial_data = {
        "target_days": 30,
        "total_pages_read": 0,
        "logs": []
    }
    repo.save_data(initial_data)
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    data = repo.load_data()
    logs = data.get("logs", [])
    total_read = data['total_pages_read']
    is_completed = total_read >= 604
    
    days_label = [f"Hari ke-{log['day']}" for log in logs]
    pages_data = [log['pages_added'] for log in logs]
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard Mutaba'ah Tilawah Al-Qur'an</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="text-success fw-bold m-0">📖 Dashboard Mutaba'ah Tilawah Al-Qur'an</h2>
                <!-- Tombol Reset Selalu Ada di Pojok Kanan Atas -->
                <form action="/dashboard-reset" method="post" onsubmit="return confirm('Yakin ingin mereset semua data bacaan menjadi 0?');">
                    <button type="submit" class="btn btn-danger fw-bold shadow-sm">🔄 Reset Data ke 0</button>
                </form>
            </div>
    """
    
    # Kondisi jika sudah khatam atau belum
    if is_completed:
        html_content += """
            <div class="alert alert-success text-center p-4 shadow-sm mb-4" role="alert">
                <h3 class="alert-heading fw-bold">🎉 Alhamdulillahi Rabbil 'Alamin! 🎉</h3>
                <p class="fs-5 mb-0">Selamat! Anda telah menyelesaikan target 604 halaman dan <strong>Khatam Al-Qur'an</strong>.</p>
            </div>
        """
    else:
        html_content += f"""
            <div class="row text-center mb-4">
                <div class="col-md-6">
                    <div class="card shadow-sm p-3 bg-white border-success">
                        <h5>Total Halaman Dibaca</h5>
                        <h3 class="text-primary">{total_read} / 604</h3>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card shadow-sm p-3 bg-white border-warning">
                        <h5>Target Waktu</h5>
                        <h3 class="text-warning">{data['target_days']} Hari</h3>
                    </div>
                </div>
            </div>

            <div class="card shadow-sm p-4 mb-4 bg-white border-primary">
                <h4 class="text-primary mb-3">➕ Tambah Catatan Bacaan Hari Ini</h4>
                <form action="/dashboard-submit" method="post" class="row g-3">
                    <div class="col-md-9">
                        <input type="number" class="form-control" name="pages_read_today" placeholder="Masukkan jumlah halaman yang dibaca hari ini..." required min="1" max="{604 - total_read}">
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-success w-100 fw-bold">Simpan & Perbarui</button>
                    </div>
                </form>
            </div>
        """

    html_content += f"""
            <!-- Grafik Peningkatan -->
            <div class="card shadow-sm p-4 mb-4 bg-white">
                <h4 class="mb-3">📈 Grafik Peningkatan Bacaan Harian</h4>
                <canvas id="readingChart" height="100"></canvas>
            </div>

            <!-- Tabel Riwayat -->
            <div class="card shadow-sm p-4 bg-white">
                <h4 class="mb-3">📋 Riwayat Catatan Harian</h4>
                <table class="table table-striped table-hover">
                    <thead class="table-success">
                        <tr>
                            <th>Hari Ke-</th>
                            <th>Halaman Dibaca Hari Ini</th>
                            <th>Total Akumulasi Halaman</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    if not logs:
        html_content += "<tr><td colspan='3' class='text-center text-muted'>Belum ada riwayat bacaan. Silakan isi form di atas!</td></tr>"
    else:
        for log in logs:
            html_content += f"""
                <tr>
                    <td>Hari {log['day']}</td>
                    <td>+{log['pages_added']} halaman</td>
                    <td>{log['total_accumulated']} halaman</td>
                </tr>
            """
            
    html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            const ctx2 = document.getElementById('readingChart').getContext('2d');
            new Chart(ctx2, {{
                type: 'bar',
                data: {{
                    labels: {days_label},
                    datasets: [{{
                        label: 'Halaman Dibaca',
                        data: {pages_data},
                        backgroundColor: 'rgba(25, 135, 84, 0.7)',
                        borderColor: 'rgba(25, 135, 84, 1)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    scales: {{ y: {{ beginAtZero: true }} }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_content