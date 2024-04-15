import config

def select(
    trackId,
    trackId_to_track_params):

  if trackId not in trackId_to_track_params:
    raise("select(): trackId not in trackId_to_track_params")
  params = trackId_to_track_params[trackId]
  pri    = params[0]
  n_hits = params[1]
  pt     = params[2]
  eta    = params[3]
  if config.only_primary and (not pri):
    return False
  if (pt < config.pt_min) or (pt > config.pt_max):
    return False
  if (eta < config.eta_min) or (eta > config.eta_max):
    return False
  if n_hits < config.n_real_hits_min:
    return False
  return True
