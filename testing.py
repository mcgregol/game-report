import pandas as pd

#  Create dataframes & remove BS on top of SM files
df1 = pd.read_excel('player_sm.xlsx', header=1)

#  Convert decimals back to percentages
percent_cols = ['Avg Supra Max Efforts', 'Avg Very High Intensity Efforts']
df1[percent_cols] = df1[percent_cols].map(
    lambda x: f"{x:.2%}" if pd.notna(x) else x
)

#  add and populate rank col
print(len(df1))
df1.insert(0, 'Rank', range(1, len(df1) + 1))

#  convert to MD
vhi_md = df1.to_markdown(index=False)

#  show output (debugging)
print(vhi_md)