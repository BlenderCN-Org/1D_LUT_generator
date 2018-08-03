from string import Template
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os.path

#TODO: clean up code, move constants and templates to seperate file

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", required = True, help = "path to the .xls or .csv file")
ap.add_argument("-d", "--degree", default = 4, help = "polynomial degree for curve fitting")
args = vars(ap.parse_args())

path = args["file"]
degree = args["degree"]

# Length of the look up table
LUT_LENGTH = 4096

# Camera Info
CAMERA_NAME = "Nikon"
CAMERA_MODEL = "D5200"
ISO = "100"
COLOUR_PROFILE = "NeutralGamma"

# output file
LUT_OUTPUT_FILE = "%s_%s_ISO_%s_%s.spi1d" % (CAMERA_NAME, CAMERA_MODEL, ISO, COLOUR_PROFILE)

# OCIO config file settings
NAME = "%s %s ISO_%s %s" % (CAMERA_NAME, CAMERA_MODEL, ISO, COLOUR_PROFILE)
DESCRIPTION = "Description String Here"
MAX_STOPS_ABOVE_0 = 3
MIN_STOPS_BELOW_0 = -4.5
CUSTOM_LUT_NAME = LUT_OUTPUT_FILE.split('.')[0]
TOTAL_DYNAMIC_RANGE = MAX_STOPS_ABOVE_0 - MIN_STOPS_BELOW_0
INPUT_MIDDLE_GRAY = 0.18
HIGH = (2**MAX_STOPS_ABOVE_0)*INPUT_MIDDLE_GRAY
LOW = (2**MIN_STOPS_BELOW_0) * INPUT_MIDDLE_GRAY
ALLOCATION_VAR2 = np.log2(HIGH)
ALLOCATION_VAR1 = np.log2(LOW)


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

    return [norm_exposure, norm_rgb]


def fit_curve(x, y, degree=degree):
    z = np.polyfit(x, y, degree)
    f = np.poly1d(z)

    # Scatter plot
    plt.scatter(x, y, label="original")

    # Line plot
    plt.plot(x, f(x), 'r-', label="fitted line")
    plt.xlabel("Exposure")
    plt.ylabel("RGB")
    plt.title(str(f))
    plt.legend(loc='upper left')

    plt.savefig('plot.png')
    plt.close()

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

    if os._exists(LUT_OUTPUT_FILE):
        os.remove(LUT_OUTPUT_FILE)

    with open(LUT_OUTPUT_FILE, 'a') as myfile:
        myfile.write("Version 1 \nFrom 0.000000 1.000000 \nLength 4096 \nComponents 1 \n{\n")
        np.savetxt(myfile, y, fmt='%.11f', delimiter=' ')
        myfile.write("}")

    print("[Creating file %s]" % LUT_OUTPUT_FILE)


def Save_Config_File_Entry():
    '''
    Generates the preamble to be appended in the config.ocio file in blender, it is saved as stanza.txt
    :return:
    '''
    stanza = """
      - !<ColorSpace>
        name: $name
        family:
        equalitygroup:
        bitdepth: $bitdepth
        description: |
          $description
        isdata: $isdata
        allocation: $allocation
        allocationvars: [$var1, $var2]
        from_reference: !<GroupTransform>
            children:
                - !<AllocationTransform> {allocation: lg2, vars: [$var1, $var2]}
                - !<FileTransform> {src: $spi1d_file, interpolation: best}      
    """

    s = Template(template=stanza)
    d = {'name': NAME,
         'bitdepth': '32f',
         'description': DESCRIPTION,
         'isdata': 'false',
         'allocation': 'lg2',
         'var1': ALLOCATION_VAR1,
         'var2': ALLOCATION_VAR2,
         'spi1d_file': LUT_OUTPUT_FILE}
    s = s.substitute(d)

    print("[Creating file stanza.txt]")
    with open("stanza.txt", 'w') as stanza:
        stanza.write(s)


def read_file(path):
    '''
    Read .csv or .xls file fro a specified path
    :param path:
    :return:
    '''
    ext = os.path.splitext(path)[1][1:]

    if ext == "csv":
        df = pd.read_csv(path)
    else:
        #TODO: install libraries to read excel files
        df = pd.read_excel(path)

    return df


print("[Reading file]")
df = read_file(path)
generate_data(df)
Save_Config_File_Entry()
print("\n\n=================== INSTRUCTIONS ======================\n")
print("[1] Copy %s into datafiles/colormanagement/lut/ in the Blender directory" % LUT_OUTPUT_FILE)
print('[2] Copy the contents of stanza.txt into Config.ocio under the section that starts with "Colorspaces:"')
print('[3] Copy and paste the following text under your appropriate display in Config.ocio:')
print('        - !<View> {name: %s, colorspace: %s}' % (NAME, NAME))
print('Note: example of a display is sRGB, use the appropriate one for your monitor.')
print('[4] You should fild your custom color transform listed in the color management section in blender.')
print('[DONE]')
