def smooth_damp(current, target, velocity, smooth_time, dt):
    smooth_time = max(smooth_time, 0.0001)
    omega = 2.0 / smooth_time
    x = omega * dt
    exp = 1.0 / (1.0 + x + 0.48 * x * x + 0.235 * x * x * x)
    delta = current - target
    temp = (velocity + omega * delta) * dt
    new_velocity = (velocity - omega * temp) * exp
    new_value = target + (delta + temp) * exp
    return new_value, new_velocity
