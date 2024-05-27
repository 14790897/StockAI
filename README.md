# CryptoChart

CryptoChart 是一个用 Python 编写的小工具，从 Yahoo Finance 获取比特币的价格数据，并绘制包含移动平均线和布林带的价格图表。

## 功能

- 获取比特币的历史价格数据
- 绘制价格图表
- 计算并绘制移动平均线（MA）
- 计算并绘制布林带（Bollinger Bands）

## 安装

首先，确保你已经安装了 Python 3。然后安装所需的 Python 包：

```sh
pip install -r requirements.txt
```

## 使用方法

1. 克隆仓库或下载源代码：

```sh
git clone https://github.com/yourusername/CryptoChart.git
cd CryptoChart
```

2. 运行脚本：

```sh
python crypto_chart.py
```

3. 查看生成的价格图表。

## 自定义参数

你可以修改 `crypto_chart.py` 中的参数以获取不同时间段的数据或绘制不同的技术指标：

- **ticker**：加密货币的代码（默认：`BTC-USD`）。
- **start_date**：数据获取的开始日期（格式：`YYYY-MM-DD`）。
- **end_date**：数据获取的结束日期（格式：`YYYY-MM-DD`）。
- **ma_window**：移动平均线的窗口大小（默认：20天）。
- **bb_window**：布林带的窗口大小（默认：20天）。

## 贡献

欢迎贡献代码！请 fork 本仓库并提交 pull request。

## 许可

此项目基于 MIT 许可证开源。