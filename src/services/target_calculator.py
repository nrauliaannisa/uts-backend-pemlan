import math

class TargetCalculator:
    def __init__(self, total_pages: int = 604):
        self.total_pages = total_pages

    def calculate_daily_target(self, target_days: int, current_day: int, total_pages_read: int) -> dict:
        """
        Menghitung target harian secara dinamis berdasarkan sisa halaman dan sisa hari.
        """
        # Pengecekan jika sudah khatam (Skenario khatam cepat)
        if total_pages_read >= self.total_pages:
            return {
                "status": "COMPLETED",
                "remaining_pages": 0,
                "remaining_days": max(0, target_days - current_day),
                "daily_target_needed": 0,
                "message": "Alhamdulillah, target khatam telah tercapai!"
            }

        remaining_pages = self.total_pages - total_pages_read
        remaining_days = target_days - current_day

        # Mencegah pembagian dengan nol jika hari sudah habis tapi belum khatam
        if remaining_days <= 0:
            return {
                "status": "EXPIRED",
                "remaining_pages": remaining_pages,
                "remaining_days": 0,
                "daily_target_needed": remaining_pages,
                "message": "Waktu target telah habis. Tetap semangat melanjutkannya!"
            }

        # Hitung target dinamis untuk hari-hari berikutnya (pembulatan ke atas)
        daily_target_needed = math.ceil(remaining_pages / remaining_days)

        return {
            "status": "IN_PROGRESS",
            "remaining_pages": remaining_pages,
            "remaining_days": remaining_days,
            "daily_target_needed": daily_target_needed,
            "message": f"Sisa {remaining_pages} halaman dalam {remaining_days} hari ke depan."
        }