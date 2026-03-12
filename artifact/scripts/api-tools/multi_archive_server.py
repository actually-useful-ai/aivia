from flask import Flask, request, redirect, render_template_string
import requests
from waybackpy.cdx_api import CDXApi as WaybackMachineCDXServerAPI
import archiveis
import urllib.parse

app = Flask(__name__)

# Define a User-Agent string to mimic a real browser
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/90.0.4430.93 Safari/537.36"
)

# HTML template for the index page
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Archived Version Finder</title>
</head>
<body>
    <h1>Archived Version Finder</h1>
    <p>Enter a URL and select an archive provider to find its most recent archived version:</p>
    <form action="/search" method="post">
        <input type="url" name="url" placeholder="https://example.com" required style="width:300px; padding:5px;"><br><br>
        <label for="provider">Select Archive Provider:</label>
        <select name="provider">
            <option value="wayback">Internet Archive (Wayback Machine)</option>
            <option value="archiveis">Archive.is</option>
            <option value="memento">Memento Aggregator</option>
        </select><br><br>
        <button type="submit" style="padding:5px 10px;">Find Archive</button>
    </form>
</body>
</html>
"""

def get_wayback_snapshot(target_url):
    """Retrieve the most recent snapshot from the Wayback Machine."""
    try:
        cdx = WaybackMachineCDXServerAPI(target_url, USER_AGENT)
        snapshot = cdx.newest()
        return snapshot.archive_url
    except Exception as e:
        raise Exception(f"Wayback Machine API error: {e}")

def get_archiveis_snapshot(target_url):
    """Capture the current state of the URL using Archive.is."""
    try:
        archived_url = archiveis.capture(target_url)
        return archived_url
    except Exception as e:
        raise Exception(f"Archive.is error: {e}")

def get_memento_snapshot(target_url):
    """Retrieve the most recent snapshot using the Memento Aggregator."""
    encoded_url = urllib.parse.quote(target_url, safe="")
    api_url = f"http://timetravel.mementoweb.org/timemap/json/{encoded_url}"
    try:
        response = requests.get(api_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        response.raise_for_status()
        data = response.json()
        mementos = data.get("mementos", {}).get("list", [])
        if mementos:
            return mementos[-1].get("uri")
        else:
            return None
    except Exception as e:
        raise Exception(f"Memento Aggregator error: {e}")

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)

@app.route("/search", methods=["POST"])
def search_archive():
    target_url = request.form.get("url")
    provider = request.form.get("provider", "wayback")

    if not target_url:
        return "Error: No URL provided", 400

    try:
        if provider == "wayback":
            archived_url = get_wayback_snapshot(target_url)
        elif provider == "archiveis":
            archived_url = get_archiveis_snapshot(target_url)
        elif provider == "memento":
            archived_url = get_memento_snapshot(target_url)
        else:
            return "Error: Unknown provider selected", 400

        if archived_url:
            return redirect(archived_url)
        else:
            return f"No archived version found via {provider}.", 404

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(debug=True, port=5097) 