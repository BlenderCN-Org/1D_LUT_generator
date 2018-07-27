import pandas as pd
import numpy as np

def geometric_mean(nums):
    '''
    Computes the geometric mean of nums.
    Given a list nums = x1,x2...xn, the mean is given as:

            mean = (x1*x2...*xn)**(1/n)

    :param nums:
    :return geometric mean of nums:
    '''
    return [(reduce(lambda x, y: x * y, l)) ** (1.0 / len(l)) for l in nums]


def normalize(data):
    '''
    Normalizes exposure and rgb values between 0 and 1.

    :param nums:
    :return normalized exposure and rgb values:
    '''

    # Normalizing exposure
    min_val = data['Exposure'].min()
    max_val = data['Exposure'].max()
    val_range = max_val - min_val
    norm_exposure = (data['Exposure'] - min_val) / (val_range)

    # Normalizing RGB values
    norm_rgb = data[['R','G','B']] / 255.0

    return  pd.concat([norm_exposure, norm_rgb], axis=1)

csv_file = "drs2srs.csv"
df = pd.read_csv(csv_file)

d = normalize(df)
gmean = geometric_mean(d[['R','G','B']].values.tolist())
print(gmean)