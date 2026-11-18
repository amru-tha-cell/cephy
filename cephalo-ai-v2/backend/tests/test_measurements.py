from app.measurements.cephalometry import angle, calculate_measurements

def test_right_angle():
    assert angle((1,0),(0,0),(0,1)) == 90.0

def test_missing_points_return_none():
    result=calculate_measurements([])
    assert result['SNA'] is None and result['SNB'] is None and result['ANB'] is None
