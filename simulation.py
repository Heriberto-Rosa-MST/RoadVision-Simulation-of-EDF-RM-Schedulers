# simulation.py

from task import Job
from scheduler import rms_scheduler, edf_scheduler


class Simulation:
    def __init__(self, tasks, scheduler_type, sim_time=500):
        self.tasks = tasks
        self.scheduler_type = scheduler_type
        self.sim_time = sim_time

        self.time = 0
        self.ready_queue = []
        self.deadline_misses = 0
        self.log = []

    def release_tasks(self):
        for task in self.tasks:
            if self.time == task.next_release:
                job = Job(task, self.time)
                self.ready_queue.append(job)
                task.next_release += task.period

    def choose_scheduler(self):
        if not self.ready_queue:
            return None

        if self.scheduler_type == "RMS":
            return rms_scheduler(self.ready_queue)
        else:
            return edf_scheduler(self.ready_queue)

    def run(self):
        current_job = None

        while self.time < self.sim_time:

            # Release new jobs
            self.release_tasks()

            # Remove completed jobs
            self.ready_queue = [j for j in self.ready_queue if not j.completed]

            # Pick job
            current_job = self.choose_scheduler()

            if current_job:
                current_job.remaining_time -= 1

                self.log.append(
                    f"Time {self.time}: Running {current_job.task.name}")

                # Check completion
                if current_job.remaining_time == 0:
                    current_job.completed = True

                    # Deadline check
                    if self.time > current_job.absolute_deadline:
                        self.deadline_misses += 1
                        self.log.append(f"MISS: {current_job.task.name}")

            self.time += 1

        return self.deadline_misses, self.log
