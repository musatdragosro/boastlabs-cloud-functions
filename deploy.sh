# https://cloud.google.com/sdk/gcloud/reference/functions/deploy
# https://stackoverflow.com/questions/55835712/gcloud-functions-deploy-deploys-code-that-cannot-listen-to-firestore-events

gcloud functions deploy github_ingest \
    --runtime python37 \
    --timeout 360 \
    --memory 2048 \
    --retry \
    --entry-point trigger \
    --trigger-event providers/cloud.firestore/eventTypes/document.create \
    --trigger-resource "projects/boast-firebase/databases/(default)/documents/debug/{tenantDB}/integrations/Github/fiscal_years/{fiscalYearCode}/etl_jobs/{etlJobId}/jobs/ingest/events/{triggerId}"
