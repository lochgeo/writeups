import numpy as np
import pandas as pd

def calculate_annualized_volatility(prices, trading_days=252):
    """
    Calculates the annualized volatility of a currency pair from a series of daily prices.

    Args:
        prices (list, pd.Series, or np.ndarray): A sequence of daily exchange rates.
        trading_days (int, optional): The number of trading days in a year. 
                                     Defaults to 252.

    Returns:
        float: The annualized volatility as a decimal (e.g., 0.15 for 15%).
               Returns None if there is not enough data to calculate.
    """
    # Ensure prices are a pandas Series for easier manipulation
    prices = pd.Series(prices)
    
    # Check if there's enough data to calculate returns
    if len(prices) < 2:
        return None

    # Step 1: Calculate the daily logarithmic returns
    # The formula is: ln(Price_t / Price_t-1)
    # pandas .shift(1) gets the previous day's price
    log_returns = np.log(prices / prices.shift(1))

    # Step 2: Calculate the standard deviation of the log returns (daily volatility)
    # .std() will automatically ignore the first NaN value from the shift operation
    daily_volatility = log_returns.std()

    # Step 3: Annualize the volatility
    # We multiply by the square root of the number of trading days
    annualized_volatility = daily_volatility * np.sqrt(trading_days)
    
    return annualized_volatility

### How to Use It: A Complete Example

Here's how you would use the function with your data for the past year.

```python
# --- Example Usage ---

# 1. Your data: A list of daily exchange rates for the past year.
# Let's generate some sample data that looks like a year of EUR/USD prices.
# In your real application, you would load this from a file or database.
base_price = 1.08
# Generate 252 days of data (approx. 1 year of trading days)
# Simulating daily movements with a mean of 0 and a small standard deviation
daily_movements = np.random.normal(loc=0, scale=0.005, size=252)
# Create the price series by cumulatively adding the movements
sample_prices = base_price + np.cumsum(daily_movements)

# We can also create a simple list for demonstration
# sample_prices = [1.075, 1.078, 1.077, 1.081, 1.079, ...] # your data goes here

print(f"Number of price points: {len(sample_prices)}")
print(f"First 5 prices: {sample_prices[:5].round(4)}")
print("-" * 30)

# 2. Call the function to calculate volatility
volatility = calculate_annualized_volatility(sample_prices)

# 3. Print the result in a user-friendly format
if volatility is not None:
    # The ':.2%' format specifier multiplies by 100 and adds a '%' sign
    print(f"Calculated Annualized Volatility: {volatility:.2%}")
else:
    print("Could not calculate volatility due to insufficient data.")
