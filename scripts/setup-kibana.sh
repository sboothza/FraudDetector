#!/bin/sh
set -e

KIBANA_URL="${KIBANA_URL:-http://kibana:5601}"
DATA_VIEW_TITLE="${DATA_VIEW_TITLE:-fraud-detector-*}"
SEARCH_ID="${SEARCH_ID:-fraud-detector-logs-search}"
DASHBOARD_ID="${DASHBOARD_ID:-fraud-detector-logs-dashboard}"

kbn() {
  curl -sf "$@" -H "kbn-xsrf: setup" -H "Content-Type: application/json"
}

echo "Waiting for Kibana at ${KIBANA_URL}..."
until curl -sf "${KIBANA_URL}/api/status" >/dev/null; do
  sleep 2
done

echo "Looking up data view '${DATA_VIEW_TITLE}'..."
data_views="$(kbn "${KIBANA_URL}/api/data_views")"
data_view_id="$(echo "${data_views}" | grep -o '"id":"[^"]*","namespaces":\[[^]]*\],"title":"fraud-detector-\*"' \
  | head -1 \
  | sed 's/.*"id":"\([^"]*\)".*/\1/')"

if [ -z "${data_view_id}" ]; then
  echo "Creating data view '${DATA_VIEW_TITLE}'..."
  create_response="$(kbn -X POST "${KIBANA_URL}/api/data_views/data_view" -d "{
    \"data_view\": {
      \"title\": \"${DATA_VIEW_TITLE}\",
      \"name\": \"Fraud Detector Logs\",
      \"timeFieldName\": \"@timestamp\"
    }
  }")"
  data_view_id="$(echo "${create_response}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)"
  echo "Data view created (id=${data_view_id})."
else
  echo "Data view already exists (id=${data_view_id})."
fi

echo "Setting default data view..."
kbn -X POST "${KIBANA_URL}/api/data_views/default" \
  -d "{\"data_view_id\":\"${data_view_id}\",\"force\":true}" >/dev/null

echo "Creating saved search..."
kbn -X POST "${KIBANA_URL}/api/saved_objects/search/${SEARCH_ID}?overwrite=true" -d "{
  \"attributes\": {
    \"title\": \"Fraud Detector Logs\",
    \"description\": \"Application log events\",
    \"columns\": [\"level\", \"logger\", \"log_message\", \"service\"],
    \"sort\": [[\"@timestamp\", \"desc\"]],
    \"kibanaSavedObjectMeta\": {
      \"searchSourceJSON\": \"{\\\"query\\\":{\\\"query\\\":\\\"\\\",\\\"language\\\":\\\"kuery\\\"},\\\"filter\\\":[],\\\"indexRefName\\\":\\\"kibanaSavedObjectMeta.searchSourceJSON.index\\\"}\"
    }
  },
  \"references\": [
    {
      \"name\": \"kibanaSavedObjectMeta.searchSourceJSON.index\",
      \"type\": \"index-pattern\",
      \"id\": \"${data_view_id}\"
    }
  ]
}" >/dev/null

echo "Creating dashboard..."
kbn -X POST "${KIBANA_URL}/api/saved_objects/dashboard/${DASHBOARD_ID}?overwrite=true" -d "{
  \"attributes\": {
    \"title\": \"Fraud Detector Logs\",
    \"description\": \"Application logs shipped from the API via Logstash\",
    \"panelsJSON\": \"[{\\\"version\\\":\\\"8.15.3\\\",\\\"type\\\":\\\"search\\\",\\\"gridData\\\":{\\\"x\\\":0,\\\"y\\\":0,\\\"w\\\":48,\\\"h\\\":28,\\\"i\\\":\\\"panel_logs\\\"},\\\"panelIndex\\\":\\\"panel_logs\\\",\\\"embeddableConfig\\\":{\\\"enhancements\\\":{}},\\\"panelRefName\\\":\\\"panel_panel_logs\\\"}]\",
    \"optionsJSON\": \"{\\\"useMargins\\\":true,\\\"syncColors\\\":false,\\\"syncCursor\\\":true,\\\"syncTooltips\\\":false,\\\"hidePanelTitles\\\":false}\",
    \"version\": 1,
    \"timeRestore\": true,
    \"timeFrom\": \"now-24h\",
    \"timeTo\": \"now\",
    \"kibanaSavedObjectMeta\": {
      \"searchSourceJSON\": \"{\\\"query\\\":{\\\"language\\\":\\\"kuery\\\",\\\"query\\\":\\\"\\\"},\\\"filter\\\":[]}\"
    }
  },
  \"references\": [
    {
      \"name\": \"panel_panel_logs\",
      \"type\": \"search\",
      \"id\": \"${SEARCH_ID}\"
    }
  ]
}" >/dev/null

echo "Setting Kibana default route to dashboard..."
kbn -X POST "${KIBANA_URL}/api/kibana/settings" \
  -d "{\"changes\":{\"defaultRoute\":\"/app/dashboards#/view/${DASHBOARD_ID}\"}}" >/dev/null

echo "Kibana ready: dashboard '${DASHBOARD_ID}' is the default landing page."
