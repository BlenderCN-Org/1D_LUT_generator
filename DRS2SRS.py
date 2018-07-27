import pandas as pd
import numpy as np

file = "drs2srs.xls"
xl = pd.ExcelFile(file)
df = xl.parse("Sheet1")
df.head()
