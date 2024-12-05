import time
import random
import numpy as np
from memory_profiler import memory_usage

from build import wmm_calc

def update_lat(model, size):
    """Simulate a computation-heavy process (e.g., matrix multiplication)."""
    
    lats = np.linspace(-90.0, 90.0, num=size)
    lon, alt = 40.55, 55.67
    lon = np.zeros(len(lats))*lon
    alt = np.zeros(len(lats))*alt

    # for i in range(size):
    
         
    #     model.setup_env(lats[i], lon, alt)
    #     results = model.get_all()  
        
    model.setup_env(lats, lon, alt)
    results = model.get_all()  
        
def run_load_lat_test():
    """
    Increase the size for latitude
    """
   
    model = wmm_calc()
    model.setup_time(year=2025, month=12, day=31)
    with open("load_lat_test.txt", "w") as fp:
    
        for size in [100, 500, 1000, 5000, 10000, 50000, 100000]:  # Increase dataset size
            fp.write(f"\nTesting with dataset size: {size}\n")
            start_time = time.time()

            mem_usage = memory_usage((update_lat, (model, size)), max_usage=True)  # Monitor memory usage
            # Measure time taken
            end_time = time.time()
            execution_time = end_time - start_time
            
            fp.write(f"Execution time: {execution_time:.2f} seconds\n")
            fp.write(f"Peak memory usage: {mem_usage:.2f} MB\n")
            fp.write("\n")

            print(f"Execution time for {size} datapoints: {execution_time:.2f} seconds\n")
            

def main():
    
    run_load_lat_test()


if __name__ == "__main__":
    main()
