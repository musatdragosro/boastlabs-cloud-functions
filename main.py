import time
from typing import List

import firebase_admin
from firebase_admin import firestore

from boastlabs.functions import Function
from boastlabs.functions.dispatch.tasks import DispatchTask
from boastlabs.functions.dispatch.events import DispatchStartEvent
from boastlabs.functions.workflow.tasks import WorkflowTask

firebase_admin.initialize_app()
db = firestore.client()


class TestDispatchTask(DispatchTask):

    def get_workflow(self) -> List[str]:
        return ['ingest', 'transform', 'summary']


class IngestTask(WorkflowTask):

    def get_task_name(self) -> str:
        return 'ingest'

    def work(self):
        time.sleep(5)
        print(self.get_task_name(), 'done')


class TransformTask(WorkflowTask):

    def get_task_name(self) -> str:
        return 'transform'

    def work(self):
        time.sleep(5)
        print(self.get_task_name(), 'done')


class SummaryTask(WorkflowTask):

    def get_task_name(self) -> str:
        return 'summary'

    def work(self):
        time.sleep(5)
        print(self.get_task_name(), 'done')


if __name__ == '__main__':
    root_path = 'tenants/test/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs'
    _, dispatch_ref = db.collection(root_path).add({})
    _, start_event_ref = dispatch_ref.collection('events').add(DispatchStartEvent().to_dict())

    dispatcher = Function(db=db, event_path=start_event_ref.path, worker_class=TestDispatchTask)
    dispatcher.run(timeout_seconds=360)

    generated_event_ref = dispatcher.worker.get_generated_event()

    # dispatch_event_path = 'tenants/test/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs/rjiXG8ThDzx2YXuCU7Oy/events/e3xSyjlLAvouc6iQ1lxU'
    #
    # dispatcher = Function(db=db, event_path=dispatch_event_path, worker_class=TestDispatchTask)
    # dispatcher.run(timeout_seconds=360)
    #
    # generated_event_ref = dispatcher.worker.get_generated_event()

    tasks = [
        {'task': 'ingest', 'worker_class': IngestTask},
        {'task': 'transform', 'worker_class': TransformTask},
        {'task': 'summary', 'worker_class': SummaryTask},
    ]

    for task in tasks:
        next_function = Function(db=db, event_path=generated_event_ref.path, worker_class=task['worker_class'])
        next_function.run(timeout_seconds=360)
        generated_event_ref = next_function.worker.get_generated_event()

        next_function = Function(db=db, event_path=generated_event_ref.path, worker_class=TestDispatchTask)
        next_function.run(timeout_seconds=360)
        generated_event_ref = next_function.worker.get_generated_event()
