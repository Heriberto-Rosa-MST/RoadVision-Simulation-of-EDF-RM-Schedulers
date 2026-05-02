# main.py

from task import Task
from simulation import Simulation

# Define tasks (Autonomous Driving Pipeline) -> Task(name, period, execution_time, deadline)
def build_tasks():
    return [
        Task("SensorProc",   period=20,  execution_time=8,  deadline=20,  priority="critical"),
        Task("Perception",   period=50,  execution_time=13, deadline=50,  priority="critical"),
        Task("Localization", period=40,  execution_time=5,  deadline=40,  priority="high"),
        Task("Planning",     period=100, execution_time=6,  deadline=100, priority="high"),
        Task("Control",      period=20,  execution_time=3,  deadline=20,  priority="critical"),
        Task("SysMonitor",   period=200, execution_time=2,  deadline=200, priority="background"),
    ]

SIM_TIME = 500 # ms


# RMS
rms_tasks = build_tasks()
rms_sim = Simulation(rms_tasks, "RMS", sim_time=SIM_TIME)
rms_metrics = rms_sim.run()

# EDF
edf_tasks = build_tasks()
edf_sim = Simulation(edf_tasks, "EDF", sim_time=SIM_TIME)
edf_metrics = edf_sim.run()


def print_report(m):
    print(f"\n{'='*50}")
    print(f"  {m['scheduler']} Results  (sim time = {SIM_TIME} ms)")
    print(f"{'='*50}")
    print(f"  Deadline Misses  : {m['deadline_misses']} / {m['total_jobs']} jobs")
    print(f"  Miss Rate        : {m['miss_rate']*100:.1f}%")
    print(f"  Avg Response Time: {m['avg_response_time']} ms")
    print(f"  CPU Utilization  : {m['cpu_utilization']*100:.1f}%")
    print(f"\n  Per-Task Breakdown:")
    for task, stats in m['per_task'].items():
        rt = f"{stats['avg_response_time']:.1f} ms" if stats['avg_response_time'] else "N/A"
        print(f"    {task:<14} completed={stats['completed']:>3}  "
              f"missed={stats['missed']:>2}  avg_RT={rt}")


print_report(rms_metrics)
print_report(edf_metrics)