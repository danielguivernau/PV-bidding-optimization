import os
import numpy as np 
import pandas as pd 
from amplpy import AMPL
from scipy.ndimage import gaussian_filter1d

os.makedirs("models", exist_ok=True)

def generate_autocorrelated_scenarios(p_actual, n_scenarios=50, sigma=0.3, rho=0.8, seed=67):
    """
    Generates time-correlated forecast error scenarios across a 24-hour horizon
    """
    if seed is not None:
        np.random.seed(seed)
    H = len(p_actual)
    noise = np.zeros((n_scenarios, H))
    noise[:, 0] = np.random.normal(0, sigma, n_scenarios)
    
    for t in range(1, H):
        innovation = np.random.normal(0, sigma, n_scenarios)
        noise[:, t] = rho * noise[:, t-1] + np.sqrt(1 - rho**2) * innovation
        
    scenarios = np.clip(p_actual * (1.0 + noise), 0, 1.0)  # Clip to 1 MW peak capacity
    return scenarios

def da_bid_point(p_forecast, lambda_da, solver="highs"):
    """
    Get the optimal Day-ahead market bids given a point estimate of the generation capacity
    """
    H = len(p_forecast)

    ampl = AMPL()
    ampl.read("models/point_pv.mod")
    ampl.set_option("solver_msg", False)
    ampl.set_option("highs_options", "outlev=0")  # Silences HiGHS C++ logs

    # Set parameters
    ampl.param['price_da'] = {t: float(lambda_da[t]) for t in range(H)}
    ampl.param['p_forecast'] = {t: float(p_forecast[t]) for t in range(H)}
    ampl.param['P_max_grid'] = 1.0

    # Solve model
    ampl.solve(solver=solver)

    # Extract resulting bids
    p_da_df = ampl.get_variable("p_da").get_values().to_pandas()
    return p_da_df.sort_index().iloc[:, 0].values

def da_bid_probabilistic_standalone(scenarios, lambda_da, c1=-5, c2=15, solver="highs"):
    """
    Get the optimal Day-ahead market bids for the standalone PV system given a series of probabilistic scenarios of generation capacity
    """
    S, H = scenarios.shape
    lambda_pos = np.maximum(0, lambda_da + c1)
    lambda_neg = lambda_da + c2

    ampl = AMPL()
    ampl.read("models/probabilistic_pv.mod")
    ampl.set_option("solver_msg", False)
    ampl.set_option("highs_options", "outlev=0")  # Silences HiGHS C++ logs

    # Pass sets using ampl.set
    ampl.param['num_sets'] = S

    # Pass parameters using ampl.param
    ampl.param['price_da'] = {t: float(lambda_da[t]) for t in range(H)}
    ampl.param['price_surplus'] = {t: float(lambda_pos[t]) for t in range(H)}
    ampl.param['price_deficit'] = {t: float(lambda_neg[t]) for t in range(H)}
    ampl.param['p_pv'] = {(s + 1, t): float(scenarios[s, t]) for s in range(S) for t in range(H)}
    ampl.param['P_max_grid'] = 1.0

    ampl.set_option("solver", solver)
    ampl.solve()

    # Extract Day-Ahead bid vector p_da
    p_da_df = ampl.get_variable("p_da").get_values().to_pandas()
    return p_da_df.sort_index().iloc[:, 0].values

def backtrack_evaluation(p_da, p_actual, lambda_da, c1=-5, c2=15):
    """
    Evaluate a series of DA bids given the actual PV production and DA prices
    """
    lambda_pos = np.maximum(0, lambda_da + c1)
    lambda_neg = lambda_da + c2

    imb = p_actual - p_da 
    surplus = np.maximum(0, imb)
    deficit = np.maximum(0,-imb)

    da_revenue = np.sum(p_da * lambda_da)
    surplus_revenue = np.sum(surplus * lambda_pos)
    deficit_penalty = np.sum(deficit * lambda_neg)

    return da_revenue + surplus_revenue - deficit_penalty