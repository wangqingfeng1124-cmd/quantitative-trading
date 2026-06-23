# 自定义策略开发指南

## 基础概念

所有策略都继承自 `BaseStrategy` 类，需要实现 `generate_signals` 方法。

## 创建一个简单策略

### 步骤 1：导入必要的模块

```python
import pandas as pd
import numpy as np
from strategy.base_strategy import BaseStrategy
```

### 步骤 2：创建策略类

```python
class MyFirstStrategy(BaseStrategy):
    """我的第一个交易策略"""
    
    def __init__(self, name: str = "My Strategy", params: dict = None):
        super().__init__(name, params)
        # 从参数中提取配置
        self.threshold = self.params.get('threshold', 0.05)
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        
        Args:
            df: DataFrame 必须包含 ['open', 'high', 'low', 'close', 'vol']
        
        Returns:
            df: 添加了 'signal' 列的 DataFrame
                signal=1: 买入
                signal=-1: 卖出  
                signal=0: 保持
        """
        # 验证数据
        self._validate_data(df)
        
        # 复制数据副本（不修改原数据）
        df = df.copy()
        
        # 初始化信号列
        df['signal'] = 0
        
        # 计算涨跌幅
        df['pct_change'] = df['close'].pct_change()
        
        # 生成买入信号：涨幅大于阈值
        buy_signal = df['pct_change'] > self.threshold
        df.loc[buy_signal, 'signal'] = 1
        
        # 生成卖出信号：跌幅大于阈值
        sell_signal = df['pct_change'] < -self.threshold
        df.loc[sell_signal, 'signal'] = -1
        
        # 保存信号
        self.signals = df
        
        return df
```

### 步骤 3：使用策略进行回测

```python
from data.data_loader import DataLoader
from backtest.engine import VectorizedBacktestEngine

# 加载数据
loader = DataLoader()
df = loader.get_stock_data('000001.SZ', '20220101', '20231231')

# 创建策略实例
strategy = MyFirstStrategy(params={'threshold': 0.05})

# 生成信号
df = strategy.generate_signals(df)

# 执行回测
engine = VectorizedBacktestEngine(initial_cash=100000)
results = engine.run(df, position_size=0.1)

# 查看结果
engine.print_summary()
```

## 高级用法

### 使用技术指标

```python
from strategy.indicators import TechnicalIndicators

class AdvancedStrategy(BaseStrategy):
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_data(df)
        df = df.copy()
        
        # 计算 RSI
        rsi = TechnicalIndicators.calculate_rsi(df['close'].values, period=14)
        df['rsi'] = rsi
        
        # 计算 SMA
        sma = TechnicalIndicators.calculate_sma(df['close'].values, period=20)
        df['sma'] = sma
        
        # 基于指标生成信号
        df['signal'] = 0
        df.loc[df['rsi'] < 30, 'signal'] = 1
        df.loc[df['rsi'] > 70, 'signal'] = -1
        
        self.signals = df
        return df
```

### 多条件组合

```python
class CombinedStrategy(BaseStrategy):
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_data(df)
        df = df.copy()
        
        # 计算多个指标
        df['ma_short'] = df['close'].rolling(window=10).mean()
        df['ma_long'] = df['close'].rolling(window=50).mean()
        df['rsi'] = TechnicalIndicators.calculate_rsi(df['close'].values)
        
        # 初始化信号
        df['signal'] = 0
        
        # 买入条件：短均线 > 长均线 AND RSI < 70
        buy = (df['ma_short'] > df['ma_long']) & (df['rsi'] < 70)
        df.loc[buy, 'signal'] = 1
        
        # 卖出条件：短均线 < 长均线 OR RSI > 80
        sell = (df['ma_short'] < df['ma_long']) | (df['rsi'] > 80)
        df.loc[sell, 'signal'] = -1
        
        self.signals = df
        return df
```

### 持仓限制

```python
class PositionLimitStrategy(BaseStrategy):
    """只允许一次持有一个持仓"""
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_data(df)
        df = df.copy()
        
        # 计算基础信号
        df['signal'] = 0
        df['rsi'] = TechnicalIndicators.calculate_rsi(df['close'].values)
        
        # 简单信号
        df.loc[df['rsi'] < 30, 'signal'] = 1
        df.loc[df['rsi'] > 70, 'signal'] = -1
        
        # 防止重复买入：只在转换时生成信号
        df['position'] = 0
        df.loc[df['signal'] == 1, 'position'] = 1
        df.loc[df['signal'] == -1, 'position'] = 0
        
        # 只在持仓状态改变时生成信号
        df['final_signal'] = 0
        df.loc[df['position'] != df['position'].shift(1), 'final_signal'] = df['signal']
        df['signal'] = df['final_signal']
        
        self.signals = df
        return df
```

## 最佳实践

### 1. 总是验证数据

```python
def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
    self._validate_data(df)  # 检查必要列和数据完整性
    df = df.copy()  # 使用副本，不修改原数据
    ...
```

### 2. 初始化信号为 0

```python
df['signal'] = 0  # 0 表示持有/不操作
```

### 3. 移除预热期

```python
df['signal'][:20] = 0  # 前 20 个交易日设为 0（指标未充分计算）
```

### 4. 记录日志

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"策略 {self.name} 生成 {(df['signal']==1).sum()} 个买入信号")
```

### 5. 测试策略

```python
import unittest

class TestMyStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = MyFirstStrategy()
    
    def test_generate_signals(self):
        # 创建模拟数据
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104],
            'open': [99, 100, 101, 102, 103],
            'high': [102, 103, 104, 105, 106],
            'low': [98, 99, 100, 101, 102],
            'vol': [1000000] * 5,
        })
        
        # 测试
        result = self.strategy.generate_signals(df)
        self.assertIn('signal', result.columns)
        self.assertTrue(all(s in [-1, 0, 1] for s in result['signal']))
```

## 常见错误

### ❌ 错误 1：忘记复制数据

```python
# 错误
def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
    df['signal'] = 0  # 修改了原数据！

# 正确
def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()  # 使用副本
    df['signal'] = 0
```

### ❌ 错误 2：生成大量信号

```python
# 错误
df.loc[df['rsi'] < 30, 'signal'] = 1  # 每个 RSI < 30 的行都生成信号

# 更好
df.loc[df['rsi'] < 30, 'signal'] = 1
df['signal'] = df['signal'].astype(int).diff()  # 只在穿���时生成信号
```

### ❌ 错误 3：未处理 NaN 值

```python
# 错误
rsi = TechnicalIndicators.calculate_rsi(prices)  # 前几个值是 NaN
df.loc[rsi < 30, 'signal'] = 1  # NaN 比较会出错

# 正确
df['rsi'] = rsi
df.loc[df['rsi'] < 30, 'signal'] = 1  # pandas 自动处理 NaN
```

## 性能优化

### 向量化操作（快）

```python
# 好
df['ma'] = df['close'].rolling(window=20).mean()  # 向量化
```

### 循环操作（慢）

```python
# 不好
ma = []
for i in range(len(df)):
    ma.append(df['close'].iloc[max(0, i-20):i].mean())  # 循环
```

## 更多资源

- 查看 `strategy/examples.py` 获取更多策略示例
- 查看 `strategy/indicators.py` 了解可用的技术指标
- 查看 `tests/` 了解测试示例
