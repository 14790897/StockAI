# 计算移动平均线
def calculate_moving_average(data, window):
    if len(data) < window:
        raise ValueError("Data is not sufficient to calculate moving average.")
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
