import os
import json
import logging
import warnings
import datetime
import optuna
from acts_launcher import run

warnings.filterwarnings("ignore", category=optuna.exceptions.ExperimentalWarning)

NUM_TRIALS = None
LOG_DIR = 'log_params'

search_space = {}

fixed_params = {
    "CollisionZmin": -300.0,
    "CollisionZmax": 300.0,
    "SigmaLoc0": 0.5,
    "SigmaLoc1": 0.5,
    "SigmaPhi": 0.00872665,
    "SigmaTheta": 0.00872665,
    "SigmaQOverP": 0.1,
    "SigmaT0": 2000.0,
    "InitVarInflatLoc0": 1.0,
    "InitVarInflatLoc1": 1.0,
    "InitVarInflatPhi": 1.0,
    "InitVarInflatTheta": 1.0,
    "InitVarInflatQOverP": 1.0,
    "InitVarInflatT0": 1.0,
    "ResolvePassive": False,
    "ResolveMaterial": True,
    "ResolveSensitive": True,
    "MultipleScattering": True,
    "EnergyLoss": True,
    "Smoothing": True,
    "ComputeSharedHits": False,
    "TrackMinLength": 4,
    "NewHitsInRow": 6,
    "NewHitsRatio": 0.25,
    "PostProcess": False,
    "SelectorEnabled": True,
    "PrimaryParticlesOnly": True,
    "SelectorPhiMin": -3.15,
    "SelectorPhiMax": 3.15,
    "AbsEtaMin": 0,
    "KeepNeutral": False,
    "NHitsMin": 9,
    "TruthMatchProbMin": 0.5,
    "MeasurementsMin": 6,
    "EtaNBins": 40,
    "PhiNBins": 100,
    "PtNBins": 40,
    "PerfPlotToolPtMin": 0.0,
    "PerfPlotToolPtMax": 2.5,
    "NumNBins": 30,
    "NumMin": -0.5,
    "NumMax": 29.5,
    "OnlyCertainTracks": False,
    "DumpData": False,
    "WriteTrajSummary": False
    }

samplers_optuna = {
    'grid': optuna.samplers.GridSampler(search_space),
    'random': optuna.samplers.RandomSampler(seed=0),
    'tpe': optuna.samplers.TPESampler(),
    'cmaes': optuna.samplers.CmaEsSampler(),
    'nsgaii': optuna.samplers.NSGAIISampler(),
    'qmc': optuna.samplers.QMCSampler(),
    'gp': optuna.samplers.GPSampler(seed=0),
    'bayes': optuna.integration.BoTorchSampler()
    }


def to_json(dct_vals: dict):
    '''dump to json'''

    name_json = 'acts_params_config.json'
    with open(name_json, 'w', encoding='utf-8') as f:
        json.dump(dct_vals, f, indent=4)
    return name_json


def opt_func(dct_params: dict):
    '''func to optimize (black-box)'''

    dct_vals = {**dct_params, **fixed_params}
    name = to_json(dct_vals)
    eff_sel, eff_all, fake_sel, fake_all, memory = run(name)
    return eff_sel, eff_all, fake_sel, fake_all, memory


def write_log(_, trial):
    '''custom callback'''

    eff_sel, eff_all, fake_sel, fake_all, memory = trial.values

    params = {repr(key): val for key, val in trial.params.items()}
    num = trial.number

    duration_sec = trial.duration.total_seconds()
    minutes = round((duration_sec % 3600) / 60, 3)

    dr = f'\n\t"duration(min)": {minutes},'
    me = f'\n\t"memory": {memory},'
    es = f'\n\t"eff_sel": {eff_sel},'
    ea = f'\n\t"eff_all": {eff_all},'
    fs = f'\n\t"fake_sel": {fake_sel},'
    fa = f'\n\t"fake_all": {fake_all},'
    pm = f'\n\t"params": {params}'

    msg = f'"{num}": {{{dr}{me}{es}{ea}{fs}{fa}{pm}}},'

    logging.info(msg)


