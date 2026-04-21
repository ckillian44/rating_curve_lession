"""
Rating Curve Lesson — Step 4: Build and apply a stage-discharge rating curve

This script:
  1) Merges daily gage height and discharge to create stage-discharge pairs (same dates).
  2) Fits a monotonic power-law rating: Q = a * max(H - H0, 0)^b,
     with bounds and simple diagnostics.
  3) Saves the parameters and a rating table; exports a plot.
  4) Applies the rating to township elevations to estimate discharge,
     and creates a combined plot of USGS vs. estimated discharge.

Discussion: What is a rating curve?
    - A rating curve is an empirical relationship between stage (water surface elevation or 
      gage height) and discharge (streamflow) at a specific streamgage. Once established, 
      it allows you to convert continuous stage measurements into continuous estimates of discharge.
    - In practice:
        - You measure discharge directly at several stages (wading, ADCP, cableway, etc.).
        - You plot stage versus discharge.
        - You fit a curve (often monotonic unless dealing with complex hydraulics) that becomes 
          the stage-discharge relation used for records computation.
    - This is central to USGS surface-water records because streamflow is rarely measured continuously, but stage is.

Run:
  python make_rating_curve.py
"""


# ---- Load packages ----
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# ---- Load data ----

df = pd.read_csv('./output/USGS_Cleaned.csv')
rh = pd.read_csv('./output/RiverHeights_Cleaned.csv')
ge = pd.read_csv('./output/gage_elevation_ft.txt')

gage_elevation_ft = ge['altitude'][0]

discharge_data   = df[df['parameter_code'] == 60] # Filter 
gage_height_data = df[df['parameter_code'] == 65] # Filter 


# ---- Helper functions ----

def rating_func(H, a, H0, b):
    """Monotonic power-law rating: Q = a * max(H - H0, 0)^b"""
    return a * np.clip(H - H0, 0, None) ** b

