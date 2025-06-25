class PrintQueueManager:
    def __init__(self, aging_interval=3):
        self.queue = []  # List of job dictionaries
        self.aging_interval = aging_interval  # After how many ticks to apply aging

    def enqueue_job(self, user_id, job_id, priority):
        """
         Adding a job to the queue.
        """
        job = {
            "job_id": job_id,
            "user_id": user_id,
            "priority": priority,
            "waiting_time": 0,
            "aging_counter": 0
        }
        self.queue.append(job)
        print(f"Job {job_id} from user {user_id} enqueued (Priority: {priority})")

    def dequeue_job(self):
        """
        Removes and returns the highest priority job from the queue.
        Returns None if queue is empty.
        """
        if not self.queue:
            print("Queue is empty - nothing to dequeue")
            return None

        # The queue is already sorted by priority and waiting time
        job = self.queue.pop(0)  # Remove first element (highest priority)
        print(f"\nDequeued Job {job['job_id']} (Priority: {job['priority']})")
        return job

    def apply_priority_aging(self):
        """
        Increases job priority based on waiting time and aging interval.
        Reorders the queue afterward.
        """
        for job in self.queue:
            job["waiting_time"] += 1  # Increase waiting time
            job["aging_counter"] += 1  # Track time for aging

            # Apply aging
            if job["aging_counter"] >= self.aging_interval:
                if job["priority"] > 1:  # Assuming 1 is highest possible priority
                    job["priority"] -= 1  # Improve priority
                job["aging_counter"] = 0  # Reset aging counter

        # Re-sort queue: lower priority number = higher priority
        self.queue.sort(key=lambda x: (x["priority"], -x["waiting_time"]))

    def tick(self):
        """
        Simulates one unit of time.
        Triggers aging logic (module 5 calls this).
        """
        print("\nTick event triggered.")
        self.apply_priority_aging()

    def show_status(self):
        """
        Displays current queue state.
        """
        print("\nQueue:")
        for job in self.queue:
            print(f"Job {job['job_id']} | User: {job['user_id']} | "
                  f"Priority: {job['priority']} | Wait: {job['waiting_time']}")

if __name__ == "__main__":
    pq = PrintQueueManager(aging_interval=2)  # Aging every 2 ticks

    # Enqueue jobs with different priorities
    pq.enqueue_job("Alice", "job1", 3)
    pq.enqueue_job("Joy", "job2", 3)
    pq.enqueue_job("Bob", "job3", 2)
    pq.enqueue_job("Joan", "job4", 1)
    pq.enqueue_job("Tracey", "job5", 5)
    pq.enqueue_job("Bob", "job6", 4)
    pq.show_status()

    # Simulate passage of time
    for _ in range(3):
        pq.tick()

        pq.dequeue_job()
    pq.show_status()

    for _ in range(1):
        pq.tick()
        pq.enqueue_job("Kelvin", "job7", 3)
        pq.enqueue_job("Leon", "job8", 4)
    pq.show_status()



    # Final dequeue
    pq.dequeue_job()
    pq.show_status()