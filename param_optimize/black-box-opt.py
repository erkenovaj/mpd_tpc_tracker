import json
import logging
import warnings
import optuna
from acts_launcher import run

logging.basicConfig(filename='param_history.json',
                    filemode='w', encoding='utf-8',
                    level=logging.INFO,
                    format='%(message)s')
warnings.filterwarnings("ignore", category=optuna.exceptions.ExperimentalWarning)

NUM_TRIALS = 100
search_space = {}

fixed_params = {
    "PtMin": 0.0,
    "CollisionZmin": -30.0,
    "CollisionZmax": 30.0,
    "BeamX": 0.0,
    "BeamY": 0.0,
    "SigmaLoc0": 0.5,
    "SigmaLoc1": 0.5,
    "SigmaPhi": 0.5,
    "SigmaTheta": 0.5,
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
    "PostProcess": True,
    "SelectorEnabled": True,
    "PrimaryParticlesOnly": True,
    "SelectorPhiMin": -3.15,
    "SelectorPhiMax": 3.15,
    "AbsEtaMin": 0,
    "SelectorPtMax": 10.0,
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
    res = run(name)
    return res


def write_log(_, trial):
    '''custom callback'''

    eff = trial.value
    params = {repr(key): val for key, val in trial.params.items()}
    num = trial.number

    logging.info(f'"{num}":\n\t{{"eff": {eff}, \n\t"params": {params}}},')


def objective(trial):
    '''optuna func to optimize'''

    SeedBinSizeR = trial.suggest_int("SeedBinSizeR", 6, 36, step=1)
    SeedDeltaRmin = trial.suggest_int("SeedDeltaRmin", 5, 20, step=1)
    SeedDeltaRmax = trial.suggest_int("SeedDeltaRmax", 30, 120, step=2)
    SeedDeltaZmax = trial.suggest_int("SeedDeltaZmax", 10, 40, step=2)
    SigmaScattering = trial.suggest_int("SigmaScattering", 1, 10, step=1)
    MaxPtScattering = trial.suggest_int("MaxPtScattering", 1, 10, step=1)
    RadLengthPerSeed = trial.suggest_float("RadLengthPerSeed", 0.01, 0.1, step=0.01)
    Chi2max = trial.suggest_int("Chi2max", 15, 60, step=5)
    MaxSeedsPerSpM = trial.suggest_int("MaxSeedsPerSpM", 1, 10, step=1)
    ImpactMax = trial.suggest_int("ImpactMax", 10, 100, step=5)
    PropagationMaxSteps = trial.suggest_int("PropagationMaxSteps", 100, 10000, step=100)
    NmaxPerSurface = trial.suggest_int("NmaxPerSurface", 1, 10, step=1)

    dct_params = {
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

    return opt_func(dct_params)


def main():
    '''main func'''

    study = optuna.create_study(
        direction='maximize',
        sampler=samplers_optuna['tpe']
        )
    study.optimize(objective, n_trials=NUM_TRIALS, callbacks=[write_log])
    best_params = {repr(key): val for key, val in study.best_params.items()}

    logging.info(f'"best":\n\t{{"eff": {study.best_value}, \n\t"params": {best_params}}}')

    with open('best_params.json', 'w', encoding='utf-8') as f:
        json.dump({**study.best_params, **fixed_params}, f, indent=4)


if __name__ == "__main__":
    main()
