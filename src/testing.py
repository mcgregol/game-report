from gr_template import GameReportTemplate
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd
import math

#  define function for creating data ranges
def add_range_from_rank(df, rank_col='Rank', out_col='Range'):
    n = len(df)
    h = math.floor(n / 3)
    m = math.floor(2 * n / 3)

    def label(r):
        if r <= h:
            return "high-range"
        elif r <= m:
            return "mid-range"
        return "low-range"

    df[out_col] = df[rank_col].apply(label)
    return df

#  Hide tkinter
Tk().withdraw()

#  Fetch data files
go_dtl_file = askopenfilename(title="Select game-only DTL Excel file", filetypes=[("Excel files","*.xlsx")])
freshness_file = askopenfilename(title="Select Freshness Excel file", filetypes=[("Excel files","*.xlsx")])
sm_team_file = askopenfilename(title="Select SupraMax team file", filetypes=[("Excel files","*.xlsx")])
sm_relative_file = askopenfilename(title="Select SupraMax relative file", filetypes=[("Excel files","*.xlsx")])

#  Create dataframes
df1 = pd.read_excel(go_dtl_file)
df2 = pd.read_excel(freshness_file)
df3 = pd.read_excel(sm_team_file, header=1)
df4 = pd.read_excel(sm_relative_file, header=1)

#  #  Swap placement of tdDTL and 3day && Trim off 7day and sort 3day
df2 = df2.drop(columns=['Freshness (7 day)', 'CTL'])
df2 = df2.sort_values(by=['Freshness (3 day)'])

df2.insert(3, 'DTL', df2.pop('DTL'))
df2 = df2.rename(columns={'DTL': 'Total Day DTL'})

#  rename DTL to td DTL & add respective rankings
df2 = df2.rename(columns={'DTL': 'Total Day DTL'})

df2["Total Day DTL"] = pd.to_numeric(df2["Total Day DTL"], errors="coerce")

df2["Total Day DTL Rank"] = (
    df2["Total Day DTL"]
        .rank(ascending=False, method="min")
        .astype("Int64")
)

#  add and populate rank cols & relative ranges
df1.insert(0, 'Rank', range(1, len(df1) + 1))

print(len(df2))
df2.insert(0, 'Rank', range(1, len(df2) + 1))

print(len(df3))
df3.insert(0, 'Rank', range(1, len(df3) + 1))
df3 = add_range_from_rank(df3, rank_col='Rank', out_col='Range')

print(len(df4))
df4.insert(0, 'Rank', range(1, len(df4) + 1))
df4 = add_range_from_rank(df4, rank_col='Rank', out_col='Range')

#  append % sign to sm files
df3['Total Supra Max Efforts'] = (df3['Total Supra Max Efforts'] * 100).round(3).astype(str) + '%'
df4['Avg Supra Max Efforts'] = (df4['Avg Supra Max Efforts'] * 100).round(3).astype(str) + '%'

t = GameReportTemplate('testing2', '', '', df1, df2, df3, df4)
t.go()