"""
generate_data.py — Generates synthetic e-commerce dataset
Run this first before analysis.py
"""
import pandas as pd
import numpy as np
import os

np.random.seed(42)

n = 5000
categories = ['Electronics', 'Clothing', 'Books', 'Home & Kitchen', 'Sports', 'Beauty']
regions = ['North', 'South', 'East', 'West']
payment_methods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'COD']

dates = pd.date_range(start='2023-01-01', end='2023-12-31', periods=n)

df = pd.DataFrame({
    'order_id': [f'ORD{str(i).zfill(5)}' for i in range(1, n+1)],
    'customer_id': np.random.randint(1000, 4000, n),
    'order_date': np.sort(dates),
    'category': np.random.choice(categories, n, p=[0.25, 0.20, 0.10, 0.20, 0.15, 0.10]),
    'product_price': np.round(np.random.exponential(scale=1500, size=n).clip(100, 15000), 2),
    'quantity': np.random.randint(1, 6, n),
    'discount_pct': np.random.choice([0, 5, 10, 15, 20, 25, 30], n, p=[0.3,0.1,0.2,0.15,0.1,0.1,0.05]),
    'region': np.random.choice(regions, n),
    'payment_method': np.random.choice(payment_methods, n),
    'returned': np.random.choice([0, 1], n, p=[0.88, 0.12]),
    'rating': np.random.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.08, 0.17, 0.40, 0.30]),
})

df['revenue'] = np.round(df['product_price'] * df['quantity'] * (1 - df['discount_pct']/100), 2)
df['profit'] = np.round(df['revenue'] * np.random.uniform(0.15, 0.40, n), 2)
df['month'] = df['order_date'].dt.month
df['month_name'] = df['order_date'].dt.strftime('%b')
df['quarter'] = df['order_date'].dt.quarter

os.makedirs('data', exist_ok=True)
df.to_csv('data/ecommerce_sales.csv', index=False)
print(f"✅ Dataset saved: {len(df)} rows → data/ecommerce_sales.csv")
print(df.head(3))
