
from datetime import datetime, timezone

import yfinance as yf

# ===== AUTO DCA V1.0: PAPER MODE =====

WATCHLIST = ["ASML", "NVDA", "GOOGL", "MSFT", "AMZN"]
MONTHLY_BUDGET_THB = 2000

# ปิดการซื้อขายเงินจริงไว้ก่อนเสมอ
LIVE_TRADING_ENABLED = False


def get_stock_price(symbol):
    """ดึงราคาปิดล่าสุดที่มีจากข้อมูลตลาด"""
    try:
        data = yf.Ticker(symbol).history(
            period="5d",
            interval="1d",
            auto_adjust=True
        )

        if data.empty:
            return None

        latest = data.dropna(subset=["Close"]).iloc[-1]

        return {
            "symbol": symbol,
            "price": round(float(latest["Close"]), 2),
            "date": str(latest.name.date()),
        }

    except Exception as error:
        print(f"ดึงข้อมูล {symbol} ไม่สำเร็จ: {error}")
        return None


def main():
    print("=" * 45)
    print("AUTO DCA US STOCKS - VERSION 1.0")
    print("Mode: PAPER ONLY")
    print("เวลา UTC:", datetime.now(timezone.utc).isoformat())
    print("งบรายเดือน:", MONTHLY_BUDGET_THB, "บาท")
    print("=" * 45)

    if LIVE_TRADING_ENABLED:
        raise RuntimeError(
            "ระบบรุ่นนี้ยังไม่อนุญาตให้ซื้อขายเงินจริง"
        )

    for symbol in WATCHLIST:
        result = get_stock_price(symbol)

        if result is None:
            print(symbol, "| ไม่มีข้อมูล")
            continue

        print(
            f"{result['symbol']} | "
            f"ราคาปิดล่าสุด: ${result['price']} | "
            f"วันที่ข้อมูล: {result['date']}"
        )

    print("=" * 45)
    print("จบการทดสอบ: ยังไม่มีการส่งคำสั่งซื้อ")


if __name__ == "__main__":
    main()
