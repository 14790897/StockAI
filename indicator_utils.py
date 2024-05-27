# 计算移动平均线
def calculate_moving_average(data, window):
    if len(data) < window:
        raise ValueError("Data is not sufficient to calculate moving average.")
    return data["close"].rolling(window=window).mean()


def calculate_bollinger_bands(data, window):
    """
    计算布林带（Bollinger Bands）。

    布林带是一种技术分析工具，由中间的简单移动平均线（SMA）和围绕它的上下两个标准差线组成。
    布林带可以用来判断市场的波动性以及潜在的超买和超卖状态。

    Args:
        data (pd.DataFrame): 包含时间序列数据的 Pandas DataFrame，其中至少包括 'close' 列表示收盘价。
        window (int): 用于计算简单移动平均线和标准差的窗口大小（周期）。

    Returns:
        pd.Series, pd.Series: 返回两个 Pandas Series 对象，分别表示布林带的上轨（upper_band）和下轨（lower_band）。
    """
    sma = data["close"].rolling(window=window).mean()
    std = data["close"].rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band, lower_band


# 计算MACD 移动平均收敛/发散指标
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    # 计算短期EMA
    short_ema = data["close"].ewm(span=short_window, adjust=False).mean()
    # 计算长期EMA
    long_ema = data["close"].ewm(span=long_window, adjust=False).mean()
    # 计算MACD线
    macd = short_ema - long_ema
    # 计算信号线
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    # 计算MACD Histogram
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


# 计算止盈和止损点
# def calculate_profit_loss_points(data, signal):
#     if signal == "buy":
#         stop_loss = data["close"].iloc[-1] * 0.95  # 止损点设为当前价格的95%
#         take_profit = data["close"].iloc[-1] * 1.05  # 止盈点设为当前价格的105%
#     elif signal == "sell":
#         stop_loss = data["close"].iloc[-1] * 1.05  # 止损点设为当前价格的105%
#         take_profit = data["close"].iloc[-1] * 0.95  # 止盈点设为当前价格的95%
#     else:
#         stop_loss = None
#         take_profit = None
#     return take_profit, stop_loss
