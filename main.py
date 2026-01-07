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
df2 = df2.drop(columns=['Freshness (7 day)'])
df2 = df2.sort_values(by=['Freshness (3 day)'])

#  Convert xlsx to MD
go_dtl_md = df1.to_markdown(index=False)
freshness_md = df2.to_markdown(index=False)
sm_team_md = df3.to_markdown(index=False)
sm_relative_md = df4.to_markdown(index=False)

#  Print text data for user
#print(f'**************************************************************\n{go_dtl_md}\n\n{freshness_md}\n\n{sm_team_md}\n\n{sm_relative_md}\n**************************************************************')

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
        'content': f'Here is the freshness data containing 3day freshness:\n{sm_relative_md}'
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