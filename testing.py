import pandas as pd

#  Create dataframes
df1 = pd.read_excel('go_dtl.xlsx')
df2 = pd.read_excel('freshness.xlsx')
df3 = pd.read_excel('sm_team.xlsx')
df4 = pd.read_excel('sm_vhi.xlsx')

#  Isolate and sort 3day freshness
df2 = df2.drop(columns=['Freshness (7 day)'])
df2 = df2.sort_values(by=['Freshness (3 day)'])

print(f'GO DTL:\n{df1}')
print(f'Freshness:\n{df2}')
print(f'SM Team:\n{df3}')
print(f'SM VHI Team:\n{df4}')