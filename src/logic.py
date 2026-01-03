def clamp(v, a, b):
    return max(a, min(v, b))


def ema(prev, curr, alpha):
    if prev is None:
        return curr
    return (
        int(alpha * curr[0] + (1 - alpha) * prev[0]),
        int(alpha * curr[1] + (1 - alpha) * prev[1]),
    )


def finger_is_up(tip_y, joint_y):
    return tip_y < joint_y


def point_in_rect(p, r):
    x, y = p
    x1, y1, x2, y2 = r
    return x1 <= x <= x2 and y1 <= y <= y2