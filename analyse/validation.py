import pandas as pd


def replace_hits_to_track_id(tracks, hits):
    tracks_hits = []
    for i in range(len(tracks)):
        tracks_hits.append([])
        for hit in tracks[i]:
            hit_id = int(hit[0])
            truth_track_id = int(hits[hit_id][3])
            tracks_hits[i].append(truth_track_id)
    return tracks_hits


def get_real_tracks(track_dict, n):
    real_track_list = []
    for tack_id, hit_list in track_dict.items():
        if len(hit_list) >= n:
            real_track_list.append(tack_id)
    return real_track_list


def get_characteristics(tracks, hits, n, ratio):
    reco_tracks = set()
    fake_tracks = set()
    duplicate_tracks = []

    # Replace hits in track with id of their real track
    tracks_hits = replace_hits_to_track_id(tracks, hits)
    for i in range(len(tracks)):
        if len(tracks[i]) < n:
            continue

        # Find the most common real track id in reco track
        reco_track_id = max(tracks_hits[i], key=tracks_hits[i].count)

        # Check duplicates
        if reco_track_id in reco_tracks:
            duplicate_tracks.append(reco_track_id)
            continue

        # Check ratio and mark track as reco or fake
        if tracks_hits[i].count(reco_track_id) / len(tracks_hits[i]) >= ratio:
            reco_tracks.add(reco_track_id)
        else:
            fake_tracks.add(i)
    return reco_tracks, fake_tracks, duplicate_tracks


def calc_characteristics(tracks,
                         hit_list,
                         track_dict,
                         track_id_dict=None,
                         min_length_real=9,
                         min_length_proto=6,
                         ratio=0.5):
    # Get all lists of necessary data
    reco_track_list, fake_track_list, duplicate_track_list = get_characteristics(tracks,
                                                                                 hit_list,
                                                                                 min_length_proto,
                                                                                 ratio)
    real_track_list = get_real_tracks(track_dict, min_length_real)

    # Remove secondary track id from data if in necessary
    if track_id_dict:
        for track_id, is_primary in track_id_dict.items():
            if track_id in real_track_list and not is_primary:
                real_track_list.remove(track_id)

    # Remove short real track from recognized data
    reco_track_list = list(filter(lambda x: x in real_track_list, reco_track_list))
    fake_track_list = list(filter(lambda x: x in real_track_list, fake_track_list))
    duplicate_track_list = list(filter(lambda x: x in real_track_list, duplicate_track_list))

    # Save table of reco and not reco tracks
    # save_recognised_logo(reco_track_list, real_track_list)

    # Calc characteristics
    num_real_track = len(real_track_list)
    num_reco_track = len(reco_track_list)
    num_fake_track = len(fake_track_list)
    num_duplicate_track = len(duplicate_track_list)
    num_reco_dupl_track = num_reco_track + num_duplicate_track
    num_proto_track = num_reco_dupl_track + num_fake_track

    characteristic_dict = {
        "efficiency": num_reco_track / num_real_track if num_real_track else 0,
        "fake_rate": num_fake_track / num_proto_track if num_proto_track else 0,
        "duplication_rate": num_duplicate_track / num_proto_track if num_proto_track else 0,
        "purity": num_reco_dupl_track / num_proto_track if num_proto_track else 0,
        "num_recognize_track": num_reco_track,
        "num_real_track": num_real_track,
        "num_duplicate_track": num_duplicate_track,
        "num_proto_track": num_proto_track,
        "num_fake_track": num_fake_track,
        "num_reco_dupl_track": num_reco_dupl_track
    }
    return characteristic_dict


def save_recognised_logo(reco_track_list, real_track_list):
    result_df = pd.DataFrame(columns=["track_id", "is_reco"])
    for i, track_id in enumerate(real_track_list):
        result_df.at[i, "track_id"] = track_id
        result_df.at[i, "is_reco"] = track_id in reco_track_list
    result_df = result_df.sort_values(by=["is_reco"])
    result_df.to_csv("logo.csv", index=False)
