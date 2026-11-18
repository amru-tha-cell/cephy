import math

def angle(a, b, c):
    """Angle ABC in degrees. Coordinates are (x,y) in image pixels."""
    ba = (a[0]-b[0], a[1]-b[1]); bc = (c[0]-b[0], c[1]-b[1])
    den = math.hypot(*ba) * math.hypot(*bc)
    if den == 0: return None
    cosine = max(-1.0, min(1.0, (ba[0]*bc[0] + ba[1]*bc[1]) / den))
    return round(math.degrees(math.acos(cosine)), 2)

def calculate_measurements(points):
    """Uses the project's declared 19-point order. Missing points yield null values."""
    # Landmark indices follow LANDMARK_NAMES in core/config.py. The SNA/SNB
    # construction uses Sella(0), Nasion(1), A(4), B(5); verify point ordering
    # against the annotation protocol used by your ISBI export before clinical use.
    def p(i):
        q = points[i] if len(points) > i else None
        return (q.get('x'), q.get('y')) if q and q.get('x') is not None and q.get('y') is not None else None
    s,n,a,b = p(0),p(1),p(4),p(5)
    sna = angle(s,n,a) if s and n and a else None
    snb = angle(s,n,b) if s and n and b else None
    return {'SNA': sna, 'SNB': snb, 'ANB': round(sna-snb,2) if sna is not None and snb is not None else None,
            'note': 'Pixel-coordinate geometry only. Calibrated clinical measurements require image scale and verified landmark ordering.'}
