import geopandas as gpd
import pandas as pd
from pathlib import Path
import os
import itertools
import numpy as np

import matplotlib.pyplot as plt

df = pd.read_csv('GIS_work\data\\timeseries\Immigrant Income Data - Entry.csv', index_col=False)

additional = pd.read_csv('GIS_work\data\\timeseries\Immigrant Income Data - MBM.csv', index_col=False)

for c in additional.columns[1:]:
    additional[c] = additional[c].str.replace(',', '', regex=False)
    additional[c] = additional[c].astype(int)
    additional = additional.rename(columns={c : int(c.replace(',', ''))})

for c in df.columns[1:]:
    df[c] = df[c].str.replace(',', '', regex=False)
    df[c] = df[c].astype(int)

pa_mask = df['Unnamed: 0'].str.contains('principal applicant', case=False)
pa_avg = df[pa_mask].mean(numeric_only=True)
pf = pa_avg.to_frame().T
pf['Unnamed: 0'] = 'Principal Applicants (Economic Immigrant)'

df = pd.concat([df[~pa_mask], pf], ignore_index=True)
df = df[df['Unnamed: 0'] != 'All immigrants']
df = df.reset_index(drop=True)

years = [int(c) for c in df.columns[1:]]
labels = df['Unnamed: 0'].tolist()

additional_years = [int(c) for c in additional.columns[1:]]  # [2020, 2021]
additional_labels = additional['Unnamed: 0'].tolist()

fig, ax = plt.subplots(figsize=(16, 6))

for i, row in df.iterrows():
    values = [row[c] for c in df.columns[1:]]
    ax.plot(years, np.array(values) / 1000, marker='o', label=labels[i])
    
for i, row in additional.iterrows():
    y_val = (row[2021] / 1000) / 2 #divided by 2 for a single person
    color = f'C{len(ax.lines)}'
    ax.axhline(y=y_val, linestyle='--', color=color, alpha=0.7, linewidth=2,
               label=f"MBM {additional_labels[i]} (2021)")

#Canadian median at that time: 45380
ax.axhline(y=45380 / 1000, linestyle='--', color='grey', linewidth=4, label='Canadian Median Income')

ax.set_xlabel('Year')
ax.set_ylabel('Income (CAD $000s)')
ax.set_title('Immigrant Entry Income (2012 - 2021) vs Market Basket Measure (MBM) for an Individual')
ax.set_xticks(years)
ax.yaxis.set_major_locator(plt.MaxNLocator(5))

ax.legend(
    loc='center left',
    bbox_to_anchor=(1.02, 0.5),
    borderaxespad=0,
    fontsize=9
)

plt.tight_layout()
plt.savefig('GIS_work\\graphs\\immigrant_income.png', dpi=150, bbox_inches='tight')
# plt.show()



#############################################

#calculate 

from simulate_timeseries import project

df = pd.read_csv('GIS_work\data\\timeseries\Immigrant Income Data - Years After.csv', index_col=False)
projected_mbm = project(pd.read_csv('GIS_work\data\\timeseries\Immigrant Income Data - MBM_longer.csv', index_col=False))
projected_mbm.drop(columns=[2020], inplace=True)

for c in df.columns[1:]:
    df[c] = df[c].str.replace(',', '', regex=False)
    df[c] = df[c].astype(int)

pa_mask = df['Unnamed: 0'].str.contains('principal applicant', case=False)
pa_avg = df[pa_mask].mean(numeric_only=True)
pf = pa_avg.to_frame().T
pf['Unnamed: 0'] = 'Principal Applicants (Economic Immigrant)'

df = pd.concat([df[~pa_mask], pf], ignore_index=True)
df = df[df['Unnamed: 0'] != 'All immigrants']
df = df.reset_index(drop=True)

years = [int(c) for c in df.columns[1:]]
labels = df['Unnamed: 0'].tolist()

fig, ax = plt.subplots(figsize=(16, 6))

for i, row in df.iterrows():
    values = [row[c] for c in df.columns[1:]]
    ax.plot(years, np.array(values) / 1000, marker='o', label=labels[i])
    

# additional = pd.read_csv('GIS_work\data\\timeseries\Immigrant Income Data - MBM.csv', index_col=False)

# for c in additional.columns[1:]:
#     additional[c] = additional[c].str.replace(',', '', regex=False)
#     additional[c] = additional[c].astype(int)
#     additional = additional.rename(columns={c : int(c.replace(',', ''))})

for c in df.columns[1:]:
    # df[c] = df[c].str.replace(',', '', regex=False)
    df[c] = df[c].astype(int)
    df = df.rename(columns={c : int(c)})

pa_mask = df['Unnamed: 0'].str.contains('principal applicant', case=False)
pa_avg = df[pa_mask].mean(numeric_only=True)
pf = pa_avg.to_frame().T
pf['Unnamed: 0'] = 'Principal Applicants (Economic Immigrant)'

df = pd.concat([df[~pa_mask], pf], ignore_index=True)
df = df[df['Unnamed: 0'] != 'All immigrants']
df = df.reset_index(drop=True)

years = [int(c) for c in df.columns[1:]]
labels = df['Unnamed: 0'].tolist()

# additional_years = [int(c) for c in additional.columns[1:]]  # [2020, 2021]
# additional_labels = additional['Unnamed: 0'].tolist()

projected_labels = projected_mbm['Unnamed: 0'].tolist()

fig, ax = plt.subplots(figsize=(16, 6))

for i, row in df.iterrows():
    values = [row[c] for c in df.columns[1:]]
    ax.plot(years, np.array(values) / 1000, marker='o', label=labels[i])
    
for i, row in projected_mbm.iterrows():
    values = [row[c] for c in projected_mbm.columns[1:]]
    ax.plot(years, (np.array(values) / 1000) / 2, linestyle='--', label=f'MBM {projected_labels[i]}')
    
ax.axvline(x=5, linestyle='--', color='grey', label='Projection Point (2025)')
    
# for i, row in additional.iterrows():
#     y_val = (row[2021] / 1000) / 2 #divided by 2 for a single person
#     color = f'C{len(ax.lines)}'
#     ax.axhline(y=y_val, linestyle='--', color=color, alpha=0.7, linewidth=2,
#                label=f"MBM {additional_labels[i]} (2021)")

ax.set_xlabel('Year')
ax.set_ylabel('Income (CAD $000s)')
ax.set_title('Immigrant Income over Years Since Admission vs Projected Market Basket Measure (MBM) for an Individual')
ax.set_xticks(years)
ax.yaxis.set_major_locator(plt.MaxNLocator(5))

ax.legend(
    loc='center left',
    bbox_to_anchor=(1.02, 0.5),
    borderaxespad=0,
    fontsize=9
)

plt.tight_layout()
plt.savefig('GIS_work\\graphs\\immigrant_income_after_admission.png', dpi=150, bbox_inches='tight')
