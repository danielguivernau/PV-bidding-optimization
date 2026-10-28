# Probabilistic bidding for a standalone PV using a set of scenarios

param num_sets;
set SET_S = 1..num_sets;         
set SET_T = 0..23;

param p_pv{SET_S, SET_T};   # Solar generation scenario matrix (MW)
param price_da{SET_T};      # DAM price (€/MWh)
param price_surplus{SET_T}; # Imbalance surplus price lambda+ (€/MWh)
param price_deficit{SET_T}; # Imbalance deficit penalty lambda- (€/MWh)
param P_max_grid;           # Grid connection capacity limit (MW)

# DAM bid
var p_da{SET_T} >= 0, <= P_max_grid;

# Scenario imbalances
var imb_surplus{SET_S, SET_T} >= 0;
var imb_deficit{SET_S, SET_T} >= 0;

# Objective: Direct sum of net financial returns across all scenarios in SET_S
maximize Total_Scenario_Sum_Profit:
    sum {s in SET_S} (
        sum {t in SET_T} price_da[t] * p_da[t]
        + sum {t in SET_T} (
            price_surplus[t] * imb_surplus[s,t]
            - price_deficit[t] * imb_deficit[s,t]
        )
    );

# Imbalance definitions
subject to Grid_Balance {s in SET_S, t in SET_T}:
    p_pv[s,t] - p_da[t] = imb_surplus[s,t] - imb_deficit[s,t];