import firebase_admin
from firebase_admin import firestore

from tests import data_pipeline, simple_functions

firebase_admin.initialize_app()
db = firestore.client()


if __name__ == '__main__':
    pass
    # data_pipeline.test(db=db, root_path='tenants/dragos/integrations/Github/fiscal_years/31-Dec-21 FYE/etl_jobs')
    # simple_functions.test(db=db, root_path='tenants/dragos/integrations/Salesforce/events')
