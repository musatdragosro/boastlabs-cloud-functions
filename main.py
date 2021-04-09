# https://googleapis.dev/python/firestore/latest/client.html
# https://cloud.google.com/functions/docs/calling/cloud-firestore
# https://cloud.google.com/sdk/gcloud/reference/functions/deploy#--trigger-event


import firebase_admin
from firebase_admin import firestore

from boastlabs.functions.retriable import Function

firebase_admin.initialize_app()
db = firestore.client()

if __name__ == '__main__':

    Function(
        service_name='ingest',
        db=db,
        event_path='tenants/test/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs/64AIT1AiFZIYkX697kXa/jobs/ingest/events/MRnASWI4v4z4k1USXg2Q'
    ).run(timeout_seconds=360)
