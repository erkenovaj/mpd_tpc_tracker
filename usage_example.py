from post_processing import (direct_merging, graph_merging,
                             graph_cleaning, coverage_cleaning,
                             direct_cleaning, create_model,
                             cluster_and_neural_net)
import config
import save_to_files

from analyse.validation import calc_characteristics
from analyse.visualizing import MainWindow
from data_processing.parse_data import *
from PyQt6.QtWidgets import QApplication
from copy import deepcopy
import pandas as pd
import sys
import os

fname = config.fname_real_tracks
if os.path.exists(fname):
    os.remove(fname)
    save_to_files.write_real_tracks_header(fname)

fname = config.fname_track_candidates
if os.path.exists(fname):
    os.remove(fname)
    save_to_files.write_track_candidates_header(fname)

debug = False

# Upload data
# "RAW" -> [[sp-index, sp-x, sp-y, sp-z]+]
result = {"RAW": get_tracks_data("data/tracks_data/event_101_prototracks.txt",
                                 "data/tracks_data/event_101_space_points.txt")}
if (debug):
    tr = result["RAW"]
    for i in tr: print(f"pnb: i:{i}")
    exit()

hit_list = get_hits("data/tracks_data/event_101_space_points.txt")
trackId_to_track_params = get_trackId_to_track_params("data/tracks_data/event_101_mc_track_params.txt")
trackId_to_hits_dict = get_trackId_to_hits_dict("data/tracks_data/event_101_space_points.txt", trackId_to_track_params)

# Upload data and settings for NNS (Can be commented out if you don't use NNS)
model = create_model()
model.load_weights('data/data_for_ml/checkpoint_dir/cp.ckpt')
nn_data = pd.read_csv('data/data_for_ml/track_candidates_params.csv')

df = nn_data[nn_data['#format:eventNumber'] == 101]
df.size
indices = df['prototrackIndex']
event_num = df['#format:eventNumber']
df = df.iloc[:, 2:-2]

# Use methods
result["NNS"] = cluster_and_neural_net(model, deepcopy(result.get("RAW")), df, event_num, indices, hits=3)
result["PWS"] = direct_cleaning(deepcopy(result.get("RAW")))
result["PWM"] = direct_merging(deepcopy(result.get("RAW")))
result["PGS"] = graph_merging(deepcopy(result.get("RAW")))
result["PGM"] = graph_cleaning(deepcopy(result.get("RAW")))
result["HCF"] = coverage_cleaning(deepcopy(result.get("RAW")))

# Computation efficiency
for post_processing_method, result_data in result.items():
    characteristic_dict = calc_characteristics(result_data, hit_list, trackId_to_hits_dict, trackId_to_track_params)

    print(f"\n\n################## {post_processing_method} ##################")
    for characteristic, value in characteristic_dict.items():
        print(f"{characteristic}: {value}")

    # Remove hit indexes for visualizing
    if len(result_data[0][0]) > 3:
        for track_id in range(len(result_data)):
            for hit_id in range(len(result_data[track_id])):
                result_data[track_id][hit_id] = result_data[track_id][hit_id][1:]

# Start visualizing
if __name__ == '__main__':
    if (False):
      app = QApplication(sys.argv)
      plot = MainWindow(list(result.values()), trackId_to_hits_dict)
      plot.show()
      sys.exit(app.exec())
