import concurrent.futures

from tqdm import tqdm

from analyse.parallel_collect_stats.data_class import MlModelData, OneEventRealTrackParams
from analyse.parallel_collect_stats.func_file import calculate_one_event_stats


def event_pool_analyse(data_for_ml: MlModelData, dirs: list[str], start_event: int, end_event: int) -> None:
    # Can be changed to concurrent.futures.ProcessPoolExecutor to use dif process cores
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Create work pool
        future_pool = (executor.submit(calculate_one_event_stats,
                                       event_number,
                                       dirs,
                                       data_for_ml) for event_number in range(start_event, end_event))
        bar_format = "\n\n{n}: events analyzed\n\n"
        pool_size = end_event - start_event
        for future in tqdm(concurrent.futures.as_completed(future_pool), total=pool_size, bar_format=bar_format):
            try:
                event_characteristics: OneEventRealTrackParams = future.result()
                event_characteristics.save_characteristics()
            except Exception as exc:
                print(exc)
            finally:
                pass
