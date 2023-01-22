import pandas as pd

file_path = './data/2022/9/Zagreb - AMBROZIJA pelud za 9.2022'

df = pd.read_csv(file_path, header=None, sep='  ', engine='python')

# print(df)

x = df.iloc[:, 1]
# y = df.iloc[:, 0]
#
print(x)
# print(y)
