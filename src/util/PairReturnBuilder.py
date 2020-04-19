import numpy as np

def decision_maker(res:float, sign, entry_z:float=2, exit_z:float=0.5):
    if sign==0 and res>entry_z:
        sign="l"
    elif sign==0 and res< - entry_z:
        sign="s"
    else:
        if sign == "s" and res > - exit_z:
            sign=0
        elif sign =="l" and res < exit_z:
            sign=0
    return sign

def signaler(scaled_residuals:np.array):
    sign_vect=[]
    sign=0
    for res in scaled_residuals:
        sign = decision_maker(res, sign)
        sign_vect.append(sign)

    sign_vect[-1]=0  #close position always at end

    return sign_vect

def pair_return_builder(x:np.array, y:np.array, signal_vector:np.array, beta:float):
    r_x = np.log(x[1:]) - np.log(x[:-1])
    r_y = np.log(y[1:]) - np.log(y[:-1])
    r_p = [beta/(beta-1) * rx - ry/(beta-1) if sig == "l" else ry/(beta-1) - beta/(beta-1) * rx if sig == "s" else 0
           for sig, rx, ry in zip(signal_vector, r_x, r_y)]
    return r_p


if __name__ == '__main__':
    '''
    1. check that fake residual vector (u) is appropriately translated into signal vector;
    2. convert signal vector into realized returns on cointegrated pair portfolio
    '''
    u =     [-2.4, -3.0, -2.5, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 2.0, 1.5, 1.0, 0.5, 0.0, -0.5, -1.0, -1.5, -2.0, -2.5]
    exp_sig=[ "s",  "s",  "s",  "s",  "s",  "s",   0,   0,   0,   0,   0, "l", "l", "l", "l", "l",   0,    0,    0,    0,    0,    0]
    x =     [ 123,  134,  122,  133,  142,  139, 136, 133, 145, 141, 134, 129, 128, 127, 130, 132, 135,  145,  142,  132,  131,  129]
    y =     [ 224,  235,  222,  213,  243,  237, 235, 232, 246, 240, 235, 221, 229, 239, 231, 234, 246,  242,  243,  232,  231,  228]
    beta=1.2

    signal_vect = signaler(u)
    # check if signaler works as expected
    print("is signal generated corresponding to the one expected in the example? ==> ", signal_vect == exp_sig)
    print("portolio pair returns: ", pair_return_builder(x, y, signal_vect, beta))

