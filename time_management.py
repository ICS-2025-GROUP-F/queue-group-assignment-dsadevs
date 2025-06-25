import time
import threading
from typing import Dict, List, Optional


class Job:
    """Represents a print job with metadata"""

    def __init__(self, user_id: str, job_id: str, priority: int):
        self.user_id = user_id
        self.job_id = job_id
        self.priority = priority
        self.submission_time = time.time()
        self.waiting_time = 0

    def __str__(self):
        return f"Job({self.job_id}, User: {self.user_id}, Priority: {self.priority}, Wait: {self.waiting_time}s)"


class PrintQueueManager:
    """
    Module 5: Event Simulation & Time Management
    Handles time progression and coordinates system updates
    """

    def __init__(self, max_capacity: int = 10, aging_interval: int = 5, expiry_time: int = 30):
        # Basic queue setup (from Module 1)
        self.max_capacity = max_capacity
        self.queue = [None] * max_capacity
        self.front = 0
        self.rear = -1
        self.size = 0
        self.lock = threading.Lock()
        self.active_jobs: Dict[str, Job] = {}

        # Module 5 specific: Time Management Configuration
        self.aging_interval = aging_interval  # How often to age priorities (seconds)
        self.expiry_time = expiry_time  # When jobs expire (seconds)
        self.system_time = 0  # Internal system time counter
        self.last_aging_time = 0  # Last time priority aging was applied
        self.tick_count = 0  # Number of ticks that have occurred

        # Event tracking
        self.events_log = []  # Log of all events for debugging

        print(f"Time Management System initialized:")
        print(f"  - Aging interval: {aging_interval} seconds")
        print(f"  - Job expiry time: {expiry_time} seconds")

    def tick(self):
        """
        Module 5 Main Function: Simulate time passing
        Updates waiting times, applies aging and expiry logic
        """
        with self.lock:
            # Increment system time
            self.system_time += 1
            self.tick_count += 1

            print(f"\n--- TICK {self.tick_count} (System Time: {self.system_time}s) ---")

            # Update waiting times for all jobs
            self._update_waiting_times()

            # Apply priority aging if interval has passed
            if self._should_apply_aging():
                self._apply_priority_aging()
                self.last_aging_time = self.system_time

            # Remove expired jobs
            self._remove_expired_jobs()

            # Log this tick event
            self._log_event("tick", {
                "system_time": self.system_time,
                "active_jobs": len(self.active_jobs),
                "queue_size": self.size
            })

            print(f"Tick complete - Active jobs: {len(self.active_jobs)}, Queue size: {self.size}")

    def _update_waiting_times(self):
        """Update waiting time for all jobs in the system"""
        updated_count = 0

        for job in self.active_jobs.values():
            # Calculate waiting time based on current system time and submission
            old_waiting_time = job.waiting_time
            job.waiting_time = self.system_time - (job.submission_time - self.system_time + self.tick_count - 1)

            # Ensure waiting time is non-negative and reasonable
            if job.waiting_time < 0:
                job.waiting_time = self.tick_count

            updated_count += 1

        if updated_count > 0:
            print(f"Updated waiting times for {updated_count} jobs")

    def _should_apply_aging(self) -> bool:
        """Check if enough time has passed to apply priority aging"""
        return (self.system_time - self.last_aging_time) >= self.aging_interval

    def _apply_priority_aging(self):
        """Increase priority for jobs that have been waiting (Module 2 integration)"""
        aged_jobs = 0

        for job in self.active_jobs.values():
            if job.waiting_time >= self.aging_interval:
                old_priority = job.priority
                job.priority += 1  # Increase priority by 1
                aged_jobs += 1
                print(f"  Aged job {job.job_id}: priority {old_priority} → {job.priority}")

        if aged_jobs > 0:
            print(f"Applied priority aging to {aged_jobs} jobs")
            # After aging, re-sort the queue by priority (integrate with Module 2)
            self._resort_queue_by_priority()
        else:
            print("No jobs eligible for priority aging")

    def _remove_expired_jobs(self):
        """Remove jobs that have exceeded expiry time (Module 3 integration)"""
        expired_jobs = []

        # Find expired jobs
        for job in self.active_jobs.values():
            if job.waiting_time >= self.expiry_time:
                expired_jobs.append(job)

        # Remove expired jobs
        for job in expired_jobs:
            self._remove_job_from_queue(job)
            print(f"  EXPIRED: Job {job.job_id} (waited {job.waiting_time}s)")

        if expired_jobs:
            print(f"Removed {len(expired_jobs)} expired jobs")

    def _resort_queue_by_priority(self):
        """Re-sort queue after priority changes (integration with Module 2)"""
        if self.size <= 1:
            return

        # Get all jobs in order
        jobs = []
        current = self.front
        for _ in range(self.size):
            if self.queue[current] is not None:
                jobs.append(self.queue[current])
            current = (current + 1) % self.max_capacity

        # Sort by priority (higher first), then by waiting time (longer first)
        jobs.sort(key=lambda job: (-job.priority, -job.waiting_time))

        # Rebuild queue with sorted jobs
        self._rebuild_queue(jobs)
        print("Queue re-sorted by priority after aging")

    def _rebuild_queue(self, sorted_jobs: List[Job]):
        """Rebuild the circular queue with sorted jobs"""
        # Clear current queue
        self.queue = [None] * self.max_capacity
        self.front = 0
        self.rear = -1
        self.size = 0

        # Add sorted jobs back
        for job in sorted_jobs:
            self.rear = (self.rear + 1) % self.max_capacity
            self.queue[self.rear] = job
            self.size += 1

    def _remove_job_from_queue(self, job_to_remove: Job):
        """Remove a specific job from the queue"""
        if job_to_remove.job_id not in self.active_jobs:
            return

        # Remove from active jobs tracking
        del self.active_jobs[job_to_remove.job_id]

        # Remove from circular queue
        new_queue = []
        current = self.front
        for _ in range(self.size):
            job = self.queue[current]
            if job and job.job_id != job_to_remove.job_id:
                new_queue.append(job)
            current = (current + 1) % self.max_capacity

        # Rebuild queue without the removed job
        self._rebuild_queue(new_queue)

    def _log_event(self, event_type: str, details: Dict):
        """Log events for debugging and analysis"""
        event = {
            "timestamp": time.time(),
            "system_time": self.system_time,
            "tick": self.tick_count,
            "event_type": event_type,
            "details": details
        }
        self.events_log.append(event)

        # Keep only last 100 events to prevent memory issues
        if len(self.events_log) > 100:
            self.events_log = self.events_log[-100:]

    def get_system_status(self) -> Dict:
        """Get current system status including time information"""
        return {
            "system_time": self.system_time,
            "tick_count": self.tick_count,
            "aging_interval": self.aging_interval,
            "expiry_time": self.expiry_time,
            "last_aging_time": self.last_aging_time,
            "next_aging_in": max(0, self.aging_interval - (self.system_time - self.last_aging_time)),
            "active_jobs": len(self.active_jobs),
            "queue_size": self.size
        }

    def simulate_time_passage(self, seconds: int):
        """Simulate multiple seconds passing at once"""
        print(f"\nSimulating {seconds} seconds of time passage...")
        for _ in range(seconds):
            self.tick()
            time.sleep(0.1)  # Small delay for visualization

    def reset_time(self):
        """Reset the time management system"""
        with self.lock:
            self.system_time = 0
            self.tick_count = 0
            self.last_aging_time = 0
            self.events_log.clear()
            print("Time management system reset")

    # Basic queue operations (simplified for Module 5 focus)
    def enqueue_job(self, user_id: str, job_id: str, priority: int) -> bool:
        """Add job to queue with time tracking"""
        with self.lock:
            if self.size >= self.max_capacity:
                return False

            if job_id in self.active_jobs:
                return False

            job = Job(user_id, job_id, priority)
            job.submission_time = self.system_time  # Use system time

            self.rear = (self.rear + 1) % self.max_capacity
            self.queue[self.rear] = job
            self.size += 1
            self.active_jobs[job_id] = job

            self._log_event("enqueue", {
                "job_id": job_id,
                "user_id": user_id,
                "priority": priority
            })

            return True

    def show_status(self):
        """Show system status with time information"""
        status = self.get_system_status()

        print("\n" + "=" * 60)
        print("SYSTEM STATUS - TIME MANAGEMENT")
        print("=" * 60)
        print(f"System Time: {status['system_time']}s (Tick #{status['tick_count']})")
        print(f"Aging Interval: {status['aging_interval']}s")
        print(f"Job Expiry Time: {status['expiry_time']}s")
        print(f"Next Aging: {status['next_aging_in']}s")
        print(f"Active Jobs: {status['active_jobs']}")
        print(f"Queue Size: {status['queue_size']}")

        if self.active_jobs:
            print(f"\nActive Jobs Details:")
            print("-" * 60)
            for i, job in enumerate(self.active_jobs.values(), 1):
                expires_in = max(0, self.expiry_time - job.waiting_time)
                print(f"{i:2d}. {job} (expires in {expires_in}s)")

        print("=" * 60 + "\n")


# Testing the Module 5 functionality
if __name__ == "__main__":
    print("Testing Module 5 - Event Simulation & Time Management")
    print("=" * 55)

    # Create queue manager with time settings
    pq_manager = PrintQueueManager(
        max_capacity=5,
        aging_interval=3,  # Age every 3 seconds
        expiry_time=10  # Jobs expire after 10 seconds
    )

    # Add some jobs
    pq_manager.enqueue_job("user1", "job1", 2)
    pq_manager.enqueue_job("user2", "job2", 1)
    pq_manager.enqueue_job("user3", "job3", 3)

    # Show initial status
    pq_manager.show_status()

    # Simulate time passing
    print("Simulating time passage...")
    for i in range(1, 12):  # Simulate 11 seconds
        print(f"\n--- Simulating second {i} ---")
        pq_manager.tick()

        # Show status at key intervals
        if i % 3 == 0:
            pq_manager.show_status()

    print("\nModule 5 testing complete!")