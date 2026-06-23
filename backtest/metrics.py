"""
性能指标计算模块 - 计算回测的各项收益指标
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class BacktestMetrics:
    """回测性能指标计算类"""

    @staticmethod
    def calculate_returns(equity: np.ndarray) -> np.ndarray:
        """
        计算每日收益率
        
        Args:
            equity: 每日总资产数组
            
        Returns:
            每日收益率数组
        """
        return np.diff(equity) / equity[:-1]

    @staticmethod
    def calculate_cumulative_return(equity: np.ndarray) -> float:
        """
        计算累计收益率
        
        Args:
            equity: 每日总资产数组
            
        Returns:
            累计收益率
        """
        return (equity[-1] - equity[0]) / equity[0]

    @staticmethod
    def calculate_annual_return(equity: np.ndarray, days_per_year: int = 252) -> float:
        """
        计算年化收益率
        
        Args:
            equity: 每日总资产数组
            days_per_year: 每年交易天数（默认252）
            
        Returns:
            年化收益率
        """
        total_return = BacktestMetrics.calculate_cumulative_return(equity)
        years = len(equity) / days_per_year
        
        if years <= 0:
            return 0
        
        annual_return = (1 + total_return) ** (1 / years) - 1
        return annual_return

    @staticmethod
    def calculate_volatility(equity: np.ndarray, days_per_year: int = 252) -> float:
        """
        计算年化波动率
        
        Args:
            equity: 每日总资产数组
            days_per_year: 每年交易天数
            
        Returns:
            年化波动率
        """
        returns = BacktestMetrics.calculate_returns(equity)
        daily_volatility = np.std(returns)
        annual_volatility = daily_volatility * np.sqrt(days_per_year)
        return annual_volatility

    @staticmethod
    def calculate_sharpe_ratio(equity: np.ndarray, risk_free_rate: float = 0.03, days_per_year: int = 252) -> float:
        """
        计算夏普比率
        
        Args:
            equity: 每日总资产数组
            risk_free_rate: 无风险利率（年化，默认3%）
            days_per_year: 每年交易天数
            
        Returns:
            夏普比率
        """
        annual_return = BacktestMetrics.calculate_annual_return(equity, days_per_year)
        annual_volatility = BacktestMetrics.calculate_volatility(equity, days_per_year)
        
        if annual_volatility == 0:
            return 0
        
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        return sharpe_ratio

    @staticmethod
    def calculate_max_drawdown(equity: np.ndarray) -> Tuple[float, int, int]:
        """
        计算最大回撤
        
        Args:
            equity: 每日总资产数组
            
        Returns:
            (最大回撤率, 开始索引, 结束索引)
        """
        cummax = np.maximum.accumulate(equity)
        drawdown = (equity - cummax) / cummax
        
        max_drawdown_idx = np.argmin(drawdown)
        max_drawdown_rate = drawdown[max_drawdown_idx]
        
        # 找到最大回撤开始的位置
        peak_idx = np.argmax(cummax[:max_drawdown_idx])
        
        return max_drawdown_rate, peak_idx, max_drawdown_idx

    @staticmethod
    def calculate_calmar_ratio(equity: np.ndarray, days_per_year: int = 252) -> float:
        """
        计算卡玛比率 (年化收益 / 最大回撤)
        
        Args:
            equity: 每日总资产数组
            days_per_year: 每年交易天数
            
        Returns:
            卡玛比率
        """
        annual_return = BacktestMetrics.calculate_annual_return(equity, days_per_year)
        max_drawdown, _, _ = BacktestMetrics.calculate_max_drawdown(equity)
        
        if max_drawdown == 0:
            return 0
        
        calmar_ratio = annual_return / abs(max_drawdown)
        return calmar_ratio

    @staticmethod
    def calculate_win_rate(trades: pd.DataFrame) -> float:
        """
        计算胜率
        
        Args:
            trades: 交易历史 DataFrame
            
        Returns:
            胜率
        """
        if 'pnl' not in trades.columns or len(trades) == 0:
            return 0
        
        winning_trades = (trades['pnl'] > 0).sum()
        total_trades = len(trades)
        
        return winning_trades / total_trades if total_trades > 0 else 0

    @staticmethod
    def calculate_profit_factor(trades: pd.DataFrame) -> float:
        """
        计算利润因子 (总盈利 / 总亏损)
        
        Args:
            trades: 交易历史 DataFrame
            
        Returns:
            利润因子
        """
        if 'pnl' not in trades.columns or len(trades) == 0:
            return 0
        
        gross_profit = trades[trades['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(trades[trades['pnl'] < 0]['pnl'].sum())
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0
        
        return gross_profit / gross_loss

    @staticmethod
    def generate_report(equity: np.ndarray, trades: pd.DataFrame = None) -> Dict:
        """
        生成完整的回测报告
        
        Args:
            equity: 每日总资产数组
            trades: 交易历史 DataFrame
            
        Returns:
            包含所有指标的字典
        """
        report = {
            'cumulative_return': BacktestMetrics.calculate_cumulative_return(equity),
            'annual_return': BacktestMetrics.calculate_annual_return(equity),
            'volatility': BacktestMetrics.calculate_volatility(equity),
            'sharpe_ratio': BacktestMetrics.calculate_sharpe_ratio(equity),
            'max_drawdown': BacktestMetrics.calculate_max_drawdown(equity)[0],
            'calmar_ratio': BacktestMetrics.calculate_calmar_ratio(equity),
        }
        
        if trades is not None and len(trades) > 0:
            report['win_rate'] = BacktestMetrics.calculate_win_rate(trades)
            report['profit_factor'] = BacktestMetrics.calculate_profit_factor(trades)
            report['total_trades'] = len(trades)
        
        return report
