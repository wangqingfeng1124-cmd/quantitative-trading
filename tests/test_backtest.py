"""
回测框架单元测试
"""
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from strategy.indicators import TechnicalIndicators
from strategy.rsi_strategy import RSIStrategy
from backtest.portfolio import Portfolio
from backtest.metrics import BacktestMetrics


class TestTechnicalIndicators(unittest.TestCase):
    """技术指标测试"""

    def setUp(self):
        """测试前准备"""
        # 生成模拟价格数据
        np.random.seed(42)
        self.prices = np.cumsum(np.random.randn(100)) + 100

    def test_rsi_calculation(self):
        """测试 RSI 计算"""
        rsi = TechnicalIndicators.calculate_rsi(self.prices, period=14)
        
        # RSI 应该在 0-100 之间
        self.assertTrue(np.all(rsi[15:] >= 0))
        self.assertTrue(np.all(rsi[15:] <= 100))
        
        # 前 14 个值应该是 NaN
        self.assertTrue(np.isnan(rsi[:14]).all())

    def test_sma_calculation(self):
        """测试 SMA 计算"""
        sma = TechnicalIndicators.calculate_sma(self.prices, period=10)
        
        # SMA 数据点应该比原数据少 9 个
        self.assertEqual(len(sma), len(self.prices) - 9)
        
        # SMA 应该在最高价和最低价之间
        self.assertTrue(np.all(sma >= self.prices.min()))
        self.assertTrue(np.all(sma <= self.prices.max()))


class TestRSIStrategy(unittest.TestCase):
    """RSI 策略测试"""

    def setUp(self):
        """测试前准备"""
        # 生成模拟股票数据
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = np.cumsum(np.random.randn(100)) + 100
        
        self.df = pd.DataFrame({
            'trade_date': dates,
            'open': prices * 0.99,
            'high': prices * 1.01,
            'low': prices * 0.98,
            'close': prices,
            'vol': np.random.randint(1000000, 10000000, 100),
        })

    def test_rsi_strategy_signal_generation(self):
        """测试 RSI 策略信号生成"""
        strategy = RSIStrategy(params={
            'rsi_period': 14,
            'overbought': 70,
            'oversold': 30
        })
        
        result_df = strategy.generate_signals(self.df)
        
        # 应该有 signal 列
        self.assertIn('signal', result_df.columns)
        
        # 应该有 rsi 列
        self.assertIn('rsi', result_df.columns)
        
        # signal 列只能包含 -1, 0, 1
        unique_signals = result_df['signal'].unique()
        self.assertTrue(all(s in [-1, 0, 1] for s in unique_signals))


class TestPortfolio(unittest.TestCase):
    """投资组合测试"""

    def setUp(self):
        """测试前准备"""
        self.portfolio = Portfolio(initial_cash=100000, commission=0.001, slippage=0.0005)

    def test_portfolio_initialization(self):
        """测试投资组合初始化"""
        self.assertEqual(self.portfolio.cash, 100000)
        self.assertEqual(self.portfolio.position, 0)
        self.assertEqual(len(self.portfolio.equity_history), 1)

    def test_portfolio_buy(self):
        """测试买入操作"""
        success = self.portfolio.buy(price=100, date='2023-01-01', percent=0.1)
        
        self.assertTrue(success)
        self.assertGreater(self.portfolio.position, 0)
        self.assertLess(self.portfolio.cash, 100000)

    def test_portfolio_sell(self):
        """测试卖出操作"""
        # 先买入
        self.portfolio.buy(price=100, date='2023-01-01', percent=0.1)
        initial_position = self.portfolio.position
        
        # 后卖出
        success = self.portfolio.sell(price=105, date='2023-01-02', percent=1.0)
        
        self.assertTrue(success)
        self.assertEqual(self.portfolio.position, 0)
        self.assertGreater(self.portfolio.cash, 100000 - 10000)  # 应该有盈利


class TestBacktestMetrics(unittest.TestCase):
    """回测指标测试"""

    def setUp(self):
        """测试前准备"""
        # 生成模拟资产曲线
        self.equity = np.array([100000, 101000, 102100, 101500, 103000, 104000])

    def test_cumulative_return(self):
        """测试累计收益率计算"""
        ret = BacktestMetrics.calculate_cumulative_return(self.equity)
        expected = (104000 - 100000) / 100000
        self.assertAlmostEqual(ret, expected, places=4)

    def test_volatility(self):
        """测试波动率计算"""
        volatility = BacktestMetrics.calculate_volatility(self.equity)
        self.assertGreater(volatility, 0)

    def test_sharpe_ratio(self):
        """测试夏普比率计算"""
        sharpe = BacktestMetrics.calculate_sharpe_ratio(self.equity)
        self.assertIsNotNone(sharpe)

    def test_max_drawdown(self):
        """测试最大回撤计算"""
        max_dd, start_idx, end_idx = BacktestMetrics.calculate_max_drawdown(self.equity)
        
        self.assertLess(max_dd, 0)
        self.assertLess(start_idx, end_idx)


if __name__ == '__main__':
    unittest.main()
