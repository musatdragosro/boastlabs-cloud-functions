# -*- coding: utf-8 -*-
""" Utility functions to simplify Google Cloud Function implementation.

This package allows simple GCP function creation by subclassing a base Task
and implementing it's `work` routine.

It will handle GPC max timeout, event handling in case of multiple GCP calls
to same function in the context of the same event, error handling, state
management (function can be `running`, `failed`, `success`, etc.)

It also provides 2 helper functions to manage simple data pipeline implementation
with a `dispatcher` and a list of `workflow tasks`.

Example GCP dispatch function:
        >>> from typing import List
        ... 
        ... import firebase_admin
        ... from firebase_admin import firestore
        ...
        ... from gcf.functions import DispatchTask
        ... from gcf.functions import Function
        ...
        ... firebase_admin.initialize_app()
        ... db = firestore.client()
        ...
        ... class TestDispatch(DispatchTask):
        ...
        ...     def get_workflow(self) -> List[str]:
        ...        return ['task1', 'task2']
        ...
        ... def trigger(data, context):
        ...    print(f"Function triggered by change to: {context.resource}.")
        ...
        ...    Function(
        ...        db=db,
        ...        event_path=context.resource.split('/documents/')[1],
        ...        worker_class=TestDispatch
        ...    ).run(timeout_seconds=540)


Deploy GCP dispatch function:
        >>> gcloud functions deploy dispatch_task
        ...    --runtime python37
        ...    --retry
        ...    --timeout 540
        ...    --entry-point trigger
        ...    --trigger-event providers/cloud.firestore/eventTypes/document.create
        ...    --trigger-resource "projects/<YOUR_PROJECT_ID>/databases/(default)/documents/<ROOT_COLLECTION>/<ROOT_DOCUMENT>/dispatch_tasks/{dispatchTaskId}/events/{eventId}"

Note:
    Dispatch function will call ``task1`` and ``task2`` in this order.
    The names associated with the functions must be reused in the `workflow` tasks as described
    below.

    The firestore path above shoule be read as:
        * `projects/<YOUR_PROJECT_ID>/databases/(default)/documents/`: required by GCP.
        * `<ROOT_COLLECTION>/<ROOT_DOCUMENT>`: a path of one choosing acting as the root document for the pipeline execution.
        * `dispatch_tasks`: a collection representing the grouping of pipeline executions. Name is not important, only the presence of this document is.
        * `{dispatchTaskId}`: Document for tracking the execution state of dispacher
        * `events`: Collection of events to triggering events.
        * `{eventId}`: Document for triggering the execution.
    
    The events for the inner tasks will be generated under the same path as follows:
        * task1: ..dispatch_tasks/{dispatchTaskId}/tasks/``task1``/events/{eventId}
        * task2: ..dispatch_tasks/{dispatchTaskId}/tasks/``task2``/events/{eventId}

Example GCP workflow function:
        >>> import firebase_admin
        ... from firebase_admin import firestore
        ...
        ... from gcf.functions import WorkflowTask
        ... from gcf.functions import Function
        ...
        ... firebase_admin.initialize_app()
        ... db = firestore.client()
        ...
        ... class Task1(WorkflowTask):
        ...
        ...    def get_task_name(self) -> str:
        ...        return 'task1'
        ...
        ...    def work(self):
        ...        print(self.get_task_name(), 'done')
        ...
        ... def trigger(data, context):
        ...    print(f"Function triggered by change to: {context.resource}.")
        ...
        ...    Function(
        ...        db=db,
        ...        event_path=context.resource.split('/documents/')[1],
        ...        worker_class=Task1
        ...    ).run(timeout_seconds=540)

Note:
    Here the task name as returned by `get_task_name` must be ``task1``.

Deploy GCP workflow function:
        >>> gcloud functions deploy task_1
        ...    --runtime python37
        ...    --retry
        ...    --timeout 540
        ...    --entry-point trigger
        ...    --trigger-event providers/cloud.firestore/eventTypes/document.create
        ...    --trigger-resource "projects/<YOUR_PROJECT_ID>/databases/(default)/documents/<ROOT_COLLECTION>/<ROOT_DOCUMENT>/dispatch_tasks/{dispatchTaskId}/tasks/task1/events/{eventId}"

Note:
    Here the task name as part of firestore document path must be ``task1``.

"""

__version__ = "1.0.13"
