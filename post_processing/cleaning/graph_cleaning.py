from post_processing.cleaning.direct_cleaning import separate_tracks, sort_hits_old
from collections import defaultdict
from time import time


def count_tracks_intersections(all_tracks: dict):
    intersections = defaultdict(list)
    intersections_count = defaultdict(int)
    tracks_graph = defaultdict(list)
    for new_track_id, track in all_tracks.items():
        for point_id in track:
            for track_id in intersections.get(point_id, []):
                track_pair = (track_id, new_track_id) if track_id < new_track_id else (new_track_id, track_id)
                tracks_graph[track_pair[0]].append(track_pair[1])
                tracks_graph[track_pair[1]].append(track_pair[0])
                intersections_count[track_pair] += 1
            intersections[point_id].append(new_track_id)
    return intersections_count, tracks_graph


def divide_tracks_graph(intersections_count: dict, tracks_graph: dict, all_tracks: dict):
    graph_to_separate = {}
    graph_to_unite = {}
    for vertex, edges in tracks_graph.items():
        unite_edges = list()
        separate_edges = list()
        for edge in set(edges):
            track_pair = (edge, vertex) if edge < vertex else (vertex, edge)
            num_shared_points = intersections_count[track_pair]
            min_len = min(len(all_tracks[track_pair[0]]), len(all_tracks[track_pair[1]]))
            unite_edges.append(edge) if num_shared_points / min_len > 0.5 else separate_edges.append(edge)
        if len(unite_edges) != 0:
            graph_to_unite[vertex] = set(unite_edges)

        if len(separate_edges) != 0:
            graph_to_separate[vertex] = set(separate_edges)
    return graph_to_unite, graph_to_separate


def dfs(graph: dict, start: int, all_visited: set, visited):
    if visited is None:
        visited = set()

    visited.add(start)
    all_visited.add(start)
    for next_vertex in graph[start]:
        if next_vertex not in all_visited:
            dfs(graph, next_vertex, all_visited, visited)


def get_connected_components(graph: dict):
    all_visited = set()
    connected_components = []
    for vertex in graph.keys():
        if vertex not in all_visited:
            visited = set()
            dfs(graph, vertex, all_visited, visited)
            connected_components.append(visited)
    return connected_components


def process_tracks(tracks: list):
    first_start = time()

    hits = {}
    for i in range(len(tracks)):
        for j in range(len(tracks[i])):
            s = tracks[i][j][0]
            hits[s] = tracks[i][j]
            tracks[i][j] = s

    tracks_dict = {i: tracks[i] for i in range(len(tracks))}
    intersections_count, tracks_graph = count_tracks_intersections(tracks_dict)

    graph_to_unite, graph_to_separate = divide_tracks_graph(intersections_count, tracks_graph, tracks_dict)
    tracks_to_unite = get_connected_components(graph_to_unite)
    end = time()
    print("All process_tracks time:")
    print(end - first_start)
    return tracks_dict, tracks_to_unite, graph_to_separate, hits


def tracks_separation(tracks_dict, graph_to_separate):
    for graph in graph_to_separate:
        if type(graph) != int:
            for i in range(1, len(graph)):
                separate_tracks(tracks_dict[i - 1], tracks_dict[i])
    return tracks_dict


def unite_tracks(tracks_dict, tracks_to_unite):
    tracks = []
    for i in range(len(tracks_to_unite)):
        track = []
        for j in tracks_to_unite[i]:
            track.extend(tracks_dict[j])
        tracks.append(list(set(track)))
    return tracks


def choose_longer(tracks_dict, tracks_to_unite):
    tracks = []
    for i in tracks_to_unite:
        i = sorted(i, key=lambda x: len(tracks_dict[x]))
        tracks.append(tracks_dict[i[-1]])
    return tracks


# Return to x,y,z and sorting
def decode(tracks, hits):
    for i in range(len(tracks)):
        for j in range(len(tracks[i])):
            tracks[i][j] = hits[tracks[i][j]]
        tracks[i] = sort_hits_old(tracks[i])
    return tracks


def graph_cleaning(tracks):
    tracks_dict, tracks_to_unite, graph_to_separate, hits = process_tracks(tracks)

    longer_tracks = choose_longer(tracks_dict, tracks_to_unite)
    longer_tracks = tracks_separation(longer_tracks, graph_to_separate)
    longer_tracks = decode(longer_tracks, hits)

    print('Number of tracks after cleaning: ', len(tracks_to_unite))

    return longer_tracks


def graph_merging(tracks):
    tracks_dict, tracks_to_unite, graph_to_separate, hits = process_tracks(tracks)

    merged_tracks = unite_tracks(tracks_dict, tracks_to_unite)
    merged_tracks = tracks_separation(merged_tracks, graph_to_separate)
    merged_tracks = decode(merged_tracks, hits)

    print('Number of tracks after cleaning: ', len(tracks_to_unite))

    return merged_tracks
