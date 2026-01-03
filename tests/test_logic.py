from src.logic import clamp, ema, finger_is_up, point_in_rect


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(20, 0, 10) == 10


def test_ema():
    assert ema(None, (10, 10), 0.5) == (10, 10)
    assert ema((0, 0), (10, 10), 0.5) == (5, 5)


def test_finger():
    assert finger_is_up(10, 20)
    assert not finger_is_up(30, 20)


def test_rect():
    assert point_in_rect((5, 5), (0, 0, 10, 10))
    assert not point_in_rect((15, 5), (0, 0, 10, 10))