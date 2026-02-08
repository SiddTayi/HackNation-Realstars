import pandas as pd

df = pd.read_excel(
    '/Users/faseehahmed26/Desktop/FaseehWorld/Interview Prep/realpage/Hackathon/HackNation-Realstars/data/final_ver3.xlsx')
print('Excel Columns:')
for i, col in enumerate(df.columns, 1):
    print(f'{i:2}. {col}')
