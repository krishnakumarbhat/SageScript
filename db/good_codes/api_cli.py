# good_practice_1.py

from typing import List

def calculate_total_price_with_tax(item_prices: List[float], tax_rate: float) -> float:
    """Calculates the total price of items including tax.

    Args:
        item_prices: A list of individual item prices.
        tax_rate: The tax rate as a decimal (e.g., 0.08 for 8%).

    Returns:
        The final total price.
    """
    subtotal = sum(item_prices)
    total_price = subtotal * (1 + tax_rate)
    return total_price

# Example usage:
prices = [10.50, 25.00, 7.99]
final_cost = calculate_total_price_with_tax(prices, 0.08)
print(f"Final cost is: ${final_cost:.2f}")