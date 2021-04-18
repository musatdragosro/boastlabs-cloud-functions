import threading
import traceback

from typing import List
from abc import abstractmethod, ABC
from datetime import datetime

from firebase_admin import firestore
from google.cloud.firestore_v1 import DocumentReference

from gcf.functions.execution.exceptions import RetryException, SleepException
from gcf.functions.execution.threading import TimedThread
from gcf.functions.execution.time import Timer
from gcf.functions.execution.events.events import Event
from gcf.functions.execution.config import ExecutionStatus
from gcf.functions.execution.progress import Progress


class AbstractWorker(TimedThread):

    task_name: str

    created_at: datetime
    modified_at: datetime

    status: ExecutionStatus

    error: str
    error_stack: str

    _progress: Progress

    def __init__(self, timer: Timer, event: Event):
        TimedThread.__init__(self, timer=timer)

        self.event = event
        self.doc_ref = event.parent_ref

        self.data = self.read_data()

        self._read_lock = threading.RLock()
        self._write_lock = threading.RLock()

        # Load progress
        if self.doc_ref.collection('progress').document('progress').get().exists:
            self._progress = Progress(
                id='progress',
                progress=self.doc_ref.collection('progress').document('progress').get().to_dict().get('progress', None)
            )
        else:
            self._progress = Progress(id='progress', progress=None)

        self.sleep_duration = 540

    def read_data(self):
        data = self.doc_ref.get().to_dict()

        self.created_at = data.get('created_at', None)
        self.modified_at = data.get('modified_at', None)
        self.status = data.get('status', ExecutionStatus.WAITING_EXECUTION)
        self.error = data.get('error', None)
        self.error_stack = data.get('error_stack', None)

        return data

    def set_created_at(self):
        if self.created_at is None:
            self.doc_ref.update({'created_at': firestore.SERVER_TIMESTAMP})

    def set_modified_at(self):
        self.doc_ref.update({'modified_at': firestore.SERVER_TIMESTAMP})

    def set_status(self, status: ExecutionStatus):
        self.doc_ref.update({
            'status': status,
            'modified_at': firestore.SERVER_TIMESTAMP
        })
        self.status = status

    def set_error(self, error: Exception):
        error_string = repr(error)
        error_stack = traceback.format_exc()

        self.doc_ref.update({
            'error': error_string,
            'error_stack': error_stack
        })

    def reset(self):
        self.doc_ref.update({
            'error': None,
            'error_stack': None
        })

    def get_sleep_duration(self):
        return self.sleep_duration

    def save_progress(self):
        with self._write_lock:
            self.set_modified_at()
            self.doc_ref.collection('progress').document('progress').set({
                'progress': self._progress.to_dict()
            }, merge=True)

    def get_progress(self, items: List[str]) -> Progress:
        """
        todo: add documentation, mandatory function
        :param items:
        :return:
        """

        # This will basically do a return progress[user_name][organisation][repo][kind]

        with self._read_lock:
            p = self._progress
            for item in items:
                p = p[item]
            return p

    def run(self):
        self.set_created_at()
        self.set_modified_at()

        # Test event.status to figure out what the function has to to
        # It can be only SLEEP or RUN
        if self.status == ExecutionStatus.SLEEPING:
            self.set_status(ExecutionStatus.SLEEPING)
            duration = self.get_sleep_duration()

            # Wait duration / can be interrupted by timeout
            self.logger.debug(f"# SLEEP START {duration}")
            self.timer.timeout_event.wait(duration)
            self.logger.debug(f"# SLEEP END")

            # Exit with WAITING_RETRY state and resume execution on next call
            self.set_status(ExecutionStatus.WAITING_RETRY)

        if self.status == ExecutionStatus.RUNNING:
            self.logger.debug(f"# RUNNING")
            try:
                self.set_status(ExecutionStatus.RUNNING)
                self.work()
                self.set_status(ExecutionStatus.SUCCESS)
            except RetryException:
                self.set_status(ExecutionStatus.WAITING_RETRY)
            except SleepException:
                self.set_status(ExecutionStatus.WAITING_SLEEP)
            except Exception as e:
                self.set_status(ExecutionStatus.FAILED)
                self.set_error(e)
                raise e

    @abstractmethod
    def work(self):
        raise NotImplementedError


class WorkflowWorker(AbstractWorker, ABC):
    generated_event: DocumentReference

    def __init__(self, timer: Timer, event: Event):
        AbstractWorker.__init__(self, timer, event)
        self.generated_event = None

    def set_generated_event(self, generated_event):
        self.generated_event = generated_event

    def get_generated_event(self):
        return self.generated_event


class Task(AbstractWorker, ABC):
    pass
