# Import and read data 
import pandas as pd
df = pd.read_csv('dancedata.csv', encoding='latin1')
print(df.head())
# t test if speed of bpm is normally distributed