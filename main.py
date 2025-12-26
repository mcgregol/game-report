from ollama import chat
from ollama import ChatResponse
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd

#  Hide tkinter
Tk().withdraw()

#  Fetch data files
dtl_file = askopenfilename(title="Select DTL Excel file", filetypes=[("Excel files","*.xlsx")])
freshness_file = askopenfilename(title="Select Freshness Excel file", filetypes=[("Excel files","*.xlsx")])

#  Create dataframes
df1 = pd.read_excel(dtl_file)
df2 = pd.read_excel(freshness_file)

#  Convert xlsx to text
dtl_text = df1.to_string(index=False)
freshness_text = df2.to_string(index=False)

#  Print text data for user
print(f'**************************************************************\n{dtl_text}\n\n{freshness_text}\n**************************************************************')

#  Build and send prompt to Ollama
response: ChatResponse = chat(model='ministral-data-analyst:latest', messages=[
    {
        #  for system role tweaks, use modelfile
        'role': 'user',
        'content': f'Here are the DTL scores:\n{dtl_text}'
    },
    {
        'role': 'user',
        'content': f'Here are the freshness scores:\n{freshness_text}'
    }
    ])

print(response.message.content)