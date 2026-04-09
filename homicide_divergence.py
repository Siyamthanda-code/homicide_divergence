import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. DATA LOADING
# ==========================================

# I'll include the loading logic from the successful script to ensure it works
file_name = 'Global_Homicide_Rate_1970_2025.csv'

try:
    df = pd.read_csv(file_name)
except FileNotFoundError:
    print(f"Error: File '{file_name}' not found.")
    exit()

# Detect delimiter
if df.shape[1] < 2:
    try:
        df = pd.read_csv(file_name, sep=';')
    except:
        try:
            df = pd.read_csv(file_name, sep='\t')
        except:
            print("Error: Could not parse file.")
            exit()

# Clean Commas
sample_val = df.iloc[0, 1]
if isinstance(sample_val, str) and ',' in sample_val:
    cols = df.columns.drop('Year')
    for col in cols:
        df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
else:
    cols = df.columns.drop('Year')
    df[cols] = df[cols].astype(float)

# Drop Global_Avg if present
if 'Global_Avg' in df.columns:
    df = df.drop(columns=['Global_Avg'])

# Set Index
df = df.set_index('Year')

# ==========================================
# 2. CALCULATE THE DIVERGENCE
# ==========================================
print("Calculating Global Safety Divergence...")

# Calculate the Maximum and Minimum homicide rate for every year
yearly_max = df.max(axis=1)
yearly_min = df.min(axis=1)

# Calculate the "Safety Gap"
yearly_gap = yearly_max - yearly_min

# Find the "Extreme" countries (The ones contributing to the gap)
country_max = df.idxmax(axis=1)
country_min = df.idxmin(axis=1)

# Create a summary DataFrame
divergence_df = pd.DataFrame({
    'Year': df.index,
    'Highest_Rate': yearly_max.values,
    'Most_Dangerous_Country': country_max.values,
    'Lowest_Rate': yearly_min.values,
    'Safest_Country': country_min.values,
    'Safety_Gap': yearly_gap.values
})

print(divergence_df.head())

# ==========================================
# 3. VISUALIZATION: THE DIVERGENCE
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# --- PLOT 1: The Safety Gap Over Time ---
ax1.fill_between(divergence_df['Year'], divergence_df['Safety_Gap'], color='orange', alpha=0.3, label='Safety Inequality')
ax1.plot(divergence_df['Year'], divergence_df['Safety_Gap'], color='red', linewidth=2)
ax1.set_title('The Great Divergence: Global Safety Gap (1970-2025)', fontsize=16, fontweight='bold')
ax1.set_ylabel('Gap (Difference in Rate)', fontsize=12)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.text(2026, divergence_df['Safety_Gap'].mean(), 
         "The 'Gap' represents the difference in safety\nbetween the safest and most dangerous country.", 
         fontsize=10, style='italic')

# --- PLOT 2: The Channels (Min vs Max) ---
ax2.plot(divergence_df['Year'], divergence_df['Highest_Rate'], color='black', label='Highest Rate (Dangerous)', linewidth=1.5)
ax2.plot(divergence_df['Year'], divergence_df['Lowest_Rate'], color='green', label='Lowest Rate (Safe)', linewidth=1.5)
ax2.fill_between(divergence_df['Year'], divergence_df['Lowest_Rate'], divergence_df['Highest_Rate'], color='grey', alpha=0.1)
ax2.set_title('Range of Violence: Worst vs. Best Case Scenarios', fontsize=16, fontweight='bold')
ax2.set_xlabel('Year', fontsize=12)
ax2.set_ylabel('Homicides per 100k', fontsize=12)
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

# Add Historical Annotations
events = {
    1994: "End of Apartheid",
    2001: "9/11 Attacks",
    2008: "Global Financial Crisis",
    2020: "COVID-19 Pandemic"
}

for year, label in events.items():
    if year in divergence_df['Year'].values:
        ax1.axvline(x=year, color='blue', linestyle=':', linewidth=1, alpha=0.5)
        ax2.axvline(x=year, color='blue', linestyle=':', linewidth=1, alpha=0.5)
        ax1.text(year, ax1.get_ylim()[1]*0.9, label, rotation=90, fontsize=8, ha='right', color='blue')

plt.tight_layout()
plt.savefig('homicide_divergence.png', dpi=300)
plt.show()

print("\n✅ Analysis Complete. Check 'homicide_divergence.png'.")