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
ib_period_file = '../data/period_ib.xlsx'

#  Create dataframes
df1 = pd.read_excel(go_dtl_file)
df2 = pd.read_excel(freshness_file)
df3 = pd.read_excel(sm_team_file, header=1)
df4 = pd.read_excel(sm_relative_file, header=1)
df5 = pd.read_excel(ib_period_file)

#  append % sign to sm & period IB files
df3['Total Supra Max Efforts'] = (df3['Total Supra Max Efforts'] * 100).round(3).astype(str) + '%'
df4['Avg Supra Max Efforts'] = (df4['Avg Supra Max Efforts'] * 100).round(3).astype(str) + '%'
df4['Avg Very High Intensity Efforts'] = (df4['Avg Very High Intensity Efforts'] * 100).round(3).astype(str) + '%'

#  load samples narratives **for TESTING**
with open("../docs/sm_narrative", "r") as f:
    sample_sm_narrative = f.read()
with open("../docs/lm_narrative", "r") as f:
    sample_lm_narrative = f.read()

intensity_note = '''In contrast to 12/31 game, which was generally high in intense efforts on a team level, there
was much higher variation on 1/3. There were 7 players who displayed SupraMax efforts greater than 105%
of their personal average. In particular, UPL exhibited an enormous 285% greater than his personal average.
But at the same time, there were 9 players who displayed efforts less than 95% of their personal average.
So, as a team, a very uneven effort. Relative to the other games in the month of December, this was the
lowest effort in terms of SupraMax efforts and Very High Intensity efforts since December 8th. As noted at
the end of this report, several players had high efforts in the first period, but it was very uneven and as a
team, it was low.'''
load_note = '''As a team, players were relatively fresh for this game. Given the day off
and practice the day before, with no morning skate, Freshness metrics were bordering on “too
fresh”, but were not to that point. The team should have been in a good spot going into this game.
This seems supported by the nature of the 9 players who were above 105% of their average and
had good intensity. After the game, there are only two players “flagged” with low 3 Day Freshness
and that flag is “yellow”, which should not be of concern. So, again, the team still seems
relatively fresh on the whole. That being said, the upcoming game schedule will be of concern
and having higher freshness to start that game sequence is probably advantageous.'''

t = GameReportTemplate('testing2', sample_sm_narrative, sample_lm_narrative, df1, df2, df3, df4, df5, intensity_note, load_note)
t.go()