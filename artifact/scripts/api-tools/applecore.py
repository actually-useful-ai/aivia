import logging
import requests
from flask import Flask, request, redirect, render_template_string
from bs4 import BeautifulSoup

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

HTML_FORM = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Apple News Redirector</title>
  <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
</head>
<body style="font-family: Arial, sans-serif; margin: 40px;">
  <h1>Apple News Redirector</h1>
  <p>Enter an Apple News link. We’ll fetch the real source URL, then prepend 12ft.io for paywall bypass.</p>
  <form method="post">
    <input type="text" name="link" placeholder="Enter Apple News link" style="width: 400px; padding: 8px;">
    <button type="submit" style="padding: 8px 12px;">Go</button>
  </form>
  {% if error %}
    <p style="color:red;">{{ error }}</p>
  {% endif %}
</body>
</html>
"""

def extract_original_url(apple_news_url):
    """Fetches Apple News link and tries to parse out the original article URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    try:
        resp = requests.get(apple_news_url, headers=headers, timeout=10)
        if resp.url and "apple.news" not in resp.url:
            logging.info("Extracted original from redirect: %s", resp.url)
            return resp.url
        
        # Otherwise parse HTML for anchor or meta refresh
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith("http") and "apple.news" not in href:
                logging.info("Found original URL in anchor: %s", href)
                return href

        meta = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta:
            content = meta.get('content', '')
            if "URL=" in content:
                parts = content.split("URL=")
                if len(parts) > 1:
                    candidate = parts[1].strip()
                    if candidate.startswith("http") and "apple.news" not in candidate:
                        logging.info("Found original URL in meta refresh: %s", candidate)
                        return candidate
    except Exception as e:
        logging.error("Error extracting original URL: %s", e)
    return None

def check_proxy_for_block(proxy_url):
    """
    Fetch entire HTML from 12ft.io and look for 'Please enable JS and disable any ad blocker' or
    any similar text. Also logs first ~4000 chars for debugging.
    """
    try:
        resp = requests.get(proxy_url, timeout=10)
        # If non-200, treat as an error
        if resp.status_code != 200:
            logging.info("Proxy returned non-200 status: %s", resp.status_code)
            return True
        
        # Grab entire text
        content = resp.text
        # Log first chunk for debugging
        snippet = content[:4000]
        logging.info("First 4000 chars of proxy response:\n%s\n", snippet)

        # Normalize
        text_lower = " ".join(content.split()).lower()
        # Some possible phrases
        keywords = [
            "please enable js and disable any ad blocker",
            "enable javascript to run this app",
            "disable adblock to proceed",
            "disable any ad blocker",
            "please enable javascript",
            "please disable adblock",
            "turn off your ad blocker",
        ]
        for kw in keywords:
            if kw in text_lower:
                logging.info("Detected keyword '%s' in proxy HTML => block", kw)
                return True
    except Exception as e:
        logging.error("Error fetching proxy: %s", e)
        return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        link = request.form.get('link', '').strip()
        if not link or "apple.news" not in link:
            error = "Please enter a valid Apple News link."
            return render_template_string(HTML_FORM, error=error)
        
        original = extract_original_url(link)
        if not original:
            error = ("Could not extract the original URL from that Apple News link. "
                     "It may be an unsupported link.")
            return render_template_string(HTML_FORM, error=error)
        
        # Construct 12ft.io link
        new_url = "https://12ft.io/" + original
        logging.info("Constructed 12ft.io URL: %s", new_url)
        
        # Check for JS/adblock block
        if check_proxy_for_block(new_url):
            error = ("12ft.io says 'Please enable JS and disable any ad blocker'. "
                     "It may not serve the article in this browser or with your current ad-block settings.")
            return render_template_string(HTML_FORM, error=error)
        
        logging.info("Redirecting user to: %s", new_url)
        return redirect(new_url)
    
    return render_template_string(HTML_FORM, error=error)

if __name__ == '__main__':
    app.run(debug=True)