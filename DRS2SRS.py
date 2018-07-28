import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os.path

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", required = True, help = "path to the .xls or .csv file")
ap.add_argument("-d", "--degree", default = 4, help = "polynomial degree for curve fitting")
args = vars(ap.parse_args())

path = args["file"]
degree = args["degree"]

# Length of the look up table
LUT_LENGTH = 4096

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

    #return  pd.concat([norm_exposure, norm_rgb], axis=1)
    return [norm_exposure, norm_rgb]


def fit_curve(x, y, degree=degree):
    z = np.polyfit(x, y, degree)
    f = np.poly1d(z)
    return f


def generate_data(df):
    print("[Normalizing data]")
    norm_exposure, norm_rgb = normalize(df)
    gmean = geometric_mean(norm_rgb.values.tolist())
    print("[Fitting a " + str(degree) + " degree polynomial]")
    polynomial = fit_curve(norm_exposure, gmean)
    print(polynomial)
    x = np.linspace(0, 1, LUT_LENGTH)
    y = polynomial(x)
    LUT = pd.DataFrame({"Exposure": x, "RGB": y}, index=None)
    #print(LUT)
    LUT.to_csv('LUTdata.csv', index=False, header=True)
    print("[Data has been written to file]")
    plt.plot(x,y)
    plt.show()


def read_file(path):
    ext = os.path.splitext(path)[1][1:]

    if ext == "csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    return df


print("[Reading file]")
df = read_file(path)
generate_data(df)



