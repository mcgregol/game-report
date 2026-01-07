import pandas as pd

#  Create dataframes & remove BS on top of SM files
df1 = pd.read_excel('sm_vhi.xlsx', header=1)

#  add and populate rank col
print(len(df1))
df1.insert(0, 'Rank', range(1, len(df1) + 1))

#  convert to MD
vhi_md = df1.to_markdown(index=False)

#  show output (debugging)
print(vhi_md)