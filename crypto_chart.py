import ccxt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time


# 获取加密货币数据
def get_crypto_data(exchange, ticker, timeframe="1m", limit=500):
    ohlcv = exchange.fetch_ohlcv(ticker, timeframe=timeframe, limit=limit)
    data = pd.DataFrame(
        ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    data["timestamp"] = pd.to_datetime(data["timestamp"], unit="ms")
    data.set_index("timestamp", inplace=True)
    return data


# 计算移动平均线
def calculate_moving_average(data, window):
    return data["close"].rolling(window=window).mean()


# 计算布林带
def calculate_bollinger_bands(data, window):
    sma = data["close"].rolling(window=window).mean()
    std = data["close"].rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band, lower_band


# 计算MACD 移动平均收敛/发散指标
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data["close"].ewm(span=short_window, adjust=False).mean()
    long_ema = data["close"].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    macd_hist = macd - signal
    return macd, signal, macd_hist


# 生成交易信号
def generate_signals(data):
    ma_condition = (
        data["close"].iloc[-1] > data["MA"].iloc[-1]
        and data["close"].iloc[-2] <= data["MA"].iloc[-2]
    )
    macd_condition = (
        data["MACD"].iloc[-1] > data["Signal"].iloc[-1]
        and data["MACD"].iloc[-2] <= data["Signal"].iloc[-2]
    )

    if ma_condition and macd_condition:
        return "buy"
    elif not ma_condition and not macd_condition:
        return "sell"
    else:
        return "hold"


# 计算止盈和止损点
def calculate_profit_loss_points(data, signal):
    if signal == "buy":
        stop_loss = data["close"].iloc[-1] * 0.95  # 止损点设为当前价格的95%
        take_profit = data["close"].iloc[-1] * 1.05  # 止盈点设为当前价格的105%
    elif signal == "sell":
        stop_loss = data["close"].iloc[-1] * 1.05  # 止损点设为当前价格的105%
        take_profit = data["close"].iloc[-1] * 0.95  # 止盈点设为当前价格的95%
    else:
        stop_loss = None
        take_profit = None
    return take_profit, stop_loss


# 提供杠杆建议
def leverage_suggestion(principal, signal, risk_ratio=0.1):
    """
    :param principal: 本金金额
    :param signal: 当前交易信号 ("buy" or "sell")
    :param risk_ratio: 每笔交易风险比例 (例如：0.1 表示愿意承担本金的10%作为风险)
    :return: 建议的杠杆倍数
    """
    if signal in ["buy", "sell"]:
        # 假设每笔交易风险为本金的10%
        risk_amount = principal * risk_ratio
        # 计算止损点距离当前价格的百分比
        stop_loss_percentage = 0.05
        # 建议的杠杆倍数 = 风险金额 / (止损点距离 * 本金)
        leverage = risk_amount / (stop_loss_percentage * principal)
        return leverage
    else:
        return 1  # 如果信号是 hold，建议杠杆为1（即无杠杆）


# 绘制图表
def plot_crypto_data(data, ticker, ax1, ax2, lines, signal_info):
    # 更新价格和布林带数据
    lines["close_price"].set_ydata(data["close"])
    lines["ma"].set_ydata(data["MA"])
    lines["upper_band"].set_ydata(data["Upper Band"])
    lines["lower_band"].set_ydata(data["Lower Band"])
    ax1.set_ylim(min(data["close"]), max(data["close"]))

    # 更新MACD数据
    lines["macd"].set_ydata(data["MACD"])
    lines["signal"].set_ydata(data["Signal"])
    for rect, h in zip(lines["macd_hist"], data["MACD_Hist"]):
        rect.set_height(h)
    ax2.set_ylim(min(data["MACD_Hist"]), max(data["MACD_Hist"]))

    # 重绘图表
    plt.draw()
    plt.pause(1)

    # 显示交易信号、止盈止损点和杠杆建议
    ax1.text(
        0.02,
        0.95,
        f"Signal: {signal_info['signal']}",
        transform=ax1.transAxes,
        fontsize=12,
        verticalalignment="top",
    )
    if signal_info["signal"] in ["buy", "sell"]:
        ax1.text(
            0.02,
            0.90,
            f"Take Profit: {signal_info['take_profit']}",
            transform=ax1.transAxes,
            fontsize=12,
            verticalalignment="top",
        )
        ax1.text(
            0.02,
            0.85,
            f"Stop Loss: {signal_info['stop_loss']}",
            transform=ax1.transAxes,
            fontsize=12,
            verticalalignment="top",
        )
        ax1.text(
            0.02,
            0.80,
            f"Leverage: {signal_info['leverage']}x",
            transform=ax1.transAxes,
            fontsize=12,
            verticalalignment="top",
        )


def initialize_plot(data, ticker):
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [2, 1]}
    )

    lines = {}
    (lines["close_price"],) = ax1.plot(
        data["close"], label="Close Price", color="black"
    )
    (lines["ma"],) = ax1.plot(data["MA"], label=f"MA 20", color="blue")
    (lines["upper_band"],) = ax1.plot(
        data["Upper Band"], label="Upper Bollinger Band", color="red"
    )
    (lines["lower_band"],) = ax1.plot(
        data["Lower Band"], label="Lower Bollinger Band", color="green"
    )
    ax1.fill_between(
        data.index, data["Upper Band"], data["Lower Band"], color="gray", alpha=0.3
    )
    ax1.set_title(f"{ticker} Price Chart with MA and Bollinger Bands")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Price")
    ax1.legend(loc="best")

    (lines["macd"],) = ax2.plot(data["MACD"], label="MACD", color="blue")
    (lines["signal"],) = ax2.plot(data["Signal"], label="Signal Line", color="red")
    lines["macd_hist"] = ax2.bar(
        data.index, data["MACD_Hist"], label="MACD Histogram", color="gray"
    )
    ax2.set_title("MACD")
    ax2.set_xlabel("Time")
    ax2.legend(loc="best")

    plt.tight_layout()
    plt.show()
    return fig, ax1, ax2, lines


# 主函数
if __name__ == "__main__":
    exchange = ccxt.binance()  # 使用Binance交易所
    ticker = "BTC/USDT"  # 比特币对USDT的符号
    timeframe = "1m"  # 可以更改为'5m', '15m', '1h', '4h', '1d' 等
    limit = 1000  # 获取最近1000条数据
    principal = 10  # 本金金额（USD）

    plt.ion()  # 开启交互模式

    # 初始绘图
    crypto_data = get_crypto_data(exchange, ticker, timeframe, limit)
    if crypto_data is not None:
        crypto_data["MA"] = calculate_moving_average(crypto_data, 20)
        crypto_data["Upper Band"], crypto_data["Lower Band"] = (
            calculate_bollinger_bands(crypto_data, 20)
        )
        crypto_data["MACD"], crypto_data["Signal"], crypto_data["MACD_Hist"] = (
            calculate_macd(crypto_data)
        )

        fig, ax1, ax2, lines = initialize_plot(crypto_data, ticker)

        while True:
            # 获取加密货币数据
            new_crypto_data = get_crypto_data(exchange, ticker, timeframe, limit)
            if new_crypto_data is not None:
                # 更新数据
                new_crypto_data["MA"] = calculate_moving_average(new_crypto_data, 20)
                new_crypto_data["Upper Band"], new_crypto_data["Lower Band"] = (
                    calculate_bollinger_bands(new_crypto_data, 20)
                )
                (
                    new_crypto_data["MACD"],
                    new_crypto_data["Signal"],
                    new_crypto_data["MACD_Hist"],
                ) = calculate_macd(new_crypto_data)

                # 生成交易信号
                signal = generate_signals(new_crypto_data)
                take_profit, stop_loss = calculate_profit_loss_points(
                    new_crypto_data, signal
                )
                leverage = leverage_suggestion(principal, signal)

                # 输出交易信号、止盈止损点和杠杆建议
                signal_info = {
                    "signal": signal,
                    "take_profit": take_profit,
                    "stop_loss": stop_loss,
                    "leverage": leverage,
                }

                # 更新图表
                plot_crypto_data(new_crypto_data, ticker, ax1, ax2, lines, signal_info)

            # 每分钟更新一次数据
            time.sleep(60)
    else:
        print("Failed to fetch initial data.")
