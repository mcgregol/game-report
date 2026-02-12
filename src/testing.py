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
'''
go_dtl_file = askopenfilename(title="Select game-only DTL Excel file", filetypes=[("Excel files","*.xlsx")])
freshness_file = askopenfilename(title="Select Freshness Excel file", filetypes=[("Excel files","*.xlsx")])
sm_team_file = askopenfilename(title="Select SupraMax team file", filetypes=[("Excel files","*.xlsx")])
sm_relative_file = askopenfilename(title="Select SupraMax relative file", filetypes=[("Excel files","*.xlsx")])
'''
go_dtl_file = '../data/1-31-26/Game_Only_DTL-1-26-31v2.xlsx'
freshness_file = '../data/1-31-26/Indidivudal_Freshness_Summary-_Game_Report-1-31-26v2.xlsx'
sm_team_file = '../data/1-31-26/Intensity_Band_player_Game-1-31-26v2.xlsx'
sm_relative_file = '../data/1-31-26/Intensity_Band_player_Relative_-_Game1-31-26v2.xlsx'

#  Create dataframes
df1 = pd.read_excel(go_dtl_file)
df2 = pd.read_excel(freshness_file)
df3 = pd.read_excel(sm_team_file, header=1)
df4 = pd.read_excel(sm_relative_file, header=1)

#  append % sign to sm files
df3['Total Supra Max Efforts'] = (df3['Total Supra Max Efforts'] * 100).round(3).astype(str) + '%'
df4['Avg Supra Max Efforts'] = (df4['Avg Supra Max Efforts'] * 100).round(3).astype(str) + '%'
df4['Avg Very High Intensity Efforts'] = (df4['Avg Very High Intensity Efforts'] * 100).round(3).astype(str) + '%'

#  load samples narratives **for TESTING**
with open("../docs/sm_narrative", "r") as f:
    sample_sm_narrative = f.read()
with open("../docs/lm_narrative", "r") as f:
    sample_lm_narrative = f.read()

t = GameReportTemplate('testing2', sample_sm_narrative, sample_lm_narrative, df1, df2, df3, df4)
t.go()