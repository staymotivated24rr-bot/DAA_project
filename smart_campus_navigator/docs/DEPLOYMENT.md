# Live deployment

Public application: https://smart-campus-navigator-7uls.onrender.com

Render dashboard: https://dashboard.render.com/web/srv-dbf43fqvcj2c73eou7e0

## Deployment record

- Workspace: Rakshith's workspace (explicitly confirmed by the user).
- Compute plan: free; no paid resources were created.
- Region: Singapore.
- Repository: https://github.com/staymotivated24rr-bot/DAA_project
- Branch: main.
- Deployed application commit: 4f462c9b5e6359856ca1527433d22d9d6d94e66f.
- Service ID: srv-dbf43fqvcj2c73eou7e0.
- Deploy ID: dep-dbf43gqvcj2c73eou990.
- Render reports `live`; finished at 2026-10-25 17:53:40 UTC.
- Automatic deployments are disabled. Later documentation-only commits do not change the running application.

The single service was created directly through the Render connection. The
repository-root render.yaml remains an alternative reproducible Blueprint; do
not apply it on top of this service without checking for duplicate provisioning.
The direct creation tool did not expose root-directory or HTTP-health-path
settings, so both commands explicitly enter the application folder and the
service uses Render's default TCP readiness checks.

## Commands used by the live service

Build:
```sh
cd smart_campus_navigator && python -m pip install -r requirements-tested.txt
```

Start:
```sh
cd smart_campus_navigator && exec python -m streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true
```

Python version: 3.12.14. No API key, database, login system or external data
service is required. Render supplies PORT; the startup log confirmed port 10000.

## Verification and limits

All 23 local algorithm and Streamlit integration tests passed before deployment.
Render built successfully, started Streamlit, passed readiness and reported the
deploy live. The execution environment blocks outbound requests to onrender.com
with proxy HTTP 403, so no public HTTP/browser flow test is claimed. Local
Chromium had already verified all six sections with external requests blocked.
Current Render documentation retrieval was also blocked; the connected tool's
actual schema and API responses were used for deployment configuration.

When opening the public URL, confirm Main Gate → Hostel gives 830 m and Prim /
Kruskal each give 1690 m with nine selected edges. Inspect step buttons and test
a temporary shortcut followed by Restore original graph.

A free Render service can sleep when idle, so the first visit may take longer.
Session graph changes are temporary and can disappear on server restart. Keep
the offline project as a classroom-demo backup.
