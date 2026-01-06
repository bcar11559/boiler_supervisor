

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

def pid_controller(setpoint, measurement, kp, ki, kd, prev_error, integral, dt):
    """A simple PID controller implementation."""
    error = setpoint - measurement
    integral += error * dt
    derivative = (error - prev_error) / dt if dt > 0 else 0
    output = kp * error + ki * integral + kd * derivative
    return output, error, integral