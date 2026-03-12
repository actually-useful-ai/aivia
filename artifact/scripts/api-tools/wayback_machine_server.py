from flask import Flask, request, redirect, render_template_string
from waybackpy.cdx_api import CDXApi as WaybackMachineCDXServerAPI

app = Flask(__name__)

# HTML template for the index page
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Wayback Machine Redirector</title>
</head>
<body>
    <h1>Wayback Machine Redirector</h1>
    <p>Enter a URL to find its most recent archived version:</p>
    <form action="/search" method="post">
        <input type="url" name="url" placeholder="https://example.com" required style="width:300px; padding:5px;">
        <button type="submit" style="padding:5px 10px;">Find Archive</button>
    </form>
</body>
</html>
"""

# Define a User-Agent string to mimic a real browser.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/90.0.4430.93 Safari/537.36")

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)

@app.route("/search", methods=["POST"])
def search_archive():
    target_url = request.form.get("url")
    if not target_url:
        return "Error: No URL provided", 400

    try:
        # Create a WaybackMachineCDXServerAPI instance for the target URL.
        wayback = WaybackMachineCDXServerAPI(target_url, USER_AGENT)
        # Retrieve the most recent snapshot.
        snapshot = wayback.newest()
        archive_url = snapshot.archive_url  # This property holds the archived URL.
    except Exception as e:
        return f"Error retrieving archive: {e}", 500

    if archive_url:
        return redirect(archive_url)
    else:
        return "No archived version found for the provided URL.", 404

if __name__ == "__main__":
    app.run(debug=True, port=5093)