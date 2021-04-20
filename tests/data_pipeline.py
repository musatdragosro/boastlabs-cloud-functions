from typing import List

from gcf.functions import Function
from gcf.functions import DispatchTask
from gcf.functions import WorkflowTask
from gcf.functions.dispatch.events import DispatchStartEvent


class TestDispatchTask(DispatchTask):

    def get_workflow(self) -> List[str]:
        return ['ingest', 'transform', 'summary']


class IngestTask(WorkflowTask):

    def get_task_name(self) -> str:
        return 'ingest'

    def work(self):
        progress1 = self.get_progress(['logs', 'users', 'user1', 'data retrieved'])
        progress2 = self.get_progress(['logs', 'users', 'user2', 'data retrieved'])
        progress1.update(ready=True)
        progress2.update(ready=True)
        self.save_progress()
        print(self.get_task_name(), 'done')


class TransformTask(WorkflowTask):

    def get_task_name(self) -> str:
        return 'transform'

    def work(self):
        print(self.get_task_name(), 'done')


class SummaryTask(WorkflowTask):

    def get_task_name(self) -> str:
        return 'summary'

    def work(self):
        print(self.get_task_name(), 'done')


def test(db, root_path):
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
