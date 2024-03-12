from post_processing.merging.merging import get_vector, get_vector_length
from time import time


def remove_outliers(tracks: list):
    print("Start removing outliers")
    start = time()
    for track in tracks:
        i = 0
        while i < len(track) - 2:
            vec_1 = get_vector(track[i], track[i + 1])
            vec_2 = get_vector(track[i], track[i + 2])
            if get_vector_length(vec_1) > get_vector_length(vec_2) * 1.4:
                track.remove(track[i + 1])
            else:
                i += 1
    print(f"Removing outliers completed in {time() - start} seconds")
    return tracks
