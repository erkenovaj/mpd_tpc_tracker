from analyse.parallel_collect_stats.data_class import MlModelData
from analyse.parallel_collect_stats.start_parallel_workers import event_pool_analyse

data_for_ml = MlModelData(checkpoint_file_path="data/data_for_ml/checkpoint_dir/cp.ckpt",
                          params_file_path="data/new_format_tracks_data/result.csv")
dirs = ["data/new_format_tracks_data"]

if __name__ == "__main__":
    event_pool_analyse(data_for_ml=data_for_ml,
                       dirs=dirs,
                       start_event=0,
                       end_event=10)
