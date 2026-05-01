# main.py

from task import Task
from simulation import Simulation

# Define tasks (Autonomous Driving Pipeline) -> Task(name, period, execution_time, deadline)
tasks = [
    Task("Camera", 50, 25, 50),
    Task("Detection", 100, 25, 100),
    Task("Decision", 50, 10, 50),
    Task("Control", 50, 5, 50),
]

# Run RMS
rms_sim = Simulation(tasks, "RMS")
rms_misses, rms_log = rms_sim.run()

# Reset tasks (important!)
tasks = [
    Task("Camera", 50, 10, 50),
    Task("Detection", 100, 25, 100),
    Task("Decision", 50, 10, 50),
    Task("Control", 50, 5, 50),
]

# Run EDF
edf_sim = Simulation(tasks, "EDF")
edf_misses, edf_log = edf_sim.run()

print("RMS Deadline Misses:", rms_misses)
print("EDF Deadline Misses:", edf_misses)
