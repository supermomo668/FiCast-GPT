import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
import dotenv, os

dotenv.load_dotenv(".env")

from ficast.conversation.podcast import Podcast
from ficast.character.podcast import Podcaster
from apps.ficast.app.tasks.task import Task
from apps.ficast.app.models.request import PodcastRequest

class TestTask(unittest.TestCase):
    def setUp(self):
        # Set up mock DB session and PodcastRequest
        self.mock_db = MagicMock(spec=Session)
        self.request1 = PodcastRequest(
            topic="Health & Longevity",
            n_rounds=3,
            participants=[
                Podcaster(name="Joe Rogan", description="Host", model="gemini-1.5-pro", role="host").model_dump(),
                Podcaster(name="David Sinclair", description="Guest", model="gemini-1.5-pro", role="guest").model_dump()
            ]
        )
        self.request2 = PodcastRequest(
            topic="AI in Healthcare",
            n_rounds=3,
            participants=[
                Podcaster(name="Elon Musk", description="Host", model="gemini-1.5-pro", role="host").model_dump(),
                Podcaster(name="Sam Altman", description="Guest", model="gemini-1.5-pro", role="guest").model_dump()
            ]
        )

    def test_no_leakage_of_participants_between_tasks(self):
        # Create two Task instances with different podcast requests
        task1 = Task(self.mock_db)
        task2 = Task(self.mock_db)

        # Mock the internal _execute_create_podcast_task method
        # task1._execute_create_podcast_task = MagicMock()
        # task2._execute_create_podcast_task = MagicMock()

        # Call create_podcast with different requests
        task1.create_podcast(self.request1)
        task2.create_podcast(self.request2)

        # Check if the participants from task1 and task2 are separate
        self.assertNotEqual(task1._execute_create_podcast_task.call_args[0][0].participants,
                            task2._execute_create_podcast_task.call_args[0][0].participants)

        # Check that the first request participants are correct
        self.assertEqual(task1._execute_create_podcast_task.call_args[0][0].participants[0].name, "Joe Rogan")
        self.assertEqual(task1._execute_create_podcast_task.call_args[0][0].participants[1].name, "David Sinclair")

        # Check that the second request participants are correct
        self.assertEqual(task2._execute_create_podcast_task.call_args[0][0].participants[0].name, "Elon Musk")
        self.assertEqual(task2._execute_create_podcast_task.call_args[0][0].participants[1].name, "Sam Altman")

if __name__ == '__main__':
    unittest.main()
