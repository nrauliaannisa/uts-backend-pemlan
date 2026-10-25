import pytest
from src.services.target_calculator import TargetCalculator

def test_initial_target_calculation():
    calc = TargetCalculator(total_pages=604)
    result = calc.calculate_daily_target(target_days=30, current_day=1, total_pages_read=0)
    
    assert result["status"] == "IN_PROGRESS"
    assert result["remaining_pages"] == 604
    assert result["daily_target_needed"] == 21  # 604 / 30 dibulatkan ke atas

def test_early_completion_khatam():
    calc = TargetCalculator(total_pages=604)
    # Skenario user sudah membaca 604 halaman pada hari ke-28
    result = calc.calculate_daily_target(target_days=30, current_day=28, total_pages_read=604)
    
    assert result["status"] == "COMPLETED"
    assert result["daily_target_needed"] == 0
    assert "Alhamdulillah" in result["message"]