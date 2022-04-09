import pandas as pd
from pathlib import Path
import os
import requests

cwd = Path(__file__).parent.absolute()
print(cwd)
os.chdir(cwd)

# read csv
df = pd.read_csv('merged.csv')
df['image'] = None
for i in range(len(df)):
    count = i % 6
    df.at[i, 'image'] = 'hdb_image'+str(count)+'.jpg'

#df.drop('Unnamed: 0', axis=1, inplace=True)
df.to_csv('merged.csv', index=False)
