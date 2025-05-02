import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import settings

class ZScoreInvestmentStrategy:
    def __init__(self, window_size=settings.WINDOW_SIZE, weekly_investment=settings.WEEKLY_INVESTMENT):
        """
        Initialize the investment strategy.
        
        Parameters:
        - window_size: Size of the moving window for z-score calculation (in weeks)
        - weekly_investment: Fixed amount available to invest each week
        """
        self.window_size = window_size
        self.weekly_investment = weekly_investment
        self.cash_available = 0
        self.crypto_holdings = 0
        self.investment_history = []
    
    def calculate_z_score(self, prices):
        """Calculate moving z-score for each price point using the window size."""
        z_scores = []
        
        for i in range(len(prices)):
            if i < self.window_size:
                # Not enough data for z-score calculation
                z_scores.append(np.nan)
            else:
                # Get window of prices
                window = prices[i-self.window_size:i]
                mean = np.mean(window)
                std = np.std(window)
                if std == 0:
                    z_scores.append(0)  # Avoid division by zero
                else:
                    # Calculate z-score: (current_price - mean) / std
                    z_score = (prices[i] - mean) / std
                    z_scores.append(z_score)
        
        return z_scores
    
    def determine_investment_amount(self, z_score):
        """
        Determine investment amount based on z-score.
        
        The more negative the z-score, the higher percentage of available cash to invest.
        """
        if np.isnan(z_score) or z_score >= 0:
            # Don't invest if z-score is positive or undefined
            return 0
        
        # Get absolute value of z-score (but we only care about negative z-scores)
        abs_z = abs(z_score)
        
        # Find the percentile corresponding to this z-score
        # Higher absolute z-score = higher percentile = higher investment percentage
        for p, z_threshold in settings.Z_SCORE_THRESHOLDS:
            if abs_z >= z_threshold:
                # Invest p% of available cash
                return self.cash_available * p
        
        return 0  # Default if z-score doesn't meet any threshold
    
    def backtest(self, price_data):
        """
        Run backtest on historical price data.
        
        Parameters:
        - price_data: DataFrame with date and price columns
        
        Returns:
        - DataFrame with backtest results
        """
        prices = price_data['price'].values
        dates = price_data['date'].values
        
        # Calculate z-scores
        z_scores = self.calculate_z_score(prices)
        
        results = []
        
        for i in range(len(prices)):
            date = dates[i]
            price = prices[i]
            z_score = z_scores[i]
            
            # Add weekly investment amount to available cash
            self.cash_available += self.weekly_investment
            
            # Determine how much to invest this week
            if not np.isnan(z_score):
                investment_amount = self.determine_investment_amount(z_score)
                
                # Invest only if the amount is positive and we have cash
                if investment_amount > 0 and self.cash_available > 0:
                    # Cap investment at available cash
                    investment_amount = min(investment_amount, self.cash_available)
                    
                    # Buy crypto
                    crypto_bought = investment_amount / price
                    self.crypto_holdings += crypto_bought
                    self.cash_available -= investment_amount
                else:
                    investment_amount = 0
                    crypto_bought = 0
            else:
                investment_amount = 0
                crypto_bought = 0
            
            # Calculate portfolio value
            portfolio_value = self.cash_available + (self.crypto_holdings * price)
            
            # Record results
            self.investment_history.append({
                'date': date,
                'price': price,
                'z_score': z_score,
                'cash_available': self.cash_available,
                'investment_amount': investment_amount,
                'crypto_bought': crypto_bought,
                'crypto_holdings': self.crypto_holdings,
                'portfolio_value': portfolio_value
            })
        
        # Convert results to DataFrame
        return pd.DataFrame(self.investment_history)
    
    def plot_results(self, results, crypto_symbol):
        """Plot backtest results."""
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
        
        # Plot crypto price
        ax1.plot(results['date'], results['price'], label=f'{crypto_symbol} Price')
        ax1.set_title(f'{crypto_symbol} Price')
        ax1.legend()
        
        # Plot Z-score
        ax2.plot(results['date'], results['z_score'], label='Z-Score', color='orange')
        ax2.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        ax2.set_title(f'Z-Score ({self.window_size}-week window)')
        ax2.legend()
        
        # Plot Investment Amounts
        ax3.bar(results['date'], results['investment_amount'], label='Investment Amount', color='green', alpha=0.7)
        ax3.set_title('Weekly Investment Amounts')
        ax3.legend()
        
        # Plot Portfolio Value
        ax4.plot(results['date'], results['portfolio_value'], label='Portfolio Value', color='purple')
        ax4.plot(results['date'], results['crypto_holdings'] * results['price'], label=f'{crypto_symbol} Value', color='blue', alpha=0.5)
        ax4.plot(results['date'], results['cash_available'], label='Cash', color='green', alpha=0.5)
        ax4.set_title('Portfolio Value')
        ax4.legend()
        
        plt.tight_layout()
        plt.show()
        
    def compare_to_dca(self, price_data, results):
        """
        Compare strategy performance to simple DCA strategy.
        
        Parameters:
        - price_data: Original price data
        - results: Results from the backtest
        
        Returns:
        - Dictionary with comparison metrics
        """
        # Calculate strategy performance
        initial_investment = self.weekly_investment * len(results)
        final_portfolio = results['portfolio_value'].iloc[-1]
        strategy_roi = (final_portfolio / initial_investment - 1) * 100
        
        # Calculate simple DCA performance
        total_investment = initial_investment
        average_price = price_data['price'].mean()
        dca_crypto_amount = total_investment / average_price
        final_price = price_data['price'].iloc[-1]
        dca_final_value = dca_crypto_amount * final_price
        dca_roi = (dca_final_value / total_investment - 1) * 100
        
        return {
            'strategy_investment': initial_investment,
            'strategy_final_value': final_portfolio,
            'strategy_roi': strategy_roi,
            'dca_investment': total_investment,
            'dca_final_value': dca_final_value,
            'dca_roi': dca_roi,
            'outperformance': strategy_roi - dca_roi
        }