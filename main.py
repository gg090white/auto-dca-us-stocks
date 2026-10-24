
"""
AUTO DCA US STOCKS V1.0
หุ้นเป้าหมาย: ASML และ NVDA
งบลงทุน: 2,000 บาทต่อเดือน
โหมด: PAPER / READ-ONLY
ยังไม่ส่งคำสั่งซื้อขายจริง
"""

from datetime import datetime, timezone

import yfinance as yf


# ==========================================
# 1. ตั้งค่าระบบ
# ==========================================

WATCHLIST = ["ASML", "NVDA"]

MONTHLY_BUDGET_THB = 2000.00

ALLOCATION = {
    "ASML": 0.50,
    "NVDA": 0.50,
}

# แบ่งเงินเฝ้าซื้อแนวรับ 3 ชั้น
SUPPORT_ALLOCATION = {
    1: 0.40,
    2: 0.35,
    3: 0.25,
}

# ปิดการซื้อขายเงินจริงไว้เสมอในเวอร์ชันนี้
LIVE_TRADING_ENABLED = False


# ==========================================
# 2. ตรวจสอบการตั้งค่า
# ==========================================

def validate_config():
    if abs(sum(ALLOCATION.values()) - 1.0) > 0.000001:
        raise ValueError("สัดส่วนหุ้นต้องรวมกันเท่ากับ 100%")

    if abs(sum(SUPPORT_ALLOCATION.values()) - 1.0) > 0.000001:
        raise ValueError("สัดส่วนแนวรับต้องรวมกันเท่ากับ 100%")

    if MONTHLY_BUDGET_THB <= 0:
        raise ValueError("งบลงทุนต้องมากกว่า 0")

    if LIVE_TRADING_ENABLED:
        raise RuntimeError(
            "เวอร์ชันนี้ไม่อนุญาตให้ส่งคำสั่งซื้อขายเงินจริง"
        )


# ==========================================
# 3. ดึงราคาหุ้นย้อนหลัง
# ==========================================

def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)

        # ใช้ข้อมูลรายวันย้อนหลังประมาณ 6 เดือน
        data = ticker.history(
            period="6mo",
            interval="1d",
            auto_adjust=True
        )

        if data.empty:
            print(f"[ERROR] {symbol}: ไม่พบข้อมูลราคา")
            return None

        data = data.dropna(subset=["Close"])

        if data.empty:
            print(f"[ERROR] {symbol}: ไม่มีราคาปิดที่ใช้งานได้")
            return None

        latest = data.iloc[-1]

        return {
            "symbol": symbol,
            "price": float(latest["Close"]),
            "date": str(data.index[-1].date()),
            "history": data,
        }

    except Exception as error:
        print(f"[ERROR] ดึงข้อมูล {symbol} ไม่สำเร็จ: {error}")
        return None


# ==========================================
# 4. คำนวณแนวรับเบื้องต้น 3 ชั้น
# ==========================================

def calculate_supports(data):
    """
    แนวรับเบื้องต้นจากจุดต่ำสุดย้อนหลัง
    20, 60 และ 120 วันซื้อขาย

    เป็นระดับสำหรับเฝ้าดู ไม่ใช่การรับประกัน
    ว่าราคาจะหยุดลงหรือกลับตัวที่ระดับดังกล่าว
    """

    history = data["history"]
    price = data["price"]

    support_1 = float(history["Low"].tail(20).min())
    support_2 = float(history["Low"].tail(60).min())
    support_3 = float(history["Low"].tail(120).min())

    return {
        "S1": support_1,
        "S2": support_2,
        "S3": support_3,
        "price": price,
    }


# ==========================================
# 5. คำนวณงบประมาณ
# ==========================================

def calculate_budget(symbol):
    stock_budget = MONTHLY_BUDGET_THB * ALLOCATION[symbol]

    return {
        "total": stock_budget,
        "support_1": stock_budget * SUPPORT_ALLOCATION[1],
        "support_2": stock_budget * SUPPORT_ALLOCATION[2],
        "support_3": stock_budget * SUPPORT_ALLOCATION[3],
    }


# ==========================================
# 6. แสดงผลวิเคราะห์
# ==========================================

def analyze_stock(symbol):
    result = get_stock_data(symbol)

    if result is None:
        return

    supports = calculate_supports(result)
    budget = calculate_budget(symbol)

    price = result["price"]

    print("\n" + "-" * 45)
    print(f"หุ้น: {symbol}")
    print(f"วันที่ข้อมูลล่าสุด: {result['date']}")
    print(f"ราคาปิดล่าสุด: ${price:.2f}")

    print("\nแนวรับสำหรับเฝ้าดู:")
    for level in ("S1", "S2", "S3"):
        support = supports[level]
        distance = (price - support) / price * 100

        print(
            f"{level}: ${support:.2f} "
            f"| ต่ำกว่าราคาปัจจุบัน {distance:.2f}%"
        )

    print("\nงบลงทุนที่จัดสรร:")
    print(f"งบหุ้นนี้: {budget['total']:.2f} บาท")
    print(f"แนวรับ 1: {budget['support_1']:.2f} บาท")
    print(f"แนวรับ 2: {budget['support_2']:.2f} บาท")
    print(f"แนวรับ 3: {budget['support_3']:.2f} บาท")

    print("\nสถานะ: วิเคราะห์เท่านั้น ยังไม่ซื้อหุ้น")


# ==========================================
# 7. เริ่มระบบ
# ==========================================

def main():
    validate_config()

    print("=" * 50)
    print("AUTO DCA US STOCKS V1.0")
    print("หุ้นเป้าหมาย: ASML / NVDA")
    print(f"งบรายเดือน: {MONTHLY_BUDGET_THB:.2f} บาท")
    print("สัดส่วน: ASML 50% / NVDA 50%")
    print("โหมด: PAPER / READ-ONLY")
    print("เงินจริง: ปิดใช้งาน")
    print(
        "เวลา UTC:",
        datetime.now(timezone.utc).isoformat()
    )
    print("=" * 50)

    for symbol in WATCHLIST:
        analyze_stock(symbol)

    print("\n" + "=" * 50)
    print("จบการวิเคราะห์")
    print("ไม่มีการส่งคำสั่งซื้อขาย")
    print("=" * 50)


if __name__ == "__main__":
    main()
