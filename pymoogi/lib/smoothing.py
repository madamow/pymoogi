from read_out_files import out2_synth, out3_synth
import numpy as np
# from scipy.signal import gaussian
import matplotlib.pyplot as plt

out2 = out2_synth('/Users/madamow/Science/pymoogi/example/out2', delimiter='ALL')
data = np.array(out2[-1][-1])
slam, sflux = out3_synth('/Users/madamow/Science/pymoogi/example/out3')

ln2 = np.log(2)

# this is smoothing MOOG style

def vmacro():
    """ (Copy from Vmacro.f from MOOG)
    This routine computes, by linear interpolation, a point along a
    radial-tangential macroturbulence profile.  This routine was written by
    Suchitra Balachandran, and is based on the work of Gray 1992, in
    "The Obs. & Anal. of Stell. Phot", p. 409.  These functions have
    been computed and included in the data arrays below:
    xrt = velocity / zeta_RT
    yrt = value at xrt
    The area under the function is normalized to unity
    """
    xrt = np.arange(0.0001, 2.5, 0.01)
    yrt = np.array([
        1.128380, 1.126790, 1.088790, 1.069200, 1.049990, 1.031020, 1.012720,
        0.993719, 0.975411, 0.957327, 0.939467, 0.921830, 0.904416, 0.887224,
        0.870264, 0.853520, 0.836978, 0.820671, 0.805960, 0.788712, 0.773060,
        0.757624, 0.742405, 0.727394, 0.712603, 0.698026, 0.683659, 0.669504,
        0.655559, 0.641822, 0.628292, 0.614969, 0.601851, 0.588936, 0.576224,
        0.563713, 0.551402, 0.539288, 0.527372, 0.515651, 0.504123, 0.492788,
        0.481644, 0.470689, 0.459921, 0.449339, 0.438813, 0.428727, 0.418693,
        0.408839, 0.399161, 0.389660, 0.382276, 0.371177, 0.362193, 0.353376,
        0.344727, 0.336242, 0.327921, 0.319760, 0.311759, 0.303916, 0.296228,
        0.288693, 0.281342, 0.273786, 0.266697, 0.260087, 0.253292, 0.246640,
        0.240128, 0.233754, 0.227516, 0.221413, 0.215442, 0.209602, 0.203891,
        0.198305, 0.192845, 0.187508, 0.182291, 0.177193, 0.172213, 0.167347,
        0.162595, 0.157955, 0.153423, 0.149000, 0.144683, 0.140469, 0.136358,
        0.132347, 0.128434, 0.124619, 0.120898, 0.117271, 0.113735, 0.110289,
        0.106931, 0.103659, 0.100472, 0.097368, 0.094346, 0.091403, 0.088538,
        0.085750, 0.083037, 0.080397, 0.077829, 0.075331, 0.072902, 0.070540,
        0.068244, 0.066012, 0.063844, 0.061736, 0.059689, 0.057701, 0.055770,
        0.053895, 0.052075, 0.050308, 0.048594, 0.046930, 0.045317, 0.043751,
        0.042233, 0.040761, 0.039334, 0.037951, 0.036611, 0.035316, 0.034058,
        0.032839, 0.031659, 0.030516, 0.029410, 0.028339, 0.027303, 0.026300,
        0.025330, 0.024392, 0.023484, 0.022607, 0.021759, 0.020939, 0.020147,
        0.019382, 0.018643, 0.017928, 0.017239, 0.016573, 0.015930, 0.015309,
        0.014711, 0.014133, 0.013576, 0.013038, 0.012520, 0.012021, 0.011539,
        0.011075, 0.010627, 0.010196, 0.009781, 0.009381, 0.008996, 0.008626,
        0.008269, 0.007925, 0.007595, 0.007277, 0.006972, 0.006678, 0.006395,
        0.006123, 0.005862, 0.005611, 0.005369, 0.005138, 0.004915, 0.004701,
        0.004496, 0.004299, 0.004110, 0.003929, 0.003755, 0.003588, 0.003428,
        0.003274, 0.003127, 0.002986, 0.002850, 0.002721, 0.002597, 0.002478,
        0.002364, 0.002255, 0.002151, 0.002051, 0.001955, 0.001864, 0.001776,
        0.001692, 0.001612, 0.001536, 0.001463, 0.001393, 0.001326, 0.001262,
        0.001201, 0.001143, 0.001087, 0.001034, 0.000984, 0.000935, 0.000889,
        0.000845, 0.000803, 0.000763, 0.000725, 0.000689, 0.000654, 0.000621,
        0.000590, 0.000560, 0.000531, 0.000504, 0.000478, 0.000454, 0.000430,
        0.000408, 0.000387, 0.000366, 0.000347, 0.000329, 0.000312, 0.000295,
        0.000280, 0.000265, 0.000251, 0.000237, 0.000224, 0.000212, 0.000201,
        0.000190, 0.000180, 0.000170, 0.000161, 0.000152
    ])
    return xrt, yrt

