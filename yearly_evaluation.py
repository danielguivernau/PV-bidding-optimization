import os
import functions as f 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Ensure output directory exists
os.makedirs("plots", exist_ok=True)
os.makedirs("results", exist_ok=True)

df = pd.read_csv("datasets/processed_data.csv", index_col=False)
sigmas = [0.1, 0.3, 0.5, 0.8]
colmap = {0.1: "#1f77b4", 0.3: "#ff7f0e", 0.5: "#2ca02c", 0.8: "#d62728"}

def yearly_execution(sigma):
    results = []
    for d in range(365):
        day_df = df.iloc[(d * 24):((d + 1) * 24)]

        p_actual = day_df['pv_mw'].values
        prices = day_df["price_da"].values

        scenarios = f.generate_autocorrelated_scenarios(p_actual, sigma=sigma, n_scenarios=50, seed=None)
        point_scenario = scenarios[np.random.randint(0, scenarios.shape[0])]

        p_da_point = f.da_bid_point(point_scenario, prices)
        p_da_probabilistic = f.da_bid_probabilistic_standalone(scenarios, prices, c1=-5, c2=15)

        rev_point = f.backtrack_evaluation(p_da_point, p_actual, prices, c1=-5, c2=15)
        rev_probabilistic = f.backtrack_evaluation(p_da_probabilistic, p_actual, prices, c1=-5, c2=15)
        
        results.append({
            "day": d, 
            "rev_point": rev_point, 
            "rev_probabilistic": rev_probabilistic, 
            "difference": rev_probabilistic - rev_point
        })

    df_results = pd.DataFrame(results)
    return round(df_results, 2)

# Execute simulations
d_res = {}
summary_rows = []

for s in sigmas:
    print(f"Running simulation for sigma = {s}...")
    df_results = yearly_execution(s)
    d_res[s] = df_results
    
    # Calculate annual summary metrics
    tot_point = df_results["rev_point"].sum()
    tot_prob = df_results["rev_probabilistic"].sum()
    abs_gain = tot_prob - tot_point
    rel_uplift = (abs_gain / tot_point) * 100
    
    summary_rows.append({
        "sigma": s,
        "tot_point_eur": tot_point,
        "tot_prob_eur": tot_prob,
        "abs_gain_eur": abs_gain,
        "rel_uplift_pct": rel_uplift
    })

# Create Summary DataFrame
df_summary = pd.DataFrame(summary_rows)

# Print clean formatted summary to terminal
print("\n" + "="*70)
print("ANNUAL REVENUE SUMMARY TABLE")
print("="*70)
for idx, row in df_summary.iterrows():
    print(f"σ = {row['sigma']:<3} | Point: {row['tot_point_eur']:>10,.2f} € | Stochastic: {row['tot_prob_eur']:>10,.2f} € | Gain: +{row['abs_gain_eur']:>8,.2f} € (+{row['rel_uplift_pct']:.2f}%)")
print("="*70 + "\n")

# Save summary table to CSV
df_summary.round(2).to_csv(os.path.join("results", "annual_revenue_summary.csv"), index=False)

# --- CREATE 2-PANEL FIGURE ---
fig, axes = plt.subplots(2, 1, figsize=(7, 10))

# --- TOP PANEL: Cumulative Euro Gain with % Uplift in Legend ---
for s in sigmas:
    temp_res = d_res[s]
    cum_gain_eur = temp_res["difference"].cumsum()
    
    # Extract exact metrics from summary DataFrame
    s_row = df_summary[df_summary["sigma"] == s].iloc[0]
    total_gain_eur = s_row["abs_gain_eur"]
    total_gain_pct = s_row["rel_uplift_pct"]

    axes[0].plot(
        temp_res["day"], 
        cum_gain_eur, 
        label=f'σ = {s} (+{total_gain_eur:,.0f} € | +{total_gain_pct:.1f}%)', 
        color=colmap[s], 
        linewidth=2
    )

axes[0].axhline(0, color='black', linestyle=':', alpha=0.7)
axes[0].set_title('Cumulative Revenue Advantage of Stochastic Bidding over Time (Stochastic − Reference)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Day of Year', fontsize=10)
axes[0].set_ylabel('Cumulative Advantage (€)', fontsize=10)
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper left', fontsize=9, framealpha=0.9)

# --- BOTTOM PANEL: Daily Difference Boxplots ---
diff_data = [d_res[s]["difference"] for s in sigmas]

bp = axes[1].boxplot(
    diff_data, 
    tick_labels=[f'σ = {s}' for s in sigmas], 
    patch_artist=True,
    medianprops=dict(color="black", linewidth=1.5),
    flierprops=dict(marker='o', markersize=3, alpha=0.3)
)

for patch, s in zip(bp['boxes'], sigmas):
    patch.set_facecolor(colmap[s])
    patch.set_alpha(0.5)

axes[1].axhline(0, color='black', linestyle=':', alpha=0.7)
axes[1].set_title('Distribution of Daily Revenue Gain (Stochastic − Reference)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Forecast Uncertainty Level (σ)', fontsize=10)
axes[1].set_ylabel('Daily Revenue Gain (€)', fontsize=10)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()

# Save plot to plots/ directory
plot_path = os.path.join("plots", "sensitivity_analysis.png")
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"Plot saved successfully to: {plot_path}")

plt.show()