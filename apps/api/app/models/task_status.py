from enum import Enum

class TaskStatus(Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"

    @classmethod
    def from_celery_state(cls, state: str):
        """
        Convert a Celery task state to a TaskStatus enum.
        
        :param state: The state string from Celery (e.g., "PENDING", "SUCCESS").
        :type state: str
        :return: Corresponding TaskStatus enum.
        :rtype: TaskStatus
        """
        try:
            return cls[state]
        except KeyError:
            raise ValueError(f"Unknown Celery task state: {state}")
