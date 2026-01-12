from ollama import chat
from ollama import ChatResponse
from ollama import Client
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd

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

#  Trim off 7day and sort 3day
df2 = df2.drop(columns=['Freshness (7 day)', 'DTL', 'CTL'])
df2 = df2.sort_values(by=['Freshness (3 day)'])

#  add and populate rank cols
df1.insert(0, 'Rank', range(1, len(df1) + 1))

print(len(df2))
df2.insert(0, 'Rank', range(1, len(df2) + 1))

print(len(df3))
df3.insert(0, 'Rank', range(1, len(df3) + 1))

print(len(df4))
df4.insert(0, 'Rank', range(1, len(df4) + 1))

#  append % sign to sm files
df3['Total Supra Max Efforts'] = (df3['Total Supra Max Efforts'] * 100).round(3).astype(str) + '%'
df4['Avg Supra Max Efforts'] = (df4['Avg Supra Max Efforts'] * 100).round(3).astype(str) + '%'

#  Convert xlsx to MD
go_dtl_md = df1.to_markdown(index=False)
freshness_md = df2.to_markdown(index=False)
sm_team_md = df3.to_markdown(index=False)
sm_relative_md = df4.to_markdown(index=False)

print(f'{go_dtl_md}\n{freshness_md}\n{sm_team_md}\n{sm_relative_md}')

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
print(response.message.content)

print('******************************************************************************************\n------------------------------------------------------------------------------------------\n******************************************************************************************\n')

#  Build and send prompt to Ollama for Load Metrics
response: ChatResponse = client.chat(model='lm-data-analyst:latest', messages=[
    {
        'role': 'user',
        'content': f'Here is the freshness data:\n{freshness_md}'
    },
    {
        'role': 'user',
        'content': f'Here is the Avg Supra Max data:\n{sm_relative_md}'
    },
    {
        'role': 'user',
        'content': f'Here is the team total Supra Max data:\n{sm_team_md}'
    },
    {
        'role': 'user',
        'content': f'Here is the game-only DTL data:\n{go_dtl_md}'
    }
])
print(response.message.content)

EXIT = input("Press ENTER to exit")