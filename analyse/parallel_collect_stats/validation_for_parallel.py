import config
from analyse.parallel_collect_stats.data_class import RealTrackParams, CandTrackParams
from analyse.validation import get_selected_trackIds, get_characteristics


def calc_parallel_characteristics(track_candidates,
                                  hit_list,
                                  trackId_to_track_params,
                                  min_length_proto=6,
                                  ratio=0.5,
                                  method=''):
    selected_trackIds = get_selected_trackIds(trackId_to_track_params)

    # Get all lists of necessary data
    (reco_track_list, fake_track_list,
     duplicate_track_list, trackCandParamsList) = get_characteristics(selected_trackIds,
                                                                      track_candidates,
                                                                      hit_list,
                                                                      min_length_proto,
                                                                      ratio)

    # Remove short real track from recognized data
    reco_track_list = list(filter(lambda x: x in selected_trackIds, reco_track_list))
    fake_track_list = list(filter(lambda x: x in selected_trackIds, fake_track_list))
    duplicate_track_list = list(filter(lambda x: x in selected_trackIds, duplicate_track_list))

    real_track_params = RealTrackParams(selected_trackIds=selected_trackIds,
                                        reco_track_list=reco_track_list,
                                        method=config.fname_real_tracks.format(method),
                                        trackId_to_track_params=trackId_to_track_params)

    cand_track_params = CandTrackParams(selected_trackIds=selected_trackIds,
                                        fake_track_list=fake_track_list,
                                        duplicate_track_list=duplicate_track_list,
                                        trackCandParamsList=trackCandParamsList,
                                        trackId_to_track_params=trackId_to_track_params,
                                        method=config.fname_track_candidates.format(method))

    return [real_track_params, cand_track_params]
