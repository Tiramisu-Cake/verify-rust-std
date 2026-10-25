#!/usr/bin/env bash
# One-time owner setup of the GCP project for K-1 resource measurements (32 GB runs).
# Run by the owner in Google Cloud Shell (gcloud is already logged in as the owner), after creating
# the project in the console. Safe to re-run: existing resources are kept.
#
#   bash owner-setup.sh [PROJECT_ID]          # default smallsort-k1
#
# The dispatcher key is written to ~/k1-gcp-key.json. Move it to the server as
# /root/.config/smallsort-ci/k1-gcp-key.json (mode 600), then delete it from Cloud Shell and from any
# local download. Never paste it into a chat.
set -euo pipefail

PROJECT=${1:-smallsort-k1}
REGION=us-central1
POOL=k1-highmem4
MACHINE=e2-highmem-4                      # 4 vCPU / 32 GB
BUCKET=gs://$PROJECT-k1-runs
BUILD_SA=k1-build@$PROJECT.iam.gserviceaccount.com
DISP_SA=k1-dispatcher@$PROJECT.iam.gserviceaccount.com
KEY=${K1_KEY:-$HOME/k1-gcp-key.json}
BUDGET_USD=10

step() { echo; echo "== $*"; }
quiet() { "$@" >/dev/null 2>&1; }

step "project $PROJECT"
quiet gcloud projects describe "$PROJECT" || { echo "project $PROJECT not found; create it in the console first" >&2; exit 1; }
BILLING=$(gcloud billing projects describe "$PROJECT" --format='value(billingAccountName)')
BILLING=${BILLING#billingAccounts/}
[ -n "$BILLING" ] || { echo "billing is not linked to $PROJECT; link it in the console (Billing) first" >&2; exit 1; }
echo "billing account $BILLING"

step "APIs"
gcloud services enable cloudbuild.googleapis.com storage.googleapis.com iam.googleapis.com \
  billingbudgets.googleapis.com --project="$PROJECT"

step "budget alert \$$BUDGET_USD (alerts only, does not stop spending)"
if gcloud billing budgets list --billing-account="$BILLING" --format='value(displayName)' | grep -qx smallsort-k1; then
  echo "exists"
else
  gcloud billing budgets create --billing-account="$BILLING" --display-name="smallsort-k1" \
    --budget-amount="${BUDGET_USD}USD" --filter-projects="projects/$PROJECT" \
    --threshold-rule=percent=0.5 --threshold-rule=percent=0.9 --threshold-rule=percent=1.0
fi

step "private pool $POOL ($MACHINE, $REGION, public egress for git/crates/apt)"
if quiet gcloud builds worker-pools describe "$POOL" --project="$PROJECT" --region="$REGION"; then
  echo "exists"
else
  gcloud builds worker-pools create "$POOL" --project="$PROJECT" --region="$REGION" \
    --worker-machine-type="$MACHINE" --worker-disk-size=100
fi

step "bucket $BUCKET (objects deleted after 30 days)"
if quiet gcloud storage buckets describe "$BUCKET"; then
  echo "exists"
else
  gcloud storage buckets create "$BUCKET" --project="$PROJECT" --location="$REGION" \
    --uniform-bucket-level-access --public-access-prevention
fi
LC=$(mktemp); echo '{"rule":[{"action":{"type":"Delete"},"condition":{"age":30}}]}' > "$LC"
gcloud storage buckets update "$BUCKET" --lifecycle-file="$LC"; rm -f "$LC"

step "service accounts"
for sa in k1-build k1-dispatcher; do
  if quiet gcloud iam service-accounts describe "$sa@$PROJECT.iam.gserviceaccount.com" --project="$PROJECT"; then
    echo "$sa exists"
  else
    gcloud iam service-accounts create "$sa" --project="$PROJECT" --display-name="${sa/k1-/K1 }"
  fi
done
sleep 10   # IAM propagation

step "roles: build SA writes logs and artifacts to the bucket only"
gcloud storage buckets add-iam-policy-binding "$BUCKET" \
  --member="serviceAccount:$BUILD_SA" --role=roles/storage.objectAdmin >/dev/null

step "roles: dispatcher submits builds to the pool, reads the bucket, runs builds as the build SA"
for role in roles/cloudbuild.builds.editor roles/cloudbuild.workerPoolUser; do
  gcloud projects add-iam-policy-binding "$PROJECT" --condition=None \
    --member="serviceAccount:$DISP_SA" --role="$role" >/dev/null
done
gcloud storage buckets add-iam-policy-binding "$BUCKET" \
  --member="serviceAccount:$DISP_SA" --role=roles/storage.objectViewer >/dev/null
gcloud iam service-accounts add-iam-policy-binding "$BUILD_SA" --project="$PROJECT" \
  --member="serviceAccount:$DISP_SA" --role=roles/iam.serviceAccountUser >/dev/null

step "dispatcher key -> $KEY"
if [ -e "$KEY" ]; then
  echo "$KEY already exists, no new key created"
else
  (umask 077; gcloud iam service-accounts keys create "$KEY" --iam-account="$DISP_SA")
fi

step "done"
echo "project=$PROJECT region=$REGION pool=projects/$PROJECT/locations/$REGION/workerPools/$POOL"
echo "bucket=$BUCKET build_sa=$BUILD_SA dispatcher=$DISP_SA key=$KEY"
