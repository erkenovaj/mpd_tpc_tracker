from post_processing.cleaning.direct_cleaning import sort_hits
from collections import defaultdict
import re


def get_tracks_data(track_path, hit_path, track_consist_of_hit_id=False) -> list:
    hit_list = get_hits_data_for_validation(hit_path)
    tracks = []
    track_id = 0
    amount_parameters_in_hit = 0

    with open(track_path) as f:
        for i in f:
            if 'format' in i:
                data_format = re.findall(r'\((.*)\)', i)[0].split(', ')
                amount_parameters_in_hit = len(data_format)
                continue

            if not amount_parameters_in_hit:
                print("Wrong format")
                exit()

            temp = []
            tracks.append([])
            mas = i.split(", ")
            amount_characteristics = 0
            j = 0
            while j < len(mas) or temp:
                if amount_characteristics != amount_parameters_in_hit:
                    temp.append(float(mas[j]))
                    amount_characteristics += 1
                    j += 1
                else:
                    hit_index = int(temp[0])
                    hit_params = hit_list[hit_index][:-1]
                    hit_params.insert(0, hit_index)
                    tracks[track_id].append(hit_index if track_consist_of_hit_id else hit_params)
                    temp = []
                    amount_characteristics = 0
            track_id += 1
    return tracks


def get_hits_data(path_hits, track_id_dict=None) -> dict:
    hits = defaultdict(list)
    with open(path_hits) as f:
        for i in f:
            if 'format' in i:
                continue

            hit = list(map(float, i.split(", ")))
            hits[int(hit[3])].append(hit[:3])

    track_id_list = list(hits.keys())
    for id_track in track_id_list:
        # Удаляем вторичные треки
        if track_id_dict:
            if not track_id_dict[id_track]:
                hits.pop(id_track)
                continue
        hits[id_track] = sort_hits(hits[id_track])
    return hits


def get_hits_data_for_validation(path_hits) -> list:
    hits = []
    with open(path_hits) as f:
        for i in f:
            if 'format' in i:
                continue

            hit = list(map(float, i.split(", ")))
            hits.append(hit)
    return hits


def get_track_id(path) -> dict:
    track_id_dict = {}
    with open(path) as f:
        for i in f:
            if 'format' in i:
                continue

            info = list(map(int, i.split(", ")))
            track_id_dict[info[0]] = info[1]
    return track_id_dict
