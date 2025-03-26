curl -X POST localhost:8080 \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-H "ce-id: 1234567890" \
-H "ce-specversion: 1.0" \
-H "ce-type: google.cloud.storage.object.v1.finalized" \
-H "ce-time: 2020-08-08T00:11:44.895529672Z" \
-H "ce-source: //storage.googleapis.com/projects/_/buckets/$BUCKET_NAME" \
-d "$(cat payload_example.json)"