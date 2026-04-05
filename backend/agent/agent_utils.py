import numpy as np
# ------------------------------
# cosine similarity
# ------------------------------
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
