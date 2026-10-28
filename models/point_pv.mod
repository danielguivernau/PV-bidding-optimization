# Deterministic Bidding using 1 Single Forecast Scenario

set SET_T = 0..23;         # Integer set prevents string sorting bugs

param p_forecast{SET_T};   # Single point solar forecast (MW)
param price_da{SET_T};     # DAM price (€/MWh)
param P_max_grid;          # Grid connection limit (MW)

var p_da{SET_T} >= 0, <= P_max_grid;
var imb_surplus{SET_T} >= 0;
var imb_deficit{SET_T} >= 0;

maximize Total_Expected_Profit:
    sum {t in SET_T} (
        price_da[t] * p_da[t]
    );

subject to Grid_Balance {t in SET_T}:
    p_forecast[t] - p_da[t] >= 0;