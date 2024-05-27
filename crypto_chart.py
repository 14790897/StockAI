from indicator_utils import (
    calculate_moving_average,
    calculate_bollinger_bands,
    calculate_macd,
    generate_signals,
    leverage_suggestion,
)

try:
    import ccxt
    import pandas as pd
    import matplotlib.pyplot as plt
    from datetime import datetime
    import time
except ImportError as e:
    print(f"Import Error: {e}")
    import subprocess
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "ccxt", "pandas", "matplotlib"]
    )


# 获取加密货币数据
def get_crypto_data(exchange, ticker, timeframe="1m", limit=500, since=None):
    try:
        if since:
            ohlcv = exchange.fetch_ohlcv(ticker, timeframe=timeframe, since=since)
        else:
            ohlcv = exchange.fetch_ohlcv(ticker, timeframe=timeframe, limit=limit)
        if ohlcv:
            data = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            data["timestamp"] = pd.to_datetime(data["timestamp"], unit="ms")
            data.set_index("timestamp", inplace=True)
            return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


# 绘制图表
def plot_crypto_data(data, ticker, ax1, ax2, lines, signal_info):
    # 清除旧的文本注释
    ax1.texts.clear()

    # 更新价格和布林带数据
    lines["close_price"].set_data(data.index.values, data["close"].values)
    lines["ma"].set_data(data.index.values, data["MA"].values)
    lines["upper_band"].set_data(data.index.values, data["Upper Band"].values)
    lines["lower_band"].set_data(data.index.values, data["Lower Band"].values)
    ax1.set_xlim(data.index.values.min(), data.index.values.max())
    ax1.set_ylim(data["close"].values.min(), data["close"].values.max())

    # 更新MACD数据
    lines["macd"].set_data(data.index.values, data["MACD"].values)
    lines["signal"].set_data(data.index.values, data["Signal"].values)
    for rect, h in zip(lines["macd_hist"], data["MACD_Hist"].values):
        rect.set_height(h)
    ax2.set_xlim(data.index.values.min(), data.index.values.max())
    ax2.set_ylim(data["MACD_Hist"].values.min(), data["MACD_Hist"].values.max())

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
    ax1.text(
        0.02,
        0.90,
        f"Current Price: {signal_info['current_price']}",
        transform=ax1.transAxes,
        fontsize=12,
        verticalalignment="top",
    )
    if signal_info["signal"] in ["buy", "sell"]:
        ax1.text(
            0.02,
            0.85,
            f"Leverage: {signal_info['leverage']}x",
            transform=ax1.transAxes,
            fontsize=12,
            verticalalignment="top",
        )


def initialize_plot(data, ticker):
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [2, 1], "hspace": 0.3}
    )

    lines = {}
    (lines["close_price"],) = ax1.plot(
        data.index.values, data["close"].values, label="Close Price", color="black"
    )
    (lines["ma"],) = ax1.plot(
        data.index.values, data["MA"].values, label=f"MA 20", color="blue"
    )
    (lines["upper_band"],) = ax1.plot(
        data.index.values,
        data["Upper Band"].values,
        label="Upper Bollinger Band",
        color="red",
    )
    (lines["lower_band"],) = ax1.plot(
        data.index.values,
        data["Lower Band"].values,
        label="Lower Bollinger Band",
        color="green",
    )
    ax1.fill_between(
        data.index.values,
        data["Upper Band"].values,
        data["Lower Band"].values,
        color="gray",
        alpha=0.3,
    )
    ax1.set_title(f"{ticker} Price Chart with MA and Bollinger Bands")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Price")
    ax1.legend(loc="best")

    (lines["macd"],) = ax2.plot(
        data.index.values, data["MACD"].values, label="MACD", color="blue"
    )
    (lines["signal"],) = ax2.plot(
        data.index.values, data["Signal"].values, label="Signal Line", color="red"
    )
    lines["macd_hist"] = ax2.bar(
        data.index.values,
        data["MACD_Hist"].values,
        label="MACD Histogram",
        color="gray",
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
    limit = 500  # 获取最近500条数据
    principal = 10  # 本金金额（USD）

    plt.ion()  # 开启交互模式

    # 初始绘图
    crypto_data = get_crypto_data(exchange, ticker, timeframe, limit)
    if crypto_data is not None:
        crypto_data["MA"] = calculate_moving_average(crypto_data, 20)
        upper_band, lower_band = calculate_bollinger_bands(crypto_data, 20)
        crypto_data["Upper Band"] = upper_band
        crypto_data["Lower Band"] = lower_band
        crypto_data["MACD"], crypto_data["Signal"], crypto_data["MACD_Hist"] = (
            calculate_macd(crypto_data)
        )

        fig, ax1, ax2, lines = initialize_plot(crypto_data, ticker)

        while True:
            try:
                # 获取加密货币数据，为了避免获取重复数据，加一毫秒
                last_timestamp = int(crypto_data.index[-1].timestamp() * 1000) + 1
                new_crypto_data = get_crypto_data(
                    exchange, ticker, timeframe="1m", since=last_timestamp
                )
                if new_crypto_data is not None and not new_crypto_data.empty:
                    # 合并新数据到现有数据
                    crypto_data = pd.concat([crypto_data, new_crypto_data])
                    crypto_data = crypto_data[
                        ~crypto_data.index.duplicated(keep="last")
                    ]  # 移除重复数据

                    # 计算指标，只计算新数据部分
                    new_indices = new_crypto_data.index
                    crypto_data.loc[new_indices, "MA"] = calculate_moving_average(
                        crypto_data, 20
                    ).loc[new_indices]
                    upper_band, lower_band = calculate_bollinger_bands(crypto_data, 20)
                    crypto_data.loc[new_indices, "Upper Band"] = upper_band.loc[
                        new_indices
                    ]
                    crypto_data.loc[new_indices, "Lower Band"] = lower_band.loc[
                        new_indices
                    ]
                    macd, signal, macd_hist = calculate_macd(crypto_data)
                    crypto_data.loc[new_indices, "MACD"] = macd.loc[new_indices]
                    crypto_data.loc[new_indices, "Signal"] = signal.loc[new_indices]
                    crypto_data.loc[new_indices, "MACD_Hist"] = macd_hist.loc[
                        new_indices
                    ]

                    # 生成交易信号
                    signal = generate_signals(crypto_data)
                    leverage = leverage_suggestion(principal, signal)
                    current_price = crypto_data["close"].iloc[-1]  # 获取当前价格

                    # 输出交易信号、止盈止损点和杠杆建议
                    signal_info = {
                        "signal": signal,
                        "leverage": leverage,
                        "current_price": current_price,  # 添加当前价格
                    }
                    print("signal_info", signal_info)
                    # 更新图表
                    plot_crypto_data(crypto_data, ticker, ax1, ax2, lines, signal_info)

                # 每分钟更新一次数据
                time.sleep(60)
            except KeyboardInterrupt:
                print("Program interrupted.")
                break
    else:
        print("Failed to fetch initial data.")
