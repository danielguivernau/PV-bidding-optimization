import os
import datetime as dt
import pandas as pd
from OMIEData.DataImport.omie_marginalprice_importer import OMIEMarginalPriceFileImporter
from OMIEData.Enums.all_enums import DataTypeInMarginalPriceFile

os.makedirs("datasets", exist_ok=True)

# 1. Download data for 2023
date_start = dt.datetime(2023, 1, 1)
date_end = dt.datetime(2023, 12, 31)
df_raw = OMIEMarginalPriceFileImporter(date_ini=date_start, date_end=date_end).read_to_dataframe(verbose=True)

# 2. Filter specifically for Spanish data (PRICE_SP)
str_price_spain = str(DataTypeInMarginalPriceFile.PRICE_SPAIN)
df_spain = df_raw[df_raw['CONCEPT'] == str_price_spain].copy()

# 3. Save raw wide dataframe to CSV
df_spain.to_csv("datasets/spain_day_ahead_prices_2023.csv", index=False)