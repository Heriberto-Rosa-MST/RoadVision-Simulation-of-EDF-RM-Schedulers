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

        # metrics
        self.deadline_misses = 0
        self.missed_jobs = []
        self.completed_jobs = []
        self.busy_ticks = 0

        self.log = []

    # simulation loop

    def release_tasks(self):
        for task in self.tasks:
            if self.time == task.next_release:
                job = Job(task, self.time)
                self.ready_queue.append(job)
                task.next_release += task.period

    def _choose_job(self):
        if not self.ready_queue:
            return None
        if self.scheduler_type == "RMS":
            return rms_scheduler(self.ready_queue)
        else:
            return edf_scheduler(self.ready_queue)

    def run(self):
        while self.time < self.sim_time:

            # Release new jobs
            self.release_tasks()

            # Remove completed jobs
            self.ready_queue = [j for j in self.ready_queue if not j.completed]

            # Pick job
            current_job = self._choose_job()

            if current_job:
                current_job.remaining_time -= 1
                self.busy_ticks += 1

                self.log.append({
                    "time": self.time,
                    "task": current_job.task.name,
                    "priority": current_job.task.priority,
                    "event": "run",
                    "deadline": current_job.absolute_deadline,
                })

                # Check completion
                if current_job.remaining_time == 0:
                    current_job.completed = True
                    current_job.completion_time = self.time + 1

                    # Deadline check
                    if current_job.completion_time > current_job.absolute_deadline:
                        self.deadline_misses += 1
                        self.missed_jobs.append(current_job)
                        self.log.append({
                            "time": self.time,
                            "task": current_job.task.name,
                            "priority": current_job.task.priority,
                            "event": "miss",
                            "deadline": current_job.absolute_deadline,
                        })
                    else:
                        self.completed_jobs.append(current_job)
                        self.log.append({
                            "time": self.time,
                            "task": current_job.task.name,
                            "priority": current_job.task.priority,
                            "event": "complete",
                            "deadline": current_job.absolute_deadline,
                        })
            else:
                self.log.append({
                    "time": self.time,
                    "task": "IDLE",
                    "priority": None,
                    "event": "idle",
                    "deadline": None,
                })

            self.time += 1

        return self.get_metrics()


    def get_metrics(self):
        total_jobs = len(self.completed_jobs) + len(self.missed_jobs)

        # Average response time across completed jobs only
        if self.completed_jobs:
            avg_response = sum(j.response_time for j in self.completed_jobs) / len(self.completed_jobs)
        else:
            avg_response = float("inf")

        # Per-task breakdown
        task_names = [t.name for t in self.tasks]
        per_task = {}
        for name in task_names:
            completed = [j for j in self.completed_jobs if j.task.name == name]
            missed = [j for j in self.missed_jobs if j.task.name == name]
            rt = sum(j.response_time for j in completed) / len(completed) if completed else None
            per_task[name] = {
                "completed": len(completed),
                "missed": len(missed),
                "avg_response_time": rt,
            }

        return {
            "scheduler": self.scheduler_type,
            "deadline_misses": self.deadline_misses,
            "total_jobs": total_jobs,
            "miss_rate": self.deadline_misses / total_jobs if total_jobs > 0 else 0,
            "avg_response_time": round(avg_response, 2),
            "cpu_utilization": round(self.busy_ticks / self.sim_time, 4),
            "per_task": per_task,
            "log": self.log,
        }