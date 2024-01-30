def coverage_cleaning(tracks: list, new_hits_ratio=0.25, new_hits_in_row=6):
    # Track candidates ordered by descending length.
    track_candidates = sorted(tracks, key=len, reverse=True)

    coverage = set()
    proto_tracks = []

    # Naive coverage-based track filtering.
    for track in track_candidates:
        n_new_hits = 0  # Number of uncovered hits in a track.
        n_new_in_row = 0  # Length of a current segment (new hits in a row).
        n_segments = 0  # Number of segments w/ length > threshold.

        for hit in track:
            hit_index = hit[0]
            if hit_index not in coverage:
                n_new_hits += 1
                n_new_in_row += 1
            else:
                if n_new_in_row >= new_hits_in_row:
                    n_segments += 1
                n_new_in_row = 0

        if n_new_in_row >= new_hits_in_row:
            n_segments += 1

        ratio = n_new_hits / len(track)
        if ratio >= new_hits_ratio and n_segments > 0:
            proto_tracks.append(track)
            coverage.update([hit[0] for hit in track])

    return proto_tracks
