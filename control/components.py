from control.config import configuration as cfg

def lp_filter(prev, new, a=0.1):
    """Applies a simple low-pass filter to smooth out sensor readings."""
    return prev + a * (new - prev)

def limiter(val, min, max):
    """Limits a value to be within the specified min and max range."""
    if val < min:
        return min
    elif val > max:
        return max
    return val

def rate_of_change(prev, new, max_roc):
    """Limits the rate of change between previous and new values."""
    delta = new - prev
    if abs(delta) > max_roc:
        delta = max_roc if delta > 0 else -max_roc
    return prev + delta

def pi_controller(e, i, dt, kp=0.1, ki=1.0, imax=10, imin=-10):
    """A simple PI controller implementation."""
    i += e * dt

    if i < imin:
        i = imin
    elif i > imax:
        i = imax

    ppart = kp * e
    ipart = ki * i
    output = ppart + ipart
    #print(ppart, ipart, i)
    return output, ppart, ipart, i

def heating_curve(t_outdoor, p=0, slope=1.0, n=0.97, t_base=20):
    """Calculates the required supply temperature based on outdoor temperature."""
    if t_outdoor >= 22:
        return t_base
    else:
        sign = (t_outdoor - 22) / abs(t_outdoor - 22)
        return p + t_base - ((abs(t_outdoor - 22) ** n) * slope * sign)

class HeatingController:

    def __init__(self,
                 id,
                 outside_temp, 
                 outside_temp_remote, 
                 outside_temp_remote_wchill, 
                 winddir, 
                 inside_temp,
                 setpoint):
        
        self.id = id
        self.outside_temp = outside_temp
        self.outside_temp_remote = outside_temp_remote
        self.outside_temp_remote_wchill = outside_temp_remote_wchill
        self.winddir = winddir
        self.inside_temp =  inside_temp
        self.setpoint = setpoint

        self.p = 0
        self.i = 0
        self.i_ = 0

        self._signal = None

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, signal):
        self._signal = signal
    
    @property
    def error(self):
        '''
        Calculate the error. 
        Error is positive if the actual temperature is lower than the setpoint.
        '''
        return self.setpoint - self.inside_temp

    @property
    def outside_temp_bias(self):
        '''
        Calculate the amount to adjust the outside temperature measurement by.
        Adjustment amount is negative if the outside apparent outside temperature
        should be lower than the measured outside temperature.
        '''
        # kwnd = self.get_kwind()
        return self.outside_temp_remote_wchill - self.outside_temp_remote
    
    @property
    def pio(self):
        '''
        PI regulator for temperature control.
        Output of the regulator is positive if the error is positive.
        '''
        tc = 1800 #desired integrator tc
        dt = cfg.cycle_time / tc
        pio, p, i, i_ = pi_controller(self.error,
                                      self.i_, 
                                      dt)
        self.p = p
        self.i = i
        self.i_ = i_

        return pio
    
    @property
    def total_bias(self):
        '''
        Amount to adjust the actual outside temeperature by.
        The bias is negative if the controller should output warmer water.
        '''
        return self.outside_temp_bias - self.pio
    
    @property
    def apparent_outside_temp(self):
        '''The apparent outside temperature as calculated and fed to the heating controller.'''
        return self.outside_temp + self.total_bias

    @property
    def flow_temp(self):
        return heating_curve(self.apparent_outside_temp)

    # def get_kwind(self):
    #     return 1
    #     #temporary simplification

    #     if self.winddir < 90:
    #         k = 1
    #     elif self.winddir < 240:
    #         k = 0
    #     else:
    #         k = 1
        
    #     return k

    @property
    def payload(self):
        return {
            "signalID": self.id,
            "outside_temp": self.outside_temp,
            "outside_temp_remote": self.outside_temp_remote,
            "outside_temp_remote_wchill": self.outside_temp_remote_wchill,
            "winddir": self.winddir,
            "inside_temp": self.inside_temp,
            "setpoint": self.setpoint,
            "error": self.error,
            "pio": self.pio,
            "p": self.p,
            "i": self.i,
            "outside_temp_bias": self.outside_temp_bias,
            "total_bias": self.total_bias,
            "apparent_outside_temp": self.apparent_outside_temp,
            "flow_temp": self.flow_temp,
            }

        