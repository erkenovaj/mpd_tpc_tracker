import json
import logging
import optuna

logging.basicConfig(filename='example.log',
                    filemode='w', encoding='utf-8',
                    level=logging.INFO,
                    format='%(levelname)s:%(message)s')

search_space = {}

fixed_params = {
    "SeedZmin": None,
    "SeedZmax": None,
    "CotThetaMax": None,
    "Bz": 0.5,
    "Bmin": 0.5,
    "Rmin": 40.0,
    "Rmax": 125.5,
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
    "ComputeSharedHits": False
    }

samplers_optuna = {
    'grid': optuna.samplers.GridSampler(search_space),
    'random': optuna.samplers.RandomSampler(),
    'tpe': optuna.samplers.TPESampler(),
    'bayes': optuna.integration.BoTorchSampler(),
    'cmaes': optuna.samplers.CmaEsSampler(),
    'nsgaii': optuna.samplers.NSGAIISampler(),
    'qmc': optuna.samplers.QMCSampler()
    }


def to_json(dct_vals: dict):
    '''dump to json'''

    name_json = 'params.json'
    with open(name_json, 'w', encoding='utf-8') as f:
        json.dump(dct_vals, f, indent=4)
    return name_json


def get_res(json_file: str):
    '''stub-func'''

    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    return data['SeedBinSizeR'] + data['MaxSeedsPerSpM'] - data['NmaxPerSurface'] + data['ImpactMax'] - data['PropagationMaxSteps']


def opt_func(SeedBinSizeR, MaxSeedsPerSpM, ImpactMax, PropagationMaxSteps, NmaxPerSurface):
    '''func to optimize (black-box)'''

    dct_vals = {
        "SeedBinSizeR": SeedBinSizeR,
        "MaxSeedsPerSpM": MaxSeedsPerSpM,
        "ImpactMax": ImpactMax,
        "PropagationMaxSteps": PropagationMaxSteps,
        "NmaxPerSurface": NmaxPerSurface
        }
    dct_vals = {**dct_vals, **fixed_params}
    name = to_json(dct_vals)
    res = get_res(name)
    return -res


def write_log(_, trial):
    '''custom callback'''

    logging.info(f'Efficiency: {trial.value}, params: {trial.params}')


def objective(trial):
    '''optuna func to optimize'''

    SeedBinSizeR = trial.suggest_int("SeedBinSizeR", 6, 36, 1)
    MaxSeedsPerSpM = trial.suggest_int("MaxSeedsPerSpM", 1, 10, 1)
    ImpactMax = trial.suggest_int("ImpactMax", 10, 100)
    PropagationMaxSteps = trial.suggest_int("PropagationMaxSteps", 100, 10000, 100)
    NmaxPerSurface = trial.suggest_int("NmaxPerSurface", 1, 10)

    return opt_func(SeedBinSizeR, MaxSeedsPerSpM, ImpactMax, PropagationMaxSteps, NmaxPerSurface)


def main():
    '''main func'''

    study = optuna.create_study(
        sampler=optuna.integration.BoTorchSampler())
    study.optimize(objective, n_trials=100, callbacks=[write_log])
    logging.info(f'BEST EFFICIENCY: {study.best_value}, '
                 f'BEST PARAMS: {study.best_params}')
    with open('best_params.json', 'w', encoding='utf-8') as f:
        json.dump({**study.best_params, **fixed_params}, f, indent=4)


if __name__ == "__main__":
    main()
