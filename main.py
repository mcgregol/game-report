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
df3 = pd.read_excel(sm_team_file)
df4 = pd.read_excel(sm_relative_file)

#  Convert xlsx to text
go_dtl_text = df1.to_string(index=False)
freshness_text = df2.to_string(index=False)
sm_team_text = df3.to_string(index=False)
sm_relative_text = df4.to_string(index=False)

#  Print text data for user
#print(f'**************************************************************\n{go_dtl_text}\n\n{freshness_text}\n**************************************************************')


#  Build and send prompt to Ollama
response: ChatResponse = client.chat(model='ministral-data-analyst:latest', messages=[
    {
        #  for system role tweaks, use modelfile
        'role': 'user',
        'content': f'Here is the Player SupraMax data:\n{sm_relative_text}'
    },
    {
        'role': 'user',
        'content': f'Here is the SupraMax data relative to team totals:\n{sm_team_text}'
    },
    {
        'role': 'user',
        'content': f'Here is the game-only DTL data:\n{go_dtl_text}'
    }
    ])

print(response.message.content)

EXIT = input('Press ENTER to exit')

'''
{
        'role': 'user',
        'content': f'Here are the freshness scores:\n{freshness_text}'
    },
'''