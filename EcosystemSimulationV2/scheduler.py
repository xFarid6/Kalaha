import concurrent.futures
import math

class TaskScheduler:
    def __init__(self, num_threads=8):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)
        self.num_threads = num_threads

    def run_system(self, system_func, store, active_indices, *args):
        """
        Splits active_indices into chunks and runs system_func on them in parallel.
        system_func signature: (store, indices_chunk, *args)
        """
        total = len(active_indices)
        if total == 0: return

        # Calculate chunk size
        chunk_size = math.ceil(total / self.num_threads)
        futures = []

        for i in range(0, total, chunk_size):
            chunk = active_indices[i : i + chunk_size]
            # Submit task
            # We perform the task: system_func(store, chunk, *args)
            f = self.executor.submit(system_func, store, chunk, *args)
            futures.append(f)

        # Wait for all to complete
        concurrent.futures.wait(futures)

    def shutdown(self):
        self.executor.shutdown()
