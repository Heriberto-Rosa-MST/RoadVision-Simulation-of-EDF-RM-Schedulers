# scheduler.py

def rms_scheduler(ready_queue):
    # shorter period = higher priority
    return min(ready_queue, key=lambda job: job.task.period)


def edf_scheduler(ready_queue):
    # earliest deadline first
    return min(ready_queue, key=lambda job: job.absolute_deadline)
