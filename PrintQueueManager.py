import time
import threading
from typing import Optional, List, Dict


class Job:
    """Represents a print job with all required metadata"""

    def __init__(self, user_id: str, job_id: str, priority: int):
        self.user_id = user_id
        self.job_id = job_id
        self.priority = priority
        self.submission_time = time.time()
        self.waiting_time = 0

    def __str__(self):
        return f"Job({self.job_id}, User: {self.user_id}, Priority: {self.priority}, Wait: {self.waiting_time}s)"


class PrintQueueManager:
    """Core Queue Management Module - Circular Queue Implementation"""

    def __init__(self, max_capacity: int = 10):
        # Circular queue with fixed capacity
        self.max_capacity = max_capacity
        self.queue = [None] * max_capacity
        self.front = 0
        self.rear = -1
        self.size = 0

        # Thread safety for concurrent operations
        self.lock = threading.Lock()

        # Job tracking for metadata management
        self.active_jobs: Dict[str, Job] = {}

    def enqueue_job(self, user_id: str, job_id: str, priority: int) -> bool:
        """
        Add a new print job to the queue

        Args:
            user_id: ID of the user submitting the job
            job_id: Unique identifier for the job
            priority: Initial priority of the job

        Returns:
            bool: True if successful, False if queue is full or job exists
        """
        with self.lock:
            # Check if queue is full
            if self.size >= self.max_capacity:
                print(f"Queue is full! Cannot add job {job_id}")
                return False

            # Check for duplicate job IDs
            if job_id in self.active_jobs:
                print(f"Job {job_id} already exists!")
                return False

            # Create new job with metadata
            job = Job(user_id, job_id, priority)

            # Add to circular queue
            self.rear = (self.rear + 1) % self.max_capacity
            self.queue[self.rear] = job
            self.size += 1

            # Track in active jobs
            self.active_jobs[job_id] = job

            print(f"Job {job_id} from user {user_id} enqueued (Priority: {priority})")
            return True

    def dequeue_job(self) -> Optional[Job]:
        """
        Remove and return the next job from the queue

        Returns:
            Job: The next job to process, or None if queue is empty
        """
        with self.lock:
            if self.size == 0:
                return None

            # Get job from front of circular queue
            job = self.queue[self.front]
            self.queue[self.front] = None

            # Update circular queue pointers
            self.front = (self.front + 1) % self.max_capacity
            self.size -= 1

            # Remove from active jobs tracking
            if job and job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]

            return job

    def print_job(self) -> bool:
        """
        Process/print the next job in the queue

        Returns:
            bool: True if a job was printed, False if queue is empty
        """
        job = self.dequeue_job()
        if job is None:
            print("No jobs in queue to print")
            return False

        print(f"PRINTING: {job}")
        return True

    def show_status(self):
        """Display current queue status and all jobs"""
        with self.lock:
            print("\n" + "=" * 50)
            print("PRINT QUEUE STATUS")
            print("=" * 50)
            print(f"Queue Size: {self.size}/{self.max_capacity}")
            print(
                f"Queue State: {'EMPTY' if self.size == 0 else 'FULL' if self.size == self.max_capacity else 'ACTIVE'}")

            if self.size > 0:
                print(f"\nJobs in Queue (Print Order):")
                print("-" * 50)

                # Display jobs in order from front to rear
                current = self.front
                for i in range(self.size):
                    job = self.queue[current]
                    if job:
                        print(f"{i + 1:2d}. {job}")
                    current = (current + 1) % self.max_capacity
            else:
                print("\nNo jobs in queue")

            print("=" * 50 + "\n")

    # Helper methods for other modules to use
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.size == 0

    def is_full(self) -> bool:
        """Check if queue is full"""
        return self.size >= self.max_capacity

    def get_all_jobs(self) -> List[Job]:
        """Get all jobs in queue order (for other modules)"""
        with self.lock:
            jobs = []
            if self.size == 0:
                return jobs

            current = self.front
            for _ in range(self.size):
                if self.queue[current]:
                    jobs.append(self.queue[current])
                current = (current + 1) % self.max_capacity
            return jobs


# Test the module
if __name__ == "__main__":
    # Create queue manager
    pq_manager = PrintQueueManager(max_capacity=5)

    print("Testing Module 1 - Core Queue Management")
    print("=" * 45)

    # Test enqueue operations
    pq_manager.enqueue_job("user1", "job1", 3)
    pq_manager.enqueue_job("user2", "job2", 1)
    pq_manager.enqueue_job("user1", "job3", 5)

    # Show current status
    pq_manager.show_status()

    # Test print operation
    pq_manager.print_job()
    pq_manager.show_status()

    # Test queue full scenario
    print("Testing queue capacity limits...")
    for i in range(4, 8):
        pq_manager.enqueue_job(f"user{i}", f"job{i}", i)

    pq_manager.show_status()