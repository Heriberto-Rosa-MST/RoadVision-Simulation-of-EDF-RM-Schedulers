# task.py

class Task:
    def __init__(self, name, period, execution_time, deadline, priority="high"):
        self.name = name
        self.period = period
        self.execution_time = execution_time
        self.deadline = deadline
        self.priority = priority
        self.next_release = 0


class Job:
    def __init__(self, task, release_time):
        self.task = task
        self.release_time = release_time
        self.remaining_time = task.execution_time
        self.absolute_deadline = release_time + task.deadline
        self.completed = False
        self.completion_time = None


    @property
    def response_time(self):
        if self.completion_time is not None:
            return self.completion_time - self.release_time
        return None