def gauss_funt(smpar, k):
    # Here: smpar == gaussian fwhm
    aa = 4. * ln2 / (smpar * smpar)
    return  np.exp(-aa * k ** 2)


def lorentzian_func(smpar, k):
    # Here: smpar == lorentzian fwhm
    sigma = 0.5 * smpar
    return (sigma * sigma) / ((sigma *sigma) + (k * k))


def macrot_func(k, wavemac):
    wavei = k / wavemac
    xrt, yrt = vmacro()
    return np.interp(wavei, xrt,yrt)


def vrot_func(dlamlim, step, limbdark=0):
    """ (copy from Smooth.f from MOOG)
    Compute a stellar rotational broadening function; this follows
    D. F. Gray, 1976, "The Obs. & Anal. of Stell. Phot", p394-9
    """
    pi = np.pi
    bottom = dlamlim * pi * (1. - limbdark / 3.)
    c1 = 2. * (1. - limbdark) / bottom
    c2 = 0.5 * limbdark * pi / bottom
    prot0 = c1 + c2

    jdelrot = int(dlamlim / step)
    k = np.arange(0, step*(jdelrot), step)
    term = 1. - (k / dlamlim) ** 2
    p = c1*np.sqrt(term) + c2*term
    return p, prot0


def get_kernel(sspec, smpar, type='g'):
    step = sspec[0][2]
    ssize = sspec[-1].size
    k = np.arange(step, ssize, step)
    pfact = 1.
    if type == 'g':
        p = gauss_funt(smpar, k)
    elif type == 'l':
        p = lorentzian_func(smpar, k)
    elif type == 'm':
        start, stop = sspec[0][:2]
        wavemac = (start + stop)/2.* smpar / 3.0e5
        p = macrot_func(k, wavemac)
    elif type == 'v':
        start, stop = sspec[0][:2]
        dlamlim = (start + stop) / 2. * smpar / 3.0e5
        p, pfact = vrot_func(dlamlim, step)

    cut = np.where(p >= 0.02)[0][-1] + 2
    p = p[:cut]
    power = 2. * np.sum(p) + pfact

    return p, power, pfact


# The convolution must take all synthetic spectra at once. Kernel will be the same,
# but the results of convvolution will be different for each syntetic spectra

def convolution_moog_style(flux, kernel, power, pfact=1):
    sf = np.ones_like(flux)
    ks = kernel.size
    new_kernel = np.concatenate([kernel[::-1], np.array([1.]), kernel])
    # wywal ten new_kernel
    print(new_kernel)
    for i, f in enumerate(sf):
        if i >= ks and flux.size - i > ks:
            print(flux[i-ks:i+ks+1])
            sf[i] = np.sum(flux[i-ks:i+ks+1]*new_kernel) #/ power
            print(i, sf[i])
            exit()
    return sf


step = out2[0][0][2]

k, power, pfact = get_kernel(out2[-1], 5., type='v')
print(power, pfact)
sf = convolution_moog_style(out2[-1][-1], k, power,pfact)

plt.plot(out2[-1][-1], label='not')
plt.plot(sf, label='my smooth')
plt.plot(sflux[-1], label='moog smooth')
plt.legend()
plt.show()