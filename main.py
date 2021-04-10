# https://googleapis.dev/python/firestore/latest/client.html
# https://cloud.google.com/functions/docs/calling/cloud-firestore
# https://cloud.google.com/sdk/gcloud/reference/functions/deploy#--trigger-event


import firebase_admin
from firebase_admin import firestore

from boastlabs.functions import Function
from boastlabs.functions.dispatch.worker import Dispatch
from boastlabs.functions.jobs.worker import Job

firebase_admin.initialize_app()
db = firestore.client()

if __name__ == '__main__':

    Function(
        service_name='github_dispatcher',
        db=db,
        event_path='tenants/test/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs/64AIT1AiFZIYkX697kXa/events/WXpL7VbAswhHxtOEhY5b',
        worker_class=Dispatch
    ).run(timeout_seconds=360)

    # Function(
    #     service_name='ingest',
    #     db=db,
    #     event_path='tenants/test/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs/64AIT1AiFZIYkX697kXa/jobs/ingest/events/5xeaNlZC2QGurOIUvqfX',
    #     worker_class=Job
    # ).run(timeout_seconds=360)

    # Function(
    #     service_name='transform',
    #     db=db,
    #     event_path='tenants/test/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs/64AIT1AiFZIYkX697kXa/jobs/transform/events/8U6kYPkOokLkAMTqia0o',
    #     worker_class=Job
    # ).run(timeout_seconds=360)

    # Function(
    #     service_name='summary',
    #     db=db,
    #     event_path='tenants/test/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs/64AIT1AiFZIYkX697kXa/jobs/summary/events/nMt8n8VGucCvNilcypcG',
    #     worker_class=Job
    # ).run(timeout_seconds=360)
    #
