"""
analysis.py — E-Commerce Sales Analysis Dashboard
Run: python generate_data.py   (first time only)
     python analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

# ─── Style ───────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0f0f1a',
    'axes.facecolor':   '#1a1a2e',
    'axes.edgecolor':   '#333355',
    'axes.labelcolor':  '#ccccee',
    'xtick.color':      '#ccccee',
    'ytick.color':      '#ccccee',
    'text.color':       '#ffffff',
    'grid.color':       '#2a2a4a',
    'grid.linestyle':   '--',
    'grid.alpha':       0.5,
    'font.family':      'DejaVu Sans',
})
PALETTE  = ['#7c5cbf', '#e05c8a', '#f5a623', '#4ecdc4', '#45b7d1', '#96ceb4']
ACCENT   = '#e05c8a'
PRIMARY  = '#7c5cbf'

# ─── Load data ────────────────────────────────────────────────────────────────
csv_path = 'data/ecommerce_sales.csv'
if not os.path.exists(csv_path):
    print("❌ Run generate_data.py first!")
    exit(1)

df = pd.read_csv(csv_path, parse_dates=['order_date'])
print(f"✅ Loaded {len(df):,} rows | {df['order_date'].min().date()} → {df['order_date'].max().date()}")

# ─── KPIs ─────────────────────────────────────────────────────────────────────
total_revenue  = df['revenue'].sum()
total_orders   = len(df)
total_profit   = df['profit'].sum()
avg_order_val  = df['revenue'].mean()
return_rate    = df['returned'].mean() * 100
unique_customers = df['customer_id'].nunique()

print(f"\n{'─'*50}")
print(f"  Total Revenue   : ₹{total_revenue:>12,.0f}")
print(f"  Total Profit    : ₹{total_profit:>12,.0f}")
print(f"  Total Orders    : {total_orders:>13,}")
print(f"  Unique Customers: {unique_customers:>13,}")
print(f"  Avg Order Value : ₹{avg_order_val:>12,.2f}")
print(f"  Return Rate     : {return_rate:>12.1f}%")
print(f"{'─'*50}\n")

# ─── Derived tables ───────────────────────────────────────────────────────────
monthly = (df.groupby('month')
             .agg(revenue=('revenue','sum'), orders=('order_id','count'))
             .reset_index())
monthly['month_name'] = pd.to_datetime(monthly['month'], format='%m').dt.strftime('%b')
monthly['rolling_avg'] = monthly['revenue'].rolling(3, min_periods=1).mean()

cat_perf = (df.groupby('category')
              .agg(revenue=('revenue','sum'), profit=('profit','sum'), orders=('order_id','count'))
              .sort_values('revenue', ascending=False).reset_index())

region_rev = df.groupby('region')['revenue'].sum().reset_index()
pay_counts = df['payment_method'].value_counts()
rating_avg = df.groupby('category')['rating'].mean().sort_values()

# RFM
snapshot = df['order_date'].max() + pd.Timedelta(days=1)
rfm = df.groupby('customer_id').agg(
    recency=('order_date', lambda x: (snapshot - x.max()).days),
    frequency=('order_id', 'count'),
    monetary=('revenue', 'sum')
).reset_index()
for col in ['recency','frequency','monetary']:
    labels = [4,3,2,1] if col == 'recency' else [1,2,3,4]
    try:
        cut = pd.qcut(rfm[col], 4, labels=labels, duplicates='drop')
        # if fewer bins returned, trim labels
        n_bins = cut.cat.categories.size
        rfm[f'{col}_score'] = pd.qcut(rfm[col], 4,
            labels=labels[:n_bins], duplicates='drop').astype(int)
    except Exception:
        rfm[f'{col}_score'] = 2  # fallback neutral score
rfm['rfm_score'] = (rfm['recency_score'].astype(int)
                  + rfm['frequency_score'].astype(int)
                  + rfm['monetary_score'].astype(int))

def segment(s):
    if s >= 10: return 'Champions'
    elif s >= 8: return 'Loyal'
    elif s >= 6: return 'Potential'
    elif s >= 4: return 'At Risk'
    else:        return 'Lost'

rfm['segment'] = rfm['rfm_score'].apply(segment)
seg_counts = rfm['segment'].value_counts()

# ─── Figure ───────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 20), facecolor='#0f0f1a')
fig.suptitle('🛒  E-Commerce Sales Analysis Dashboard  |  2023',
             fontsize=22, fontweight='bold', color='white', y=0.98)

gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.50, wspace=0.38)

# ── 1. Monthly Revenue + Rolling Avg ─────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
bars = ax1.bar(monthly['month_name'], monthly['revenue']/1e6,
               color=PALETTE, alpha=0.85, width=0.6, zorder=2)
ax1.plot(monthly['month_name'], monthly['rolling_avg']/1e6,
         color=ACCENT, lw=2.5, marker='o', ms=5, label='3-Month Rolling Avg', zorder=3)
ax1.set_title('Monthly Revenue & Rolling Average', fontsize=13, pad=10)
ax1.set_ylabel('Revenue (₹ Millions)')
ax1.legend(facecolor='#1a1a2e', edgecolor='#444')
ax1.grid(axis='y', zorder=0)
for bar in bars:
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02,
             f'{bar.get_height():.1f}M', ha='center', fontsize=7.5, color='#ccccee')

# ── 2. KPI Tiles ─────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
ax2.axis('off')
kpis = [
    ('Total Revenue',   f'₹{total_revenue/1e6:.1f}M',  '#4ecdc4'),
    ('Total Profit',    f'₹{total_profit/1e6:.1f}M',   '#96ceb4'),
    ('Total Orders',    f'{total_orders:,}',             '#f5a623'),
    ('Avg Order Value', f'₹{avg_order_val:,.0f}',       '#45b7d1'),
    ('Return Rate',     f'{return_rate:.1f}%',           ACCENT),
    ('Customers',       f'{unique_customers:,}',         PRIMARY),
]
for i, (label, val, color) in enumerate(kpis):
    y = 0.95 - i * 0.16
    ax2.add_patch(plt.Rectangle((0, y-0.12), 1, 0.13,
                  transform=ax2.transAxes, color=color, alpha=0.15, clip_on=False))
    ax2.text(0.05, y-0.03, label, transform=ax2.transAxes,
             fontsize=9, color='#aaaacc')
    ax2.text(0.95, y-0.03, val, transform=ax2.transAxes,
             fontsize=12, fontweight='bold', color=color, ha='right')

# ── 3. Category Revenue ───────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
ax3.barh(cat_perf['category'], cat_perf['revenue']/1e6,
         color=PALETTE[:len(cat_perf)], alpha=0.85)
ax3.set_title('Revenue by Category', fontsize=12)
ax3.set_xlabel('Revenue (₹ Millions)')
ax3.grid(axis='x')

# ── 4. Profit Margin by Category ─────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
cat_perf['margin'] = (cat_perf['profit'] / cat_perf['revenue'] * 100).round(1)
colors = [PRIMARY if m >= cat_perf['margin'].mean() else ACCENT for m in cat_perf['margin']]
ax4.bar(cat_perf['category'], cat_perf['margin'], color=colors, alpha=0.85)
ax4.axhline(cat_perf['margin'].mean(), color='yellow', lw=1.5, linestyle='--', label='Avg')
ax4.set_title('Profit Margin % by Category', fontsize=12)
ax4.set_ylabel('Margin %')
ax4.legend(facecolor='#1a1a2e')
plt.setp(ax4.get_xticklabels(), rotation=20, ha='right', fontsize=8)
ax4.grid(axis='y')

# ── 5. Payment Method Pie ─────────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
wedges, texts, autotexts = ax5.pie(
    pay_counts, labels=pay_counts.index,
    autopct='%1.1f%%', colors=PALETTE,
    startangle=90, pctdistance=0.82,
    wedgeprops=dict(edgecolor='#0f0f1a', linewidth=2))
for at in autotexts: at.set_fontsize(8)
ax5.set_title('Payment Methods', fontsize=12)

# ── 6. Rating Distribution ───────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[2, 0])
rating_dist = df['rating'].value_counts().sort_index()
ax6.bar(rating_dist.index.astype(str), rating_dist.values,
        color=[ACCENT if r < 3 else PRIMARY for r in rating_dist.index], alpha=0.85)
ax6.set_title('Rating Distribution', fontsize=12)
ax6.set_xlabel('Star Rating')
ax6.set_ylabel('Number of Orders')
ax6.grid(axis='y')

# ── 7. Region Revenue ────────────────────────────────────────────────────────
ax7 = fig.add_subplot(gs[2, 1])
ax7.bar(region_rev['region'], region_rev['revenue']/1e6,
        color=PALETTE, alpha=0.85, width=0.5)
ax7.set_title('Revenue by Region', fontsize=12)
ax7.set_ylabel('Revenue (₹ Millions)')
ax7.grid(axis='y')

# ── 8. RFM Segments ──────────────────────────────────────────────────────────
ax8 = fig.add_subplot(gs[2, 2])
seg_order = ['Champions','Loyal','Potential','At Risk','Lost']
seg_vals  = [seg_counts.get(s, 0) for s in seg_order]
seg_colors = ['#4ecdc4','#96ceb4','#f5a623','#e05c8a','#7c5cbf']
ax8.barh(seg_order, seg_vals, color=seg_colors, alpha=0.85)
ax8.set_title('RFM Customer Segments', fontsize=12)
ax8.set_xlabel('No. of Customers')
ax8.grid(axis='x')

# ── 9. Heatmap: Category × Quarter Revenue ───────────────────────────────────
ax9 = fig.add_subplot(gs[3, :2])
pivot = df.pivot_table(values='revenue', index='category',
                        columns='quarter', aggfunc='sum') / 1e6
sns.heatmap(pivot, ax=ax9, cmap='RdPu', annot=True, fmt='.1f',
            linewidths=0.5, linecolor='#0f0f1a',
            cbar_kws={'label': 'Revenue (₹M)'})
ax9.set_title('Category × Quarter Revenue Heatmap (₹ Millions)', fontsize=12)
ax9.set_xlabel('Quarter')
ax9.set_ylabel('')

# ── 10. Discount vs Revenue Scatter ─────────────────────────────────────────
ax10 = fig.add_subplot(gs[3, 2])
sample = df.sample(500, random_state=1)
sc = ax10.scatter(sample['discount_pct'], sample['revenue'],
                  c=sample['rating'], cmap='plasma',
                  alpha=0.6, s=20, vmin=1, vmax=5)
plt.colorbar(sc, ax=ax10, label='Rating')
ax10.set_title('Discount % vs Revenue', fontsize=12)
ax10.set_xlabel('Discount %')
ax10.set_ylabel('Revenue (₹)')
ax10.grid(True)

os.makedirs('outputs', exist_ok=True)
plt.savefig('outputs/ecommerce_dashboard.png', dpi=150,
            bbox_inches='tight', facecolor='#0f0f1a')
print("✅ Dashboard saved → outputs/ecommerce_dashboard.png")
plt.show()
