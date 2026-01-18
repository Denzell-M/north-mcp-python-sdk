# WISE North MCP Workshop — Quickstart (Recommended)

This directory contains **example MCP servers** you can run and register into **North**.

> If you came here looking for `import north` / `north.Client(...).chat(...)`: that is **not** used in this repo.
> This repo is for building **MCP servers** using `north_mcp_python_sdk.NorthMCPServer`.

## Fastest path: run the working demo server

We included a minimal, known-good server at:

- `my_mcp_server.py`

It exposes a few calculator tools and is set up to avoid the most common North issue: **tool name collisions**.

### 0) One-time setup

```bash
# clone this repo
git clone https://github.com/cohere-ai/north-mcp-python-sdk.git
cd north-mcp-python-sdk

# switch to the WISE branch
git switch wise_2026_conference

# enter examples
cd wise_examples

# install dependencies
uv sync
```

### 1) Run the server locally

Pick a unique tool prefix (must be globally unique in North):

```bash
export TOOL_PREFIX="yourname_yourlastname"  # e.g. denzell_twerdohl_lib
export MCP_PORT=3001

uv run python my_mcp_server.py
```

Leave this terminal running.

### 2) Expose the server publicly (ngrok)

In a new terminal:

```bash
ngrok http 3001
```

Copy the **https** Forwarding URL (example):

- `https://abc123.ngrok-free.app`

### 3) Register the server in North

1. Get your North token here:
   - https://gtxcc.democloud.cohere.com/developer/python

2. Export variables (use your ngrok URL **without** `/mcp`):

```bash
export NORTH_TOKEN="<paste your north token>"
export HOST="https://gtxcc.democloud.cohere.com/api"
export URL="https://abc123.ngrok-free.app"
```

3. Register:

```bash
curl --location "${HOST}/internal/v1/mcp_servers" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer ${NORTH_TOKEN}" \
  --data '{
    "url": "'"${URL}"'",
    "name": "My WISE MCP Server"
  }'
```

4. Open North and try your tools:
   - https://gtxcc.democloud.cohere.com/

### Notes / troubleshooting

- **Tool names must be unique**: that’s why `TOOL_PREFIX` exists.
- **Keep tokens secret**: don’t paste them into chat, screenshots, or public repos.

---

# Detailed walkthrough (cleaned up)

This section is a more explicit version of the original walkthrough, with less duplication and clearer “what goes where”.

## 1) Prerequisites

- **Python 3.11+**
- **uv**: <https://astral.sh/uv>
- **ngrok**: <https://ngrok.com/download>

### Install / configure ngrok (if you’ve never used it)

If `ngrok http <port>` fails with an “authtoken required” error, do:

1. Create an account: <https://dashboard.ngrok.com/signup>
2. Find your authtoken: <https://dashboard.ngrok.com/get-started/your-authtoken>
3. Configure it:

```bash
ngrok config add-authtoken $YOUR_AUTHTOKEN
```

## 2) Pick a starting server

You have three good starting points:

- **`my_mcp_server.py`** (recommended): minimal + already set up for unique tool names via `TOOL_PREFIX`
- **`simple_calculator.py`**: more tools + shows annotations like `destructiveHint`
- **`simple_calendar.py`**: Google Calendar example (requires Google OAuth token)

If you build your own server, copy one of these files and modify it.

## 3) Make tool names unique (important)

North requires tool names to be globally unique.

### Option A (recommended): use `TOOL_PREFIX`

`my_mcp_server.py` supports a prefix automatically:

```bash
export TOOL_PREFIX="first_last_project"   # must be unique
uv run python my_mcp_server.py
```

### Option B: rename your tool functions

In `simple_calculator.py` / `simple_calendar.py`, rename tool functions:

- from: `firstname_lastname_add`
- to: `denzell_twerdohl_lib_add`

## 4) Run the server locally

Run one of these:

```bash
# recommended demo
uv run python my_mcp_server.py

# or calculator example
uv run python simple_calculator.py

# or calendar example
uv run python simple_calendar.py
```

Each script declares a port near the top. Common defaults:

- calculator: `3001`
- calendar: `3002`

## 5) Expose the server via ngrok

In a second terminal:

```bash
ngrok http <port>
# e.g.
ngrok http 3001
```

You will get a public URL like:

- `https://abc123.ngrok-free.app`

## 6) Register / list / delete servers in North

### Get your North token

- https://gtxcc.democloud.cohere.com/developer/python

### Set environment variables

```bash
export NORTH_TOKEN="<north token>"
export HOST="https://gtxcc.democloud.cohere.com/api"
export URL="<ngrok https url>"  # IMPORTANT: do NOT add /mcp
```

### List registered servers

```bash
curl --location "${HOST}/internal/v1/mcp_servers" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer ${NORTH_TOKEN}"
```

### Register your server

```bash
curl --location "${HOST}/internal/v1/mcp_servers" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer ${NORTH_TOKEN}" \
  --data '{
    "url": "'"${URL}"'",
    "name": "My MCP Server"
  }'
```

### Delete a server

```bash
curl --location --request DELETE "${HOST}/internal/v1/mcp_servers/<server_id>" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer ${NORTH_TOKEN}"
```

### Open North

You must create a new account with the domain `wiseconference.com` to have access.

- https://gtxcc.democloud.cohere.com/

---

# Optional: Google Calendar connector (for `simple_calendar.py`)

`simple_calendar.py` talks to the Google Calendar API. For it to work, you need a Google OAuth access token.

## Quick version

1. Put your Google OAuth client credentials file at:
   - `wise_examples/client_secret.json`
2. Run the helper to get a Google access token:

```bash
uv run python get_google_access_token.py
```

3. Set the token as an environment variable (recommended):

```bash
export ACCESS_TOKEN="<google access token>"
uv run python simple_calendar.py
```

## Where do I get the OAuth Client ID/Secret?

Google’s official docs (recommended):
- <https://developers.google.com/workspace/guides/create-credentials>

High-level steps:

1. Go to <https://console.cloud.google.com>
2. Create/select a project
3. Enable **Google Calendar API**
4. Create **OAuth client ID** credentials
5. Download the JSON and save it as `client_secret.json` in this directory

---

# Troubleshooting

## “My tools don’t show up in North”

Most common causes:

- Tool names are not unique → set `TOOL_PREFIX` or rename the tool functions.
- Your server isn’t reachable publicly → confirm ngrok is running and you registered the **https** URL.

## “What URL do I register?”

Register the **base ngrok URL** (no `/mcp`). Example:

- ✅ `https://abc123.ngrok-free.app`
- ❌ `https://abc123.ngrok-free.app/mcp`

## “Port already in use”

Change the port in the script, or set one via env var if the script supports it.

For `my_mcp_server.py`:

```bash
export MCP_PORT=3005
uv run python my_mcp_server.py
```
