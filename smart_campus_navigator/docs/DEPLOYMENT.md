# Hosting deployment

## Prepared target: Render web service

The repository-root `render.yaml` defines a free Python web service named
`smart-campus-navigator`. It installs the four tested direct dependency versions,
starts the original Streamlit app on the host-provided PORT, and checks
`/_stcore/health`. No database, secret, authentication system or paid plan is
configured. Automatic deploys are disabled so publishing remains explicit.

The deployment uses the original Python algorithms and UI. It does not replace
Streamlit with a separate web implementation. Streamlit needs a Python server
and WebSocket support. A regular long-running web-service host fits its
session-state behavior.

## Source layout

Repository: https://github.com/staymotivated24rr-bot/DAA_project

Blueprint location: `render.yaml` at repository root.
Application root: `smart_campus_navigator`.

The source files and blueprint must be committed and pushed before Render can
build from Git. Preparing these files locally does not mean the remote Git
repository has been updated or the service has been deployed.

## Deployment access

Render is connected. The user confirmed Rakshith's workspace and the free plan.
The source is being published before service creation. A public deployment is
complete only after Render reports live and the application has been checked.
The connected Render account also needs access to the source GitHub repository.

Once account access is available, publish the project source, create the web
service from this blueprint, wait for its build, and verify the public service:

1. `/_stcore/health` returns HTTP 200.
2. Dashboard shows ten locations and seventeen paths.
3. Main Gate → Hostel shows 830 m.
4. Prim and Kruskal show 1690 m with nine selected edges.
5. Next/Previous/Reset controls work over the public WebSocket connection.
6. A temporary shortcut changes the route and Restore returns it to 830 m.

## Hosting behavior

A free Render service can sleep while idle and has a cold start when reopened.
Availability and quotas depend on the account and provider. Browser-session graph
edits are temporary; a server restart can clear them. For an examiner, open the
public URL before the demonstration and keep the offline Windows copy as a
backup. No paid plan or billing upgrade is authorized or required by this
configuration.
