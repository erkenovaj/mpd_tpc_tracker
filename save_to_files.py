import os

def write_real_tracks_header(fname):
    with open(fname, 'w') as f:
        f.write('# format: trackId, is-primary, nHits, pt, eta, multiplicity, is-reco' + os.linesep)

def write_real_tracks(selected_trackIds, real_tracks_is_reco, fname, trackId_to_track_params):
    multiplicity = len(selected_trackIds)
    with open(fname, 'a') as f:
        for trackId in selected_trackIds:
            params = trackId_to_track_params[trackId]
            pri    = params[0]
            n_hits = params[1]
            pt     = params[2]
            eta    = params[3]

            is_reco = int(trackId in real_tracks_is_reco)
            f.write(f'{trackId},{pri},{n_hits},{pt},{eta},{multiplicity},{is_reco}' + os.linesep)


def write_track_candidates_header(fname):
    with open(fname, 'w') as f:
        f.write("# format: isPrimary, nHits, isFake, isDup, pt, eta, multiplicity, selected, trackId" + os.linesep)


def to_int(val):
  if val is None: 
      return -1
  else: 
      return int(val)


def save_track_candidates(
        selected_trackIds,
        fake_track_list,
        duplicate_track_list,
        trackCandParamsList,
        trackId_to_track_params,
        fname):

    print("save_track_candidates(): len(trackCandParamsList): {}".format(
            len(trackCandParamsList)))
    multiplicity = len(selected_trackIds)
    with open(fname, 'a') as f:
        ipnb = -1
        for params in trackCandParamsList:

#            selected = None
#            if params.selected is None:
#              selected = -1
#            else:
#              selected = (params.selected == True)
#            # skip not selected track-candidate
#            if not params.selected:
#                pass
##               continue
            selected = params.selected

            isDup   = to_int(params.isDup)
            isFake  = to_int(params.isFake)
            trackId = to_int(params.trackId)

            isPri = -1
            nHits = -1
            pt    = -1
            eta   = -123

            if True:
                ipnb += 1
                print("save_track_candidates(): #{ipnb}; "
                      "selected: {selected}; "
                      "isDup: {isDup}; "
                      "isFake: {isFake}; "
                      "trackId: {trackId}; "
                      "isPri: {isPri}; "
                      "nHits: {nHits}; "
                      "pt: {pt}; "
                      "eta: {eta}".format(
                              ipnb=ipnb,
                              selected=params.selected,
                              isDup=params.isDup,
                              isFake=params.isFake,
                              trackId=params.trackId,
                              isPri=isPri,
                              nHits=nHits,
                              pt=pt,
                              eta=eta)
                      )

            if trackId != -1:
                if trackId not in selected_trackIds:
                    continue

                isPri = trackId_to_track_params[trackId][0]
                nHits = trackId_to_track_params[trackId][1]
                pt    = trackId_to_track_params[trackId][2]
                eta   = trackId_to_track_params[trackId][3]
            

            f.write(f"{isPri},{nHits},{isFake},{isDup},{pt},{eta},"
                    f"{multiplicity},{selected},{trackId}" + os.linesep)


