from flask import Flask, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

@app.route('/api/stock/<ticker_symbol>', methods=['GET'])
def get_stock_info(ticker_symbol):
    try:
        # 创建股票ticker对象
        stock = yf.Ticker(ticker_symbol)
        historical_data = stock.history(period="2d")

        if historical_data.empty:
            return {"error": f"无法获取 {ticker_symbol} 的股价数据"}, 404

        latest_data = historical_data.iloc[-1]
        latest_date = historical_data.index[-1].strftime('%Y-%m-%d')

        result = {
            "代码": ticker_symbol,
            "日期": latest_date,
            "价格": round(latest_data['Close'], 2),
            "开盘价": round(latest_data['Open'], 2),
            "最高价": round(latest_data['High'], 2),
            "最低价": round(latest_data['Low'], 2),
            "交易量": int(latest_data['Volume'])
        }

        if len(historical_data) >= 2:
            previous_close = historical_data['Close'].iloc[-2]
            price_change = latest_data['Close'] - previous_close
            price_change_percent = (price_change / previous_close) * 100

            result.update({
                "前收盘价": round(previous_close, 2),
                "额": round(price_change, 2),
                "幅": round(price_change_percent, 2)
            })
        else:
            result.update({
                "额": 0,
                "幅": 0
            })

        try:
            company_info = stock.info
            if 'shortName' in company_info:
                result["名称"] = company_info['shortName']
        except:
            result["名称"] = "未知"

        return jsonify(result)

    except Exception as e:
        return {"error": f"获取 {ticker_symbol} 信息时出错: {str(e)}"}, 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
