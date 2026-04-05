from ollama import ChatResponse
from ollama import Client
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pandas as pd
import math

from src.gr_template import GameReportTemplate

OLLAMA_HOST = 'http://192.168.1.47:11434'

###########################################
#  Define function for creating data ranges
###########################################
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

################################
#  Gather other data params from user
################################
rn = asksaveasfilename()
opponent = input('Enter opposing team name: ')
game_date = input('Enter game date(mm/dd/yy): ')
intn = input('Enter intensity note: ')
ln = input('Enter load note: ')
ibn = input('Enter intensity note by period: ')
num_intensity = input('Enter intensity player count(blank for default): ')
num_freshness = input('Enter player freshness player count(blank for default): ')


###############################
#  Creates narratives with qwen
###############################
#  Create custom client
client = Client(
    host=OLLAMA_HOST,
    timeout=1)

#  Hide tkinter
Tk().withdraw()

#  Fetch data files
go_dtl_file = askopenfilename(title="Select game-only DTL Excel file", filetypes=[("Excel files","*.xlsx")])
freshness_file = askopenfilename(title="Select Freshness Excel file", filetypes=[("Excel files","*.xlsx")])
sm_team_file = askopenfilename(title="Select SupraMax team file", filetypes=[("Excel files","*.xlsx")])
sm_relative_file = askopenfilename(title="Select SupraMax relative file", filetypes=[("Excel files","*.xlsx")])
ib_period_file = askopenfilename(title="Select intensity band by period file", filetypes=[("Excel files","*.xlsx")])

#  Create dataframes for qwen
df1 = pd.read_excel(go_dtl_file)
df2 = pd.read_excel(freshness_file)
df3 = pd.read_excel(sm_team_file, header=1)
df4 = pd.read_excel(sm_relative_file, header=1)
df5 = pd.read_excel(ib_period_file)

#  create stock dataframes
stock_df1 = pd.read_excel(go_dtl_file)
stock_df2 = pd.read_excel(freshness_file)
stock_df3 = pd.read_excel(sm_team_file, header=1)
stock_df4 = pd.read_excel(sm_relative_file, header=1)
stock_df5 = pd.read_excel(ib_period_file)

#  #  Swap placement of tdDTL and 3day && Trim off 7day and sort 3day
df2 = df2.drop(columns=['Freshness (7 day)', 'CTL'])
df2 = df2.sort_values(by=['Freshness (3 day)'])
stock_df2 = stock_df2.sort_values(by=['Freshness (3 day)'])

#  trim player count if user specifies
if num_freshness.strip() != '':
    pc = int(num_freshness)

    df1 = df1.head(pc)
    df2 = df2.head(pc)

if num_intensity.strip() != '':
    pc = int(num_intensity)

    df3 = df3.head(pc)
    df4 = df4.head(pc)

df2.insert(3, 'DTL', df2.pop('DTL'))

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

#  append % sign to sm files for qwen
df3['Total Supra Max Efforts'] = (df3['Total Supra Max Efforts'] * 100).round(3).astype(str) + '%'
df4['Avg Supra Max Efforts'] = (df4['Avg Supra Max Efforts'] * 100).round(3).astype(str) + '%'

#  append % sign to stock files
stock_df3['Total Supra Max Efforts'] = (stock_df3['Total Supra Max Efforts'] * 100).round(3).astype(str) + '%'
stock_df4['Avg Supra Max Efforts'] = (stock_df4['Avg Supra Max Efforts'] * 100).round(3).astype(str) + '%'
stock_df4['Avg Very High Intensity Efforts'] = (stock_df4['Avg Very High Intensity Efforts'] * 100).round(3).astype(str) + '%'

#  Convert xlsx to MD
go_dtl_md = df1.copy().apply(lambda c: c.round(2) if pd.api.types.is_numeric_dtype(c) else c).to_markdown(index=False)
freshness_md = df2.copy().apply(lambda c: c.round(2) if pd.api.types.is_numeric_dtype(c) else c).to_markdown(index=False)
sm_team_md = df3.to_markdown(index=False)
sm_relative_md = df4.to_markdown(index=False)

print(f'{sm_team_md}\n{sm_relative_md}\n{go_dtl_md}\n{freshness_md}\n')

print('\nSending to Qwen...\nWorking...')

#  Build and send prompt to Ollama for SupraMax metrics
try:
    response: ChatResponse = client.chat(model='sm-data-analyst:latest', messages=[
        {
            #  for system role tweaks, use modelfile
            'role': 'user',
            'content': f'Here is data including the Avg Supra Max Efforts:\n{sm_relative_md}'
        },
        {
            'role': 'user',
            'content': f'Here is data including the team total Supra Max data:\n{sm_team_md}'
        },
        {
            'role': 'user',
            'content': f'Here is the game-only DTL data:\n{go_dtl_md}'
        }
    ])
    sm_narrative = response.message.content

    print('SupraMax metrics complete')

    #  Build and send prompt to Ollama for Load Metrics
    response: ChatResponse = client.chat(model='lm-data-analyst:latest', messages=[
        {
            'role': 'user',
            'content': f'Here is the freshness & total day DTL data:\n{freshness_md}'
        },
        {
            'role': 'user',
            'content': f'Here is the game-only DTL data:\n{go_dtl_md}'
        }
    ])
    lm_narrative = response.message.content

    print('Load Metrics complete\nDone processing with Qwen!')
except Exception as e:
    print('Timeout Qwen\nUsing sample data instead...')
    #  Testing block
    #  Simulates Qwen
    with open('docs/sm_narrative', 'r') as f:
        sm_narrative = f.read()
    with open('docs/lm_narrative', 'r') as f:
        lm_narrative = f.read()

##########################
#  Build and create report
##########################
t = GameReportTemplate(
    rn,
    opponent,
    game_date,
    sm_narrative,
    lm_narrative,
    stock_df1,
    stock_df2,
    stock_df3,
    stock_df4,
    stock_df5,
    intn,
    ln,
    ibn)
t.go()

EXIT = input("Press ENTER to close...")