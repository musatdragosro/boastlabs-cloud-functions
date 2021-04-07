# https://googleapis.dev/python/firestore/latest/client.html
# https://cloud.google.com/functions/docs/calling/cloud-firestore
# https://cloud.google.com/sdk/gcloud/reference/functions/deploy#--trigger-event


import firebase_admin
from firebase_admin import firestore
from etl.execution.process import Process
from etl.execution.worker import NoopWorker

firebase_admin.initialize_app()
db = firestore.client()


def trigger(request, context):
    # tenants/{tenantDB}/integrations/Github/fiscal_years/{fiscalYearCode}/etl_jobs/{etlJobId}/jobs/ingest/triggers/{triggerId}

    print(f"Function triggered by change to: {context.resource}.")

    event_path = context.resource.split('/documents/')[1]

    Process(db=db, event_path=event_path, worker_class=NoopWorker).run()


if __name__ == '__main__':

    # ep = 'debug/test-tenant-0/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs/Lq6MVMWKk80GZ8jLEZ0y/jobs/ingest/events/llT8NsocvoVGxcw70PdZ'
    ep = 'debug/test-tenant-0/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs/gUCIuXaWHAeY6SFoEl8m/jobs/ingest/events/7POzoWAkMJeZlwnUyWD8'

    Process(db=db, event_path=ep, worker_class=NoopWorker).run()
