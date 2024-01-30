from post_processing import (direct_merging, graph_merging,
                             graph_cleaning, coverage_cleaning,
                             direct_cleaning, create_model,
                             cluster_and_neural_net)
from analyse.validation import calc_characteristics
from analyse.visualizing import MainWindow
from data_processing.parse_data import *
from PyQt6.QtWidgets import QApplication
from copy import deepcopy
import pandas as pd
import sys

# Upload data
result = {"RAW": get_tracks_data("data/tracks_data/event_501_prototracks.txt",
                                 "data/tracks_data/event_501_space_points.txt")}
hit_list = get_hits_data_for_validation("data/tracks_data/event_501_space_points.txt")
track_id_dict = get_track_id("data/tracks_data/event_501_trackIds.txt")
track_dict = get_hits_data("data/tracks_data/event_501_space_points.txt", track_id_dict)

# Upload data and settings for NNS (Can be commented out if you don't use NNS)
model = create_model()
model.load_weights('data/data_for_ml/checkpoint_dir/cp.ckpt')
nn_data = pd.read_csv('data/data_for_ml/track_candidates_params.csv')

df = nn_data[nn_data['#format:eventNumber'] == 501]
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
    characteristic_dict = calc_characteristics(result_data, hit_list, track_dict, track_id_dict)

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
    app = QApplication(sys.argv)
    plot = MainWindow(list(result.values()), track_dict)
    plot.show()
    sys.exit(app.exec())
