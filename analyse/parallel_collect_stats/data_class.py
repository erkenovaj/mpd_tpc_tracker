from copy import deepcopy
from dataclasses import dataclass, field
from tf_keras import Sequential
from pandas import Series, DataFrame
import pandas as pd

import save_to_files
from post_processing.cleaning.neural_net import create_model


@dataclass
class MlModelData:
    params_file_path: str
    checkpoint_file_path: str

    indices: Series = field(init=False)
    event_num_ser: Series = field(init=False)
    event_df: DataFrame = field(init=False)

    def calc_event_filed(self, event_num: int):
        self.event_df = self.base_df[self.base_df['#format:eventNumber'] == event_num]
        self.indices = self.event_df['prototrackIndex']
        self.event_num_ser = self.event_df['#format:eventNumber']
        self.event_df = self.event_df.iloc[:, 2:-2]

    def __post_init__(self):
        self.model: Sequential = self.__load_model__()
        self.base_df: DataFrame = pd.read_csv(self.params_file_path)

    def __load_model__(self):
        model = create_model()
        checkpoint_path = self.checkpoint_file_path
        model.load_weights(checkpoint_path)
        return model


@dataclass
class BaseTrackParams:
    selected_trackIds: list
    method: str
    trackId_to_track_params: list


@dataclass
class RealTrackParams(BaseTrackParams):
    reco_track_list: list


@dataclass
class CandTrackParams(BaseTrackParams):
    fake_track_list: list
    duplicate_track_list: list
    trackCandParamsList: list


@dataclass
class OneEventRealTrackParams:
    all_method_for_real_tracks: list[RealTrackParams] = field(default_factory=list)
    all_method_for_cand_tracks: list[CandTrackParams] = field(default_factory=list)

    def save_characteristics(self):
        # Save real track characteristics
        for real_track_characteristics in self.all_method_for_real_tracks:
            save_to_files.write_real_tracks(
                selected_trackIds=real_track_characteristics.selected_trackIds,
                real_tracks_is_reco=real_track_characteristics.reco_track_list,
                fname=real_track_characteristics.method,
                trackId_to_track_params=real_track_characteristics.trackId_to_track_params
            )
        # Save cand track characteristics
        for cand_track_characteristics in self.all_method_for_cand_tracks:
            save_to_files.save_track_candidates(
                selected_trackIds=cand_track_characteristics.selected_trackIds,
                fake_track_list=cand_track_characteristics.fake_track_list,
                duplicate_track_list=cand_track_characteristics.duplicate_track_list,
                trackCandParamsList=cand_track_characteristics.trackCandParamsList,
                trackId_to_track_params=cand_track_characteristics.trackId_to_track_params,
                fname=cand_track_characteristics.method
            )


@dataclass
class HitData:
    tracks: list[float]


@dataclass
class TrackData:
    tracks: list[HitData]


@dataclass
class InputEventData:
    hits_list: list[HitData]
    track_id_to_track_params: dict[int, list[float]]
    _tracks: list[TrackData] = field(default_factory=list, repr=False)

    @property
    def tracks(self) -> list[TrackData]:
        return deepcopy(self._tracks)

    @tracks.setter
    def tracks(self, value: list[TrackData]):
        self._tracks = value
