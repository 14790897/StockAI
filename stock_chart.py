import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


# 获取股票数据
def get_stock_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data


# 计算移动平均线
def calculate_moving_average(data, window):
    return data["Close"].rolling(window=window).mean()


# 计算布林带
def calculate_bollinger_bands(data, window):
    sma = data["Close"].rolling(window=window).mean()
    std = data["Close"].rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band, lower_band


# 绘制图表
def plot_stock_data(data, ticker, ma_window=20, bb_window=20):
    # 计算指标
    data["MA"] = calculate_moving_average(data, ma_window)
    data["Upper Band"], data["Lower Band"] = calculate_bollinger_bands(data, bb_window)

    # 绘制价格和指标
    plt.figure(figsize=(14, 7))
    plt.plot(data["Close"], label="Close Price", color="black")
    plt.plot(data["MA"], label=f"MA {ma_window}", color="blue")
    plt.plot(data["Upper Band"], label="Upper Bollinger Band", color="red")
    plt.plot(data["Lower Band"], label="Lower Bollinger Band", color="green")

    # 填充布林带
    plt.fill_between(
        data.index, data["Upper Band"], data["Lower Band"], color="gray", alpha=0.3
    )

    # 标题和图例
    plt.title(f"{ticker} Price Chart with MA and Bollinger Bands")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend(loc="best")
    plt.show()


# 主函数
if __name__ == "__main__":
    ticker = "AAPL"  # 股票代码
    start_date = "2022-01-01"  # 开始日期
    end_date = "2024-05-04"  # 结束日期

    # 获取股票数据
    stock_data = get_stock_data(ticker, start_date, end_date)

    # 绘制图表
    plot_stock_data(stock_data, ticker)