def fit_rating(H, Q):
    """Fit power-law rating parameters with bounds and return params + diagnostics."""
    # initial guesses
    H0_guess = float(np.min(H)) - 0.1
    b_guess = 2.0
    a_guess = float(np.median(Q) / max((np.median(H) - H0_guess), 1e-6) ** b_guess)
    p0 = [a_guess, H0_guess, b_guess]
    lower = [1e-8, np.min(H) - 2.0, 0.5]
    upper = [1e8, np.min(H) + 1.0, 6.0]
    params_opt, cov = curve_fit(
        rating_func, H, Q, p0 = p0, bounds=(lower, upper), maxfev=20000
    )
    a_opt, H0_opt, b_opt = params_opt
    Q_hat = rating_func(H, a_opt, H0_opt, b_opt)
    ss_res = float(np.sum((Q - Q_hat) ** 2))
    ss_tot = float(np.sum((Q - np.mean(Q)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan

    # parameter uncertainties (1-sigma) if cov is well-formed
    try:
        se = np.sqrt(np.diag(cov))
        se_a, se_H0, se_b = [float(x) for x in se]
    except Exception:
        se_a = se_H0 = se_b = np.nan

    params = {
        "a": float(a_opt),
        "H0_ft": float(H0_opt),
        "b": float(b_opt),
        "r2": r2,
        "se_a": se_a,
        "se_H0_ft": se_H0,
        "se_b": se_b,
    }
    return params, Q_hat

def plot_rating(H, Q, params, outfile_png):
    """Scatter + fitted curve."""
    a, H0, b = params["a"], params["H0_ft"], params["b"]
    H_plot = np.linspace(max(H0, np.min(H) - 0.1), np.max(H) + 1.0, 300)
    Q_plot = rating_func(H_plot, a, H0, b)

    plt.figure(figsize=(7.5, 5.5))
    plt.scatter(H, Q, s = 30, color = "#1f77b4", alpha = 0.85, label = "Daily pairs")
    plt.plot(H_plot, Q_plot, color = "#d62728", lw = 2.5, label = "Fitted rating: Q = a(H-H0)^b")
    plt.xlabel("Gage height, H (ft)")
    plt.ylabel("Discharge, Q (cfs)")
    plt.title("USGS 05424157 Rating (daily stage–discharge pairs)")
    plt.grid(True, ls = ":", alpha = 0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outfile_png, dpi = 220)
    plt.close()

def save_rating_table(params, H_min, H_max, step_ft = 0.1, outfile_csv = "rating_table.csv"):
    """Export stage–discharge table over a range."""
    a, H0, b = params["a"], params["H0_ft"], params["b"]
    H_vals = np.arange(H_min, H_max + step_ft, step_ft)
    Q_vals = rating_func(H_vals, a, H0, b)
    table = pd.DataFrame({"H_ft": H_vals, "Q_cfs": Q_vals})
    table.to_csv(outfile_csv, index=False)
    return table


# ---- Make rating curve ----

print("Building rating pairs (daily stage-discharge match)...")
pairs = pd.merge(
    gage_height_data[["time", "value", "approval_status"]],
    discharge_data[[  "time", "value", "approval_status"]],
    on = "time",
    suffixes = ("_H", "_Q"),
    how = "inner"
)

# Clean and filter
pairs = pairs.dropna(subset=["value_H", "value_Q"])
pairs = pairs[(pairs["value_H"] > -100) & (pairs["value_Q"] > 0)]  # basic sanity checks

H = pairs["value_H"].to_numpy(dtype = float)
Q = pairs["value_Q"].to_numpy(dtype = float)

if len(pairs) < 15:
    print(f"WARNING: Only {len(pairs)} paired daily points; fit may be weak. Consider field measurements.")

# Fit rating
print("Fitting power-law rating Q = a*(H - H0)^b ...")
params, Q_hat = fit_rating(H, Q)
print(f"Fitted params: a = {params['a']:.6g}, H0 = {params['H0_ft']:.6g} ft, b = {params['b']:.6g}, R^2 = {params['r2']:.4f}")

# Save params
with open("./output/rating_params_05424157.json", "w") as f:
    json.dump(params, f, indent=2)

# Plot rating curve
plot_rating(H, Q, params, "./figs/rating_curve_05424157.png")

# Export rating table across observed stage range (with small margin)
H_min = max(params["H0_ft"], float(np.min(H)) - 0.1)
H_max = float(np.max(H)) + 0.5
save_rating_table(params, H_min, H_max, step_ft = 0.1, outfile_csv = "./output/rating_table_05424157.csv")


# ---- Apply rating to township data (back-estimate discharge) ----

print("Applying rating to township water elevations...")
# Convert township absolute elevations to gage height at the USGS site
rh["Township_GageHeight_ft"] = rh["Water Elevation"] - gage_elevation_ft

# Compute estimated discharge; clip negatives to 0
rh["Est_Q_cfs"] = rating_func(rh["Township_GageHeight_ft"], params["a"], params["H0_ft"], params["b"])

# Flag extrapolations outside (H_min, H_max) used for table
rh["Extrapolated"] = (rh["Township_GageHeight_ft"] < H_min) | (rh["Township_GageHeight_ft"] > H_max)


# ---- Plot discharge data ----

# Ensure datetime types
discharge_data["time"] = pd.to_datetime(discharge_data["time"], errors = "coerce")
rh['Date'] = pd.to_datetime(rh['Date'], errors = 'coerce') 

# Estimated daily discharge
plt.figure(figsize = (10, 6))
# Plot actual data
plt.plot(rh['Date'], rh['Est_Q_cfs'], marker = 'o', markersize = 3, linestyle = '-')
plt.title('Estimated Daily Discharge Over Time')
plt.xlabel('Date')
plt.ylabel('Estimated Discharge (cfs)')
plt.grid()
plt.legend()
plt.tight_layout()
plt.savefig('./figs/estimated_daily_discharge_over_time.png')


# Combined daily and estimated discharge
approval_color_map = {
    "Approved": "green",  
    "Provisional": "gray" 
}

fig, ax = plt.subplots(figsize=(14, 6))

usgs_handles = []
for status, color in approval_color_map.items():
    subset = discharge_data[discharge_data["approval_status"] == status]
    h = ax.plot(
        subset["time"],
        subset["value"],
        color = color,
        linestyle = '-',
        marker = 'o',
        markersize = 2,
        label = f"USGS {status}"
    )
    usgs_handles.extend(h)

ax.plot(rh['Date'], rh['Est_Q_cfs'], marker = 'o', markersize = 2, linestyle = '-', color = 'C0', label = 'Estimated Discharge')

ax.set_title("Daily Discharge (USGS) and Estimated Discharge (Monroe Road) — USGS-05424157")
ax.set_xlabel("Date")
ax.set_ylabel("Discharge (cfs)")
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend()

plt.tight_layout()
plt.savefig("./figs/combined_estimated_and_usgs_discharge.png", dpi = 200)


# ---- Save estmiated discharge ----

out_cols = ["Date", "Year", "Water_Elevation_ft", "Township_GageHeight_ft", "Est_Q_cfs", "Monroe_Road_Closed"]
print("Writing estimated discharge CSV -> Township_Estimated_Discharge_05424157.csv")
rh.loc[:, [c for c in out_cols if c in rh.columns]].to_csv("./output/Township_Estimated_Discharge_05424157.csv", index=False)

print("Done.")
