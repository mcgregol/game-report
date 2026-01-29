from ollama import chat
from ollama import ChatResponse
from ollama import Client
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd
import math

from src.testing import GameReportTemplate

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

#  Create custom client
client = Client(
    host='http://192.168.1.47:11434')

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

#  Convert xlsx to MD
go_dtl_md = df1.to_markdown(index=False)
freshness_md = df2.to_markdown(index=False)
sm_team_md = df3.to_markdown(index=False)
sm_relative_md = df4.to_markdown(index=False)

print(f'{sm_team_md}\n{sm_relative_md}\n{go_dtl_md}\n{freshness_md}\n')

#  Build and send prompt to Ollama for SupraMax metrics
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
print(response.message.content)

print('******************************************************************************************\n------------------------------------------------------------------------------------------\n******************************************************************************************\n')

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
print(response.message.content)

game_report_final = GameReportTemplate(sm_narrative, lm_narrative, 'googly.pdf')

EXIT = input("Press ENTER to exit")