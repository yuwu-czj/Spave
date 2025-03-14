import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

plt.style.use('ggplot')  # 或其他樣式如 'bmh', 'classic', 'dark_background' 等

def calculate_roi(investment, returns, days):
    """計算投資回報率"""
    annual_return = (returns - investment) / investment * (365 / days) * 100
    total_return = (returns - investment) / investment * 100
    return annual_return, total_return

def analyze_investment():
    print("=== 投資分析程式 ===")
    
    # 獲取基本資訊
    try:
        investment = float(input("請輸入投資金額（元）："))
        expected_return = float(input("請輸入預期收益金額（元）："))
        days = int(input("請輸入投資天數："))
        risk_level = int(input("請評估風險等級（1-低風險，2-中風險，3-高風險）："))
        
        # 計算回報率
        annual_roi, total_roi = calculate_roi(investment, expected_return, days)
        
        # 分析結果
        print("\n=== 分析結果 ===")
        print(f"投資金額：{investment:,.2f} 元")
        print(f"預期收益：{expected_return:,.2f} 元")
        print(f"投資天數：{days} 天")
        print(f"年化報酬率：{annual_roi:.2f}%")
        print(f"總報酬率：{total_roi:.2f}%")
        
        # 投資建議
        if annual_roi < 0:
            print("\n投資建議：不建議投資，預計會虧損！")
        elif annual_roi < 3 and risk_level == 1:
            print("\n投資建議：報酬率低於定存，建議考慮其他低風險投資方案。")
        elif annual_roi > 20 and risk_level == 3:
            print("\n投資建議：報酬率較高，但要注意高風險！建議分散投資。")
        else:
            print("\n投資建議：報酬率合理，請根據個人風險承受能力決定。")
        
        # 繪製簡單的收益曲線圖
        dates = pd.date_range(start=datetime.now(), periods=days)
        daily_return = (expected_return - investment) / days
        values = [investment + daily_return * i for i in range(days)]
        
        plt.figure(figsize=(10, 6))
        plt.plot(dates, values, 'b-')
        plt.title('預期投資收益曲線')
        plt.xlabel('日期')
        plt.ylabel('投資價值（元）')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    except ValueError:
        print("錯誤：請輸入有效的數字！")
    except Exception as e:
        print(f"發生錯誤：{str(e)}")
    finally:
        input("\n按 Enter 鍵結束程式...")

if __name__ == "__main__":
    analyze_investment()