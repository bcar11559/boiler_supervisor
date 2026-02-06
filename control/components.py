import random
from initialise import is_micropython
from control.signals import Signal
from control.exceptions import EmulationError, HeatingControllerError
import logging

logger = logging.getLogger(__name__)

if is_micropython:
    pass
else:
    import random
    import numpy as np


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
    return output, ppart, ipart, i


class HeatingController:

    cycle_time = 5
    alias_mapping = {
        "outside_temp_local" : "outside_temp_local",
        "outside_temp_remote" : "outside_temp_remote",
        "wind_dir" : "wind_dir",
        "wind_speed" : "wind_speed",
        "inside_temp_apparent" : "inside_temp_apparent",
        "setpoint" : "setpoint"
    }

    MIN_OUTSIDE_TEMP = -40
    MAX_OUTSIDE_TEMP = 40
    MIN_WIND_SPEED = 0
    MAX_WIND_SPEED = 35
    MIN_WIND_DIR = 0
    MAX_WIND_DIR = 360
    MIN_INSIDE_TEMP = -10
    MAX_INSIDE_TEMP = 30
    MIN_SETPOINT = 5
    MAX_SETPOINT = 30

    def __init__(self,
                 outside_temp_local=0.0, 
                 outside_temp_remote=0.0, 
                 wind_dir=0.0, 
                 wind_speed=0.0, 
                 inside_temp_apparent=21,
                 setpoint=21):
        
        self.outside_temp_local = outside_temp_local
        self.outside_temp_remote = outside_temp_remote
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed
        self.inside_temp_apparent =  inside_temp_apparent
        self.setpoint = setpoint
        self.__em_setpoint_span__ = 4
        self.__em_setpoint_baseline__ = setpoint - self.__em_setpoint_span__/2

        self.p = 0
        self.i = 0
        self.i_ = 0

    def validate_value(value, minval, maxval):
        print(3, value)

        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except ValueError:
                msg = f"{value} was not converted."
                logger.exception(msg)
                raise HeatingControllerError(msg)
        
        msg = f"{value} is out of range {minval}-{maxval}."
        if value < minval:
            logger.warning(msg)
            return minval
        elif value > maxval:
            logger.warning(msg)
            return maxval
        else:
            return value

    @property
    def outside_temp_local(self):
        return self._outside_temp_local
    
    @outside_temp_local.setter
    def outside_temp_local(self, value):
        max_ = HeatingController.MAX_OUTSIDE_TEMP
        min_ = HeatingController.MIN_OUTSIDE_TEMP
        self._outside_temp_local = HeatingController.validate_value(value, min_, max_)
    
    @property
    def outside_temp_remote(self):
        return self._outside_temp_remote

    @outside_temp_remote.setter
    def outside_temp_remote(self, value):
        max_ = HeatingController.MAX_OUTSIDE_TEMP
        min_ = HeatingController.MIN_OUTSIDE_TEMP
        self._outside_temp_remote = HeatingController.validate_value(value, min_, max_)
    
    @property
    def windchill_temp(self):
        if self.outside_temp_remote > 10 or self.wind_speed < 2:
            return self.outside_temp_remote
        elif self.outside_temp_remote < -40:
            temp = -40
        elif speed > 35:
            speed = 35
        else:
            return 13.12 + (0.6215 * temp) - (13.956 * (speed ** 0.16)) + (0.48669 * temp * (speed ** 0.16))

    
    @property
    def error(self):
        '''
        Calculate the error. 
        Error is positive if the actual temperature is lower than the setpoint.
        '''
        return self.setpoint - self.inside_temp_apparent

    @property
    def outside_temp_bias(self):
        '''
        Calculate the amount to adjust the outside temperature measurement by.
        Adjustment amount is negative if the outside apparent outside temperature
        should be lower than the measured outside temperature.
        '''
        # kwnd = self.get_kwind()
        return self.windchill_temp - self.outside_temp_remote
    
    @property
    def pio(self):
        '''
        PI regulator for temperature control.
        Output of the regulator is positive if the error is positive.
        '''
        tc = 1800 #desired integrator tc
        dt = HeatingController.cycle_time / tc
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
        return self.outside_temp_local + self.total_bias

    def heating_curve(self, t_outdoor, p=0, slope=1.0, n=0.97, t_base=20):
        """Calculates the required supply temperature based on outdoor temperature."""
        if t_outdoor >= 22:
            return t_base
        else:
            sign = (t_outdoor - 22) / abs(t_outdoor - 22)
            return p + t_base - ((abs(t_outdoor - 22) ** n) * slope * sign)


    @property
    def flow_temp(self):
        return self.heating_curve(self.apparent_outside_temp)

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

    def update_values(self):
        for id, alias in HeatingController.alias_mapping.items():
            
            # Get the data source for the signal
            src = Signal.get_signal_with_id(id)
            print(2, id, src.__dict__)

            # Get the value of the signal in the data source
            value = getattr(src.source, "value")

            # Set the value in the heating controller
            if getattr(self, id) != value:
                setattr(self, id, value)
            # if src:
            #     try:
            #         value = getattr(src, alias)
            #         print(4, alias, value)
            #     except AttributeError:
                    
            #         print(5, id, value)
            #     else:
            #         setattr(self, id, value)
                
    @property
    def payload(self):
        return {
            "signalID": "heating_controller",
            "outside_temp_local": self.outside_temp_local,
            "outside_temp_remote": self.outside_temp_remote,
            "windchill_temp": self.windchill_temp,
            "wind_dir": self.wind_dir,
            "inside_temp_apparent": self.inside_temp_apparent,
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
    
    def __str__(self):
        if is_micropython:
            return (f"HC: T_out={self.outside_temp_remote:.2f} °C, "
                    f"T_in={self.inside_temp_apparent:.2f} °C, "
                    f"Setp={self.setpoint:.2f} °C, "
                    f"Error={self.error:.2f} °C, "
                    f"Pio={self.pio:.2f}, "
                    f"Flow={self.flow_temp:.2f} °C")
        else:
            return (f"HC: T_out={self.outside_temp_remote:.2f} °C, "
                    f"T_in={self.inside_temp_apparent:.2f} °C, "
                    f"Setp={self.setpoint:.2f} °C, "
                    f"Error={self.error:.2f} °C, "
                    f"Pio={self.pio:.2f}, "
                    f"Flow={self.flow_temp:.2f} °C, "
                    f"emloss={self.em_ploss:.2f} W, " 
                    f"eminput={self.em_input_power:.2f} W, "
                    f"emdiffgain={self.em_diff_gain:.2f}")

    # Emulated methods for testing without real sensors/actuators

    def em_setpoint(self):
        if is_micropython:
            raise EmulationError("em_setpoint can only be used in emulation mode.")           
        r = random.random()*self.__em_setpoint_span__
        self.setpoint = self.__em_setpoint_baseline__ + r

    def em_inside_temp(self):
        if is_micropython:
            raise EmulationError("em_inside_temp can only be used in emulation mode.") 
        self.inside_temp_apparent += self.em_diff_gain

    @property
    def em_input_power(self, Pnom=15000, delta_t=10):
        if is_micropython:
            raise EmulationError("em_inputpower can only be used in emulation mode.")  
        t_return = self.flow_temp - delta_t
        A = (self.flow_temp - self.inside_temp_apparent) / (t_return - self.inside_temp_apparent)
        dTln = (self.flow_temp - t_return) / np.log(A) 
        return Pnom * (dTln / 49.83289) ** 1.3

    @property
    def em_diff_gain(self, kdiff=0.0001):
        if is_micropython:
            raise EmulationError("em_diff_gain can only be used in emulation mode.") 
        return(self.em_input_power - self.em_ploss)*kdiff

    @property
    def em_ploss(self, kloss=150):
        return (self.inside_temp_apparent - self.windchill_temp) * kloss