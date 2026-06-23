# Quantitative Trading Framework

用 Python 从零搭建的股票量化交易回测框架。采用向量化回测引擎，支持快速策略测试和性能评估。

## 功能特性

### 📊 核心模块

- **数据加载** (`data/data_loader.py`)
  - 集成 Tushare API 获取国内股票数据
  - 支持数据缓存机制
  - 自动处理数据类型转换

- **技术指标** (`strategy/indicators.py`)
  - RSI (相对强弱指数)
  - SMA (简单移动平均)
  - EMA (指数移动平均)
  - MACD
  - 布林线

- **交易策略** (`strategy/`)
  - RSI 超买超卖策略
  - 可扩展的基础策略类
  - 灵活的信号生成机制

- **回测引擎** (`backtest/engine.py`)
  - 向量化回测 (高效)
  - 真实交易成本模拟 (手续费、滑点)
  - 完整的持仓管理

- **性能评估** (`backtest/metrics.py`)
  - 累计收益率
  - 年化收益率
  - 年化波动率
  - 夏普比率
  - 最大回撤
  - 卡玛比率
  - 胜率
  - 利润因子

- **可视化工具** (`utils/helpers.py`)
  - 资产曲线图
  - 收益率柱状图
  - 交易信号标记
  - RSI 指标展示
  - Excel 报告导出

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Tushare Token

获取免费 token：https://tushare.pro/

编辑 `config.py` 配置 token：

```python
TUSHARE_TOKEN = 'your_token_here'
```

或设置环境变量：

```bash
export TUSHARE_TOKEN='your_token_here'
```

### 3. 运行回测示例

```bash
python example_backtest.py
```

## 项目结构

```
quantitative-trading/
├── data/                           # 数据模块
│   ├── __init__.py
│   └── data_loader.py              # 数据加载器
│
├── strategy/                        # 策略模块
│   ├── __init__.py
│   ├── base_strategy.py            # 基础策略类
│   ├── indicators.py               # 技术指标计算
│   └── rsi_strategy.py             # RSI 策略实现
│
├── backtest/                        # 回测引擎
│   ├── __init__.py
│   ├── engine.py                   # 向量化回测引擎
│   ├── portfolio.py                # 投资组合管理
│   └── metrics.py                  # 性能指标计算
│
├── utils/                           # 工具函数
│   ├── __init__.py
│   └── helpers.py                  # 辅助函数 (可视化、导出)
│
├── tests/                           # 单元测试
│   ├── __init__.py
│   └── test_backtest.py            # 测试用例
│
├── config.py                        # 配置文件
├── example_backtest.py              # 完整示例
├── requirements.txt                 # 依赖列表
└── README.md                        # 项目说明
```

## 配置说明

编辑 `config.py` 自定义回测参数：

```python
# 回测参数
BACKTEST_CONFIG = {
    'start_date': '20220101',        # 开始日期
    'end_date': '20231231',          # 结束日期
    'initial_cash': 100000,          # 初始资金
    'commission': 0.001,             # 手续费 0.1%
    'slippage': 0.0005,              # 滑点 0.05%
}

# 策略参数
STRATEGY_CONFIG = {
    'rsi_period': 14,                # RSI 周期
    'overbought': 70,                # 超买阈值
    'oversold': 30,                  # 超卖阈值
    'position_size': 0.1,            # 单笔资金占比
}
```

## 使用示例

### 基础回测

```python
from data.data_loader import DataLoader
from strategy.rsi_strategy import RSIStrategy
from backtest.engine import VectorizedBacktestEngine

# 加载数据
loader = DataLoader()
df = loader.get_stock_data('000001.SZ', '20220101', '20231231')

# 生成信号
strategy = RSIStrategy(params={'rsi_period': 14, 'overbought': 70, 'oversold': 30})
df = strategy.generate_signals(df)

# 执行回测
engine = VectorizedBacktestEngine(initial_cash=100000)
results = engine.run(df, position_size=0.1)

# 打印结果
engine.print_summary()
```

### 自定义策略

```python
from strategy.base_strategy import BaseStrategy
import pandas as pd

class MyStrategy(BaseStrategy):
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['signal'] = 0
        # 自定义交易逻辑
        df.loc[df['close'] > df['close'].shift(1), 'signal'] = 1
        return df

# 使用自定义策略
strategy = MyStrategy('My Strategy')
df = strategy.generate_signals(df)
```

## 回测结果

运行完整示例后，会生成：

1. **backtest_results.png** - 资产曲线和收益率图
2. **trading_signals.png** - 交易信号和 RSI 指标图
3. **backtest_report.xlsx** - 详细的 Excel 报告
4. **backtest.log** - 完整的运行日志

## 性能指标解释

| 指标 | 说明 | 范围 |
|------|------|------|
| **累计收益率** | 整个回测期间的总收益 | - |
| **年化收益率** | 按年计算的平均收益率 | - |
| **年化波动率** | 收益的标准差，代表风险 | - |
| **夏普比率** | 单位风险的超额收益 | > 1 较好 |
| **最大回撤** | 从高点到低点的最大跌幅 | - |
| **卡玛比率** | 年化收益 / 最大回撤 | > 1 较好 |
| **胜率** | 盈利交易占比 | 0-100% |
| **利润因子** | 总盈利 / 总亏损 | > 1 较好 |

## 运行测试

```bash
python -m pytest tests/
```

或使用 unittest：

```bash
python -m unittest discover tests/
```

## 注意事项

1. **Tushare API 限制**
   - 免费版本有查询次数限制
   - 建议使用数据缓存功能
   - 大批量数据获取可能需要付费

2. **回测局限性**
   - 不考虑流动性风险
   - 不支持夜间交易和涨跌停
   - 不支持分红送股处理
   - 不支持融资融券

3. **实盘应用**
   - 回测好的策略在实盘中表现可能不同
   - 需要持续监控和调整
   - 建议小额试验后再加大资金

## 后续改进方向

- [ ] 支持多只股票组合回测
- [ ] 添加更多技术指标
- [ ] 实现事件驱动型回测引擎
- [ ] 支持 A 股停牌处理
- [ ] 集成实时交易执行
- [ ] 构建策略参数优化框架
- [ ] 添加风险管理模块（止损、止盈）
- [ ] 支持期货、基金等其他资产

## 参考资源

- [Tushare ���档](https://tushare.pro/)
- [Pandas 官方文档](https://pandas.pydata.org/)
- [NumPy 官方文档](https://numpy.org/)

## 许可证

MIT License

## 作者

quantitative-trading

## 贡献

欢迎提交 Issue 和 Pull Request！