def objective(trial):
    '''optuna func to optimize'''

    SeedBinSizeR = trial.suggest_int("SeedBinSizeR", 6, 36, step=1)
    SeedDeltaRmin = trial.suggest_int("SeedDeltaRmin", 5, 20, step=1)
    SeedDeltaRmax = trial.suggest_int("SeedDeltaRmax", 30, 120, step=2)
    SeedDeltaZmax = trial.suggest_int("SeedDeltaZmax", 100, 400, step=2)
    SigmaScattering = trial.suggest_int("SigmaScattering", 1, 10, step=1)
    MaxPtScattering = trial.suggest_int("MaxPtScattering", 1, 10, step=1)
    RadLengthPerSeed = trial.suggest_float("RadLengthPerSeed", 0.01, 0.1, step=0.01)
    Chi2max = trial.suggest_int("Chi2max", 15, 60, step=5)
    MaxSeedsPerSpM = trial.suggest_int("MaxSeedsPerSpM", 1, 10, step=1)
    ImpactMax = trial.suggest_int("ImpactMax", 10, 100, step=5)
    PropagationMaxSteps = trial.suggest_int("PropagationMaxSteps", 100, 1000, step=100)
    NmaxPerSurface = trial.suggest_int("NmaxPerSurface", 1, 10, step=1)
    SelectorPtMax = trial.suggest_int("SelectorPtMax", 2, 10, step=1)
    EtaMax = trial.suggest_float("EtaMax", 1.8, 2.2, step=0.04)
    PtMin = trial.suggest_float("PtMin", 0.04, 0.1, step=0.002)
    BeamX = trial.suggest_int("BeamX", 0, 10, step=1)
    BeamY = trial.suggest_int("BeamY", 0, 10, step=1)

    dct_params = {
        "SelectorPtMax": SelectorPtMax,
        "EtaMax": EtaMax,
        "PtMin": PtMin,
        "BeamX": BeamX,
        "BeamY": BeamY,
        "SeedBinSizeR": SeedBinSizeR,
        "SeedDeltaRmin": SeedDeltaRmin,
        "SeedDeltaRmax": SeedDeltaRmax,
        "SeedDeltaZmax": SeedDeltaZmax,
        "SigmaScattering": SigmaScattering,
        "MaxPtScattering": MaxPtScattering,
        "RadLengthPerSeed": RadLengthPerSeed,
        "Chi2max": Chi2max,
        "MaxSeedsPerSpM": MaxSeedsPerSpM,
        "ImpactMax": ImpactMax,
        "PropagationMaxSteps": PropagationMaxSteps,
        "NmaxPerSurface": NmaxPerSurface
        }
    
    eff_sel, eff_all, fake_sel, fake_all, memory = opt_func(dct_params)

    return eff_sel, eff_all, fake_sel, fake_all, memory


def main():
    '''main func'''

    if not os.path.isdir(LOG_DIR):
        new_dirpath = os.path.join(os.getcwd(), LOG_DIR)
        os.mkdir(new_dirpath)

    curr_time = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(curr_time, "%Y-%d-%m-%H-%M-%S")
    logging.basicConfig(filename=f'{LOG_DIR}/param_history_{timestamp}.json',
                        filemode='w', encoding='utf-8',
                        level=logging.INFO,
                        format='%(message)s'
                        )

    study = optuna.create_study(
        directions=["maximize", "maximize", "minimize", "minimize", "minimize"],
        sampler=samplers_optuna['random']
        )
    study.optimize(objective, n_trials=NUM_TRIALS, callbacks=[write_log], n_jobs=1)
    best_trial = max(study.best_trials, key=lambda t: t.values[0])
    best_params = best_trial.params

    with open('best_params.json', 'w', encoding='utf-8') as f:
        json.dump({**best_params, **fixed_params}, f, indent=4)


if __name__ == "__main__":
    main()
