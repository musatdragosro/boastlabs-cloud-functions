from gcf.functions import Function
from gcf.functions import Worker
from gcf.functions.workflow.events import TaskStartEvent


class MyTask(Worker):

    def work(self):
        print(self.get_task_name(), 'done')

        doc_ref = self.event.parent_ref
        data = {
            'event_received': True,
            'event_context': {
                'param1': 'param1',
                'param2': 100,
                'path': self.event.event_ref.path,
                'firestore_data': self.event.firestore_data,
            }
        }
        doc_ref.update({
            'data': data
        })


def test(db, root_path):
    _, task_ref = db.collection(root_path).add({})
    _, start_task_ref = task_ref.collection('events').add(TaskStartEvent(task_name='my-task').to_dict())

    f = Function(db=db, event_path=start_task_ref.path, worker_class=MyTask)
    f.run(timeout_seconds=360)
