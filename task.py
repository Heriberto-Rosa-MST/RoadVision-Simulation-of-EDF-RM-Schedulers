# task.py

class Task:
    def __init__(self, name, period, execution_time, deadline):
        self.name = name
        self.period = period
        self.execution_time = execution_time
        self.deadline = deadline
        self.next_release = 0


class Job:
    def __init__(self, task, release_time):
        self.task = task
        self.release_time = release_time
        self.remaining_time = task.execution_time
        self.absolute_deadline = release_time + task.deadline
        self.completed = False
