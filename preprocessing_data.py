import os
import pandas as pd

os.makedirs("datasets", exist_ok=True)

# 1. PV Generation Data
pv_df = pd.read_csv('datasets/pv_generation_data.csv', skiprows=10, skipfooter=12, engine='python')
pv_df['pv_mw'] = pv_df['P'] / 1e6 
pv_df['dt'] = pd.to_datetime(pv_df['time'], format='%Y%m%d:%H%M').dt.floor('h')

# 2. Spanish Day-Ahead Prices (OMIE 2023)
price_df = pd.read_csv('datasets/spain_day_ahead_prices_2023.csv')
price_cols = [f'H{i}' for i in range(1, 25)]
price_long = price_df.melt(id_vars=['DATE'], value_vars=price_cols, var_name='hour_col', value_name='price_da')
price_long['hour'] = price_long['hour_col'].str.replace('H', '').astype(int) - 1
price_long['dt'] = pd.to_datetime(price_long['DATE']) + pd.to_timedelta(price_long['hour'], unit='h')

# 3. Merge data
df = pd.merge(pv_df[['dt', 'pv_mw']], price_long[['dt', 'price_da']], on='dt', how='outer')

full_year = pd.date_range(start='2023-01-01 00:00:00', end='2023-12-31 23:00:00', freq='h')
df = df.drop_duplicates(subset=['dt']).set_index('dt').reindex(full_year).rename_axis('dt').reset_index()

# Forward fill the single missing DST price hour and zero-fill solar gaps
df['price_da'] = df['price_da'].ffill().bfill()
df['pv_mw'] = df['pv_mw'].fillna(0.0)

# Save processed dataset
df.to_csv("datasets/processed_data.csv", index=False)
