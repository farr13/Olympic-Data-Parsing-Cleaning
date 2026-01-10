from project import main
import time
start_time = time.perf_counter()
main()
end_time = time.perf_counter()
total_time = (end_time-start_time)
print(f"EXECUTION_TIME: {total_time:.3f}")
