import time
import random
import numpy as np
from memory_profiler import memory_usage

from wmm import wmm_calc

def update_lat(model, size):
    """Simulate a computation-heavy process (e.g., matrix multiplication)."""
    
    lats = np.linspace(-90.0, 90.0, num=size)
    lon, alt = 40.55, 55.67

    
    model.setup_env(lats, lon, alt)
    results = model.get_all()

        
        
        
def run_load_lat_test():
    """
    Increase the size for latitude
    """
   
    model = wmm_calc()
    model.setup_time(year=2025, month=12, day=31)
    with open("load_lat_test.txt", "w") as fp:
    
        for size in [100, 500, 1000, 5000, 10000]:  # Increase dataset size
            fp.write(f"\nTesting with dataset size: {size}\n")
            print(f"Testing with dataset size: {size}")
            start_time = time.time()

            mem_usage = memory_usage((update_lat, (model, size)), max_usage=True)  # Monitor memory usage
            # Measure time taken
            end_time = time.time()
            execution_time = end_time - start_time
            
            fp.write(f"Execution time: {execution_time:.2f} seconds\n")
            fp.write(f"Peak memory usage: {mem_usage:.2f} MB\n")
            fp.write("\n")

            print(f"Peak memory usage: {mem_usage:.2f} MB\n")
            print(f"Execution time: {execution_time:.2f} seconds\n")
            

def main():
    
    run_load_lat_test()


if __name__ == "__main__":
    main()

