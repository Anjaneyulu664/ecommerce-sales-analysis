# 🛒 E-Commerce Sales Analysis Dashboard

## Overview
A comprehensive data analysis project exploring e-commerce sales performance across categories, regions, and customer segments using Python.

## Features
- Monthly revenue trends with rolling averages
- Category-wise revenue and profit margin analysis
- RFM (Recency, Frequency, Monetary) customer segmentation
- Payment method distribution
- Region-wise performance
- Discount vs Revenue correlation
- Category × Quarter heatmap

## Tech Stack
- Python 3.8+
- pandas, numpy
- matplotlib, seaborn
- Jupyter Notebook (optional)

## Setup & Run

```bash
pip install pandas numpy matplotlib seaborn
python generate_data.py     # Generate synthetic dataset
python analysis.py          # Run full analysis → saves dashboard PNG
```

## Output
- `outputs/ecommerce_dashboard.png` — Full 10-panel dashboard
- Console KPI summary

## Dataset
Synthetically generated (5,000 orders, 2023 full year) covering:
- 6 product categories
- 4 regions
- 5 payment methods
- Customer ratings, returns, discounts

## Key Insights Explored
1. Which month has peak sales?
2. What category generates the most profit margin?
3. Who are our champion customers (RFM)?
4. Does higher discount reduce average revenue?
5. Which region underperforms?
