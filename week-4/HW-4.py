# Author: Asmaa Abdul-Amin
# Date: 2021-07-25
# Version: 1.0
# Description: Homework 4 for the Python Programming course, which includes functions to process stock data and count occurrences of a substring in a string.

import pandas as pd

def process_stock_data(file_path):
    """Processes the stock CSV file and computes purchase price and profit margin."""
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    df['Purchase Price'] = df['Purchase Price'].str.replace('$', '').str.replace(',', '').astype(float)
    df['Current Price'] = df['Current Price'].str.replace('$', '').str.replace(',', '').astype(float)
    df['Shares'] = df['Shares'].astype(int)
    return df

def total_purchase_price(df):
    """Calculates the total purchase price of the portfolio."""
    return (df['Purchase Price'] * df['Shares']).sum()

def portfolio_profit_margin(df):
    """Calculates the total profit margin of the portfolio."""
    return ((df['Current Price'] - df['Purchase Price']) * df['Shares']).sum()


def foo(input_str, substring):
    """Counts occurrences of a substring in a string."""
    return input_str.count(substring)

def foo_enhanced(input_str, substring):
    """Counts occurrences and returns the indices where the substring appears."""
    occurrences = input_str.count(substring)
    indices = [i for i in range(len(input_str)) if input_str.startswith(substring, i)]
    return occurrences, indices

if __name__ == "__main__":
    # Process stock data
    file_path = 'week-4/Stocks.csv'
    stocks_df = process_stock_data(file_path)
    
    # Compute results
    total_purchase = total_purchase_price(stocks_df)
    profit_margin = portfolio_profit_margin(stocks_df)
    print(f"Total Purchase Price: ${total_purchase:.2f}")
    print(f"Portfolio Profit Margin: ${profit_margin:.2f}")

    """Test foo functions"""

def test_substring_occurrences():
    test_cases = [
        ("Emma is a good developer. Emma works hard. Emma likes coding.", "Emma"),
        ("Sophia is a skilled engineer. Sophia solves problems. Sophia enjoys designing.", "Sophia"),
        ("Emma is a talented and dedicated engineer with a passion for problem-solving and design. She excels \
            in finding efficient solutions to complex technical challenges and enjoys collaborating with her peers \
            to develop innovative ideas. Emma's analytical mindset and creativity allow her to approach engineering tasks \
            with both precision and ingenuity. She is always eager to learn new concepts and apply them effectively \
            in her work,making her a valuable asset in any technical environment.", "Emma"),
        ("Daniel is an excellent researcher. Daniel writes insightful papers. Daniel presents findings well.", "Daniel")
    ]
    
    for text, substring in test_cases:
        occurrences = text.count(substring)
        indices = [i for i in range(len(text)) if text.startswith(substring, i)]
        print(f"Occurrences of '{substring}': {occurrences}, Indices: {indices}")

if __name__ == "__main__":
    test_substring_occurrences()
