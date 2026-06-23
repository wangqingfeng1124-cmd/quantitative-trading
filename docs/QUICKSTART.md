# 快速开始指南

## 安装与配置

### 1. 克隆仓库

```bash
git clone https://github.com/wangqingfeng1124-cmd/quantitative-trading.git
cd quantitative-trading
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 Tushare Token

1. 访问 https://tushare.pro/ 注册账户
2. 获取免费 token
3. 编辑 `config.py`：

```python
TUSHARE_TOKEN = 'your_token_here'
```

## 5 分钟快速体验

### 方法一：运行完整示例

```bash
python example_backtest.py
```

这会：
- 下载 2022-2023 年平安银行(000001.SZ)数据
- 运行 RSI 策略回测
- 生成性能报告
- 输出图表和 Excel 报告

### 方法二：自定义回测

创建 `my_backtest.py`：

```python
from data.data_loader import DataLoader
from strategy.rsi_strategy import RSIStrategy
from backtest.engine import VectorizedBacktestEngine

# 1. 加载数据
loader = DataLoader()
df = loader.get_stock_data('000001.SZ', '20220101', '20231231')
print(f"加载了 {len(df)} 条数据")

# 2. 生成交易信号
strategy = RSIStrategy(params={
    'rsi_period': 14,
    'overbought': 70,
    'oversold': 30
})
df = strategy.generate_signals(df)

# 3. 执行回测
engine = VectorizedBacktestEngine(initial_cash=100000)
results = engine.run(df, position_size=0.1)

# 4. 查看结果
engine.print_summary()
```

运行：
```bash
python my_backtest.py
```

## 更换股票代码

Tushare 股票代码格式：`股票代码.交易所`

- `.SZ` - 深圳证券交易所
- `.SH` - 上海证券交易所

常见股票：
- 平安银行：`000001.SZ`
- 招商银行：`600036.SH`
- 贵州茅台：`600519.SH`
- 腾讯控股：`000700.SZ`（港股）
- 中国平安：`601318.SH`

```python
# 修改 ts_code
df = loader.get_stock_data('600519.SH', '20220101', '20231231')
```

## 尝试不同策略

### RSI 策略
```python
from strategy.rsi_strategy import RSIStrategy

strategy = RSIStrategy(params={
    'rsi_period': 14,
    'overbought': 70,
    'oversold': 30
})
```

### 双均线策略
```python
from strategy.examples import DualMovingAverageStrategy

strategy = DualMovingAverageStrategy(params={
    'fast_period': 12,
    'slow_period': 26
})
```

### MACD 策略
```python
from strategy.examples import MACDStrategy

strategy = MACDStrategy(params={
    'fast': 12,
    'slow': 26,
    'signal': 9
})
```

### 布林线策略
```python
from strategy.examples import BollingerBandsStrategy

strategy = BollingerBandsStrategy(params={
    'period': 20,
    'std_dev': 2.0
})
```

## 常见问题

### Q: 如何调整回测参数？
A: 编辑 `config.py` 文件：
```python
BACKTEST_CONFIG = {
    'start_date': '20220101',  # 改这里
    'end_date': '20231231',    # 改这里
    'initial_cash': 100000,    # 改这里
    'commission': 0.001,       # 改这里
    'slippage': 0.0005,        # 改这里
}
```

### Q: 如何优化策略参数？
A: 修改 `STRATEGY_CONFIG`：
```python
STRATEGY_CONFIG = {
    'rsi_period': 14,      # 试试 10-20
    'overbought': 70,      # 试试 60-80
    'oversold': 30,        # 试试 20-40
    'position_size': 0.1,  # 试试 0.05-0.2
}
```

### Q: Tushare API 限制怎么办？
A: 使用数据缓存（默认启用）：
```python
# 编辑 config.py
DATA_CONFIG = {
    'cache_dir': './data/cache',
    'use_cache': True,  # 启用缓存
}
```

### Q: 如何查看更详细的日志？
A: 检查 `backtest.log` 文件

## 下一步

- 📖 查看 [完整文档](../README.md)
- 🧪 运行单元测试：`python -m pytest tests/`
- 📚 学习如何 [自定义策略](CUSTOM_STRATEGY.md)
- 🔧 查看 [API 参考](API.md)

## 需要帮助？

- 查看 issue：https://github.com/wangqingfeng1124-cmd/quantitative-trading/issues
- 提交问题：欢迎开 issue 或 PR
