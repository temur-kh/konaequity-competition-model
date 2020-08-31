import numpy as np
from scipy import spatial


def get_gps_distance(vec1, vec2):
    lat1 = np.radians(vec1[0])
    lon1 = np.radians(vec1[1])
    lat2 = np.radians(vec2[0])
    lon2 = np.radians(vec2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return min(c, 1.0)


def get_gs_distance(vec1, vec2):
    res = 0.5 * spatial.distance.cosine(vec1, vec2)
    return 0.5 if np.isnan(res) else res
