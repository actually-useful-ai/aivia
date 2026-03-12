import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

class Drummer:
    def __init__(self, username):
        self.username = str(username).strip()
        self.networks = {
            "facebook.com": "https://www.facebook.com/",
            "twitter.com": "https://twitter.com/",
            "instagram.com": "https://www.instagram.com/",
            "linkedin.com": "https://www.linkedin.com/in/",
            "github.com": "https://github.com/",
            "twitch.tv": "https://www.twitch.tv/",
            "reddit.com": "https://www.reddit.com/user/",
            "pinterest.com": "https://www.pinterest.com/",
            "tumblr.com": "https://www.tumblr.com/blog/view/",
            "flickr.com": "https://www.flickr.com/people/",
            "soundcloud.com": "https://soundcloud.com/",
            "snapchat.com": "https://www.snapchat.com/add/",
            "vimeo.com": "https://vimeo.com/",
            "medium.com": "https://medium.com/@",
            "discord.com": "https://discord.com/users/",
            "steamcommunity.com": "https://steamcommunity.com/id/",
            "behance.net": "https://www.behance.net/",
            "dribbble.com": "https://dribbble.com/",
            "quora.com": "https://www.quora.com/profile/",
            "pixiv.net": "https://www.pixiv.net/en/users/",
            "open.spotify.com": "https://open.spotify.com/user/",
            "tiktok.com": "https://www.tiktok.com/@",
            "youtube.com": "https://www.youtube.com/@",
            "clubhouse.com": "https://www.clubhouse.com/@",
            "epicgames.com": "https://www.epicgames.com/id/",
            "telegram.org": "https://t.me/",
            "rumble.com": "https://rumble.com/user/",
            "parler.com": "https://parler.com/user/",
            "gab.com": "https://gab.com/",
            "odyssee.com": "https://odysee.com/@"
        }
        self.results = []

    def check_account(self, network, base_url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"{base_url}{self.username}"
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                if self.verify_account_exists(network, response):
                    return {"platform": network, "status": "Exists", "url": url}
                else:
                    return {"platform": network, "status": "Does not exist", "url": None}
            else:
                return {"platform": network, "status": "Does not exist", "url": None}
        except requests.exceptions.RequestException as e:
            return {"platform": network, "status": "Error", "message": str(e), "url": None}

    def verify_account_exists(self, network, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if network == "twitter.com":
            return "This account doesn’t exist" not in soup.text
        elif network == "instagram.com":
            return "Sorry, this page isn't available." not in soup.text and "content not available" not in response.text.lower()
        elif network == "facebook.com":
            return "The link you followed may be broken" not in soup.text and "content isn't available" not in soup.text
        elif network == "linkedin.com":
            return "Profile Not Found" not in soup.text
        elif network == "github.com":
            return "Page not found" not in soup.text
        elif network == "tiktok.com":
            return "Couldn't find this account" not in soup.text and "couldn't find" not in response.text.lower()
        elif network == "twitch.tv":
            # Improve Twitch check by looking for a specific meta tag that indicates a user does not exist
            return "content is unavailable" not in soup.text.lower() and "no longer available" not in soup.text.lower()
        elif network == "telegram.org":
            return "If you have Telegram, you can contact" in soup.text and "start messaging" not in response.text.lower()
        elif network == "medium.com":
            return "Medium member page" in soup.text
        elif network == "reddit.com":
            return "Sorry, nobody on Reddit goes by that name." not in soup.text
        elif network == "snapchat.com":
            return "Could not find that username." not in soup.text
        elif network == "youtube.com":
            return "This channel does not exist." not in soup.text
        else:
            # Fallback: check if username appears anywhere in the page source
            return self.username.lower() in response.text.lower()

    def check_accounts(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_network = {executor.submit(self.check_account, network, base_url): network for network, base_url in self.networks.items()}
            for future in as_completed(future_to_network):
                network = future_to_network[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as exc:
                    self.results.append({"platform": network, "status": "Error", "message": str(exc), "url": None})

    def display_results(self):
        if not any(result["status"] == "Exists" for result in self.results):
            return {"message": "No accounts found for the username.", "results": []}
        return {"message": "Accounts found for the username.", "results": self.results}

def handler(args):
    username_to_check = args.input.username_to_check
    drummer = Drummer(username_to_check)
    drummer.check_accounts()
    return drummer.display_results()

if __name__ == "__main__":
    handler(args)
    
    
    
    
    
    FINAL aug 16 - being replaced -
    
    import requests
import logging
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SherlockDrummer:
    def __init__(self, username):
        self.username = str(username).strip()
        self.results = []
        self.platforms = self.get_platforms()

    def get_platforms(self):
        # Extended list of platforms from Sherlock
        return {
            "GitHub": f"https://github.com/{self.username}",
            "Instagram": f"https://www.instagram.com/{self.username}/",
            "Twitter": f"https://twitter.com/{self.username}",
            "Facebook": f"https://www.facebook.com/{self.username}",
            "Reddit": f"https://www.reddit.com/user/{self.username}",
            "LinkedIn": f"https://www.linkedin.com/in/{self.username}",
            "Tumblr": f"https://{self.username}.tumblr.com",
            "YouTube": f"https://www.youtube.com/@{self.username}",
            "Bluesky": f"https://bsky.app/profile/{self.username}.bsky.social",
            "TikTok": f"https://www.tiktok.com/@{self.username}",
            "Snapchat": f"https://www.snapchat.com/add/{self.username}",
            "Medium": f"https://medium.com/@{self.username}",
            "Vimeo": f"https://vimeo.com/{self.username}",
            "SoundCloud": f"https://soundcloud.com/{self.username}",
            "Twitch": f"https://www.twitch.tv/{self.username}",
            "Dribbble": f"https://dribbble.com/{self.username}",
            "Behance": f"https://www.behance.net/{self.username}",
            "Flickr": f"https://www.flickr.com/people/{self.username}",
            "DeviantArt": f"https://www.deviantart.com/{self.username}",
            "Goodreads": f"https://www.goodreads.com/{self.username}",
            "GitLab": f"https://gitlab.com/{self.username}",
            "Bitbucket": f"https://bitbucket.org/{self.username}",
            "Steam": f"https://steamcommunity.com/id/{self.username}",
            "Patreon": f"https://www.patreon.com/{self.username}",
            "Ko-fi": f"https://ko-fi.com/{self.username}",
            "BuyMeACoffee": f"https://www.buymeacoffee.com/{self.username}",
            "AngelList": f"https://angel.co/{self.username}",
            "ProductHunt": f"https://www.producthunt.com/@{self.username}",
            "500px": f"https://500px.com/{self.username}",
            "About.me": f"https://about.me/{self.username}",
            "WordPress": f"https://{self.username}.wordpress.com",
            "Blogspot": f"https://{self.username}.blogspot.com",
            "LiveJournal": f"https://{self.username}.livejournal.com",
            "VK": f"https://vk.com/{self.username}",
            "OK": f"https://ok.ru/{self.username}",
            "Weibo": f"https://weibo.com/{self.username}",
            "Douban": f"https://www.douban.com/people/{self.username}",
            "Zhihu": f"https://www.zhihu.com/people/{self.username}",
            "Quora": f"https://www.quora.com/profile/{self.username}",
            "Mix": f"https://mix.com/{self.username}",
            "Ello": f"https://ello.co/{self.username}",
            "Myspace": f"https://myspace.com/{self.username}",
            "Badoo": f"https://badoo.com/en/{self.username}",
            "Meetup": f"https://www.meetup.com/members/{self.username}",
            "Xing": f"https://www.xing.com/profile/{self.username}",
            "Kaggle": f"https://www.kaggle.com/{self.username}",
            "ResearchGate": f"https://www.researchgate.net/profile/{self.username}",
            "Academia": f"https://independent.academia.edu/{self.username}",
            "Scribd": f"https://www.scribd.com/{self.username}",
            "Slideshare": f"https://www.slideshare.net/{self.username}",
            "Scoop.it": f"https://www.scoop.it/u/{self.username}",
            "Disqus": f"https://disqus.com/by/{self.username}",
            "Gravatar": f"https://en.gravatar.com/{self.username}",
            "Keybase": f"https://keybase.io/{self.username}",
            "Last.fm": f"https://www.last.fm/user/{self.username}",
            "Bandcamp": f"https://bandcamp.com/{self.username}",
            "ReverbNation": f"https://www.reverbnation.com/{self.username}",
            "Mixcloud": f"https://www.mixcloud.com/{self.username}",
            "8tracks": f"https://8tracks.com/{self.username}",
            "Audiomack": f"https://audiomack.com/{self.username}",
            "DatPiff": f"https://www.datpiff.com/profile/{self.username}",
            "Gumroad": f"https://gumroad.com/{self.username}",
            "Payhip": f"https://payhip.com/{self.username}",
            "Teespring": f"https://teespring.com/stores/{self.username}",
            "Redbubble": f"https://www.redbubble.com/people/{self.username}",
            "Society6": f"https://society6.com/{self.username}",
            "Zazzle": f"https://www.zazzle.com/{self.username}",
            "CafePress": f"https://www.cafepress.com/profile/{self.username}",
            "Threadless": f"https://www.threadless.com/@{self.username}",
            "DesignByHumans": f"https://www.designbyhumans.com/shop/{self.username}",
            "Spreadshirt": f"https://www.spreadshirt.com/user/{self.username}",
            "Storenvy": f"https://{self.username}.storenvy.com",
            "BigCartel": f"https://{self.username}.bigcartel.com",
            "Etsy": f"https://www.etsy.com/shop/{self.username}",
            "ArtStation": f"https://www.artstation.com/{self.username}"
        }

    def check_platform(self, platform_name, url):
        logging.info(f"Checking {platform_name} for username '{self.username}' at {url}")
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code == 200:
                if platform_name in ["GitHub", "Twitter", "Facebook", "Reddit", "LinkedIn", "Tumblr", "YouTube"]:
                    if self.username in response.text:
                        self.results.append({"platform": platform_name, "status": "Exists", "url": url})
                    else:
                        self.results.append({"platform": platform_name, "status": "Does not exist", "url": None})
                elif platform_name == "Instagram":
                    soup = BeautifulSoup(response.text, 'html.parser')
                    username_element = soup.find('meta', attrs={'name': 'description'})
                    if username_element and username_element.get('content') and self.username in username_element['content']:
                        self.results.append({"platform": platform_name, "status": "Exists", "url": url})
                    else:
                        self.results.append({"platform": platform_name, "status": "Does not exist", "url": None})
                else:
                    self.results.append({"platform": platform_name, "status": "Exists", "url": url})
            else:
                self.results.append({"platform": platform_name, "status": "Does not exist", "url": None})
        except requests.exceptions.RequestException as e:
            logging.error(f"Error checking {platform_name}: {e}")
            self.results.append({"platform": platform_name, "status": "Error", "message": str(e), "url": None})

    def check_accounts(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_platform = {executor.submit(self.check_platform, platform, url): platform for platform, url in self.platforms.items()}
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    result = future.result()
                    if result is not None:
                        self.results.append(result)
                except Exception as exc:
                    self.results.append({"platform": platform, "status": "Error", "message": str(exc), "url": None})

    def display_results(self):
        valid_results = [result for result in self.results if result is not None]
        if not any(result["status"] == "Exists" for result in valid_results):
            return {"message": "No accounts found for the username.", "results": []}
        return {"message": "Accounts found for the username.", "results": valid_results}

# Coze handler function
def handler(args):
    logging.info("Handler called with args: %s", args)
    
    if not hasattr(args, 'input'):
        logging.error("Error: args does not have an 'input' attribute.")
        return {"message": "Invalid input structure: 'input' attribute missing.", "results": []}

    if args.input is None:
        logging.error("Error: args.input is None.")
        return {"message": "Invalid input structure: 'input' is None.", "results": []}

    if isinstance(args.input, dict):
        input_dict = args.input
    elif hasattr(args.input, '__dict__'):
        input_dict = vars(args.input)
    else:
        logging.error("Error: args.input is of an unsupported type: %s", type(args.input))
        return {"message": f"Invalid input structure: expected dict, got {type(args.input)}.", "results": []}

    username_to_check = input_dict.get("username_to_check")
    if not username_to_check:
        logging.error("Error: Username is required.")
        return {"message": "Username is required.", "results": []}

    drummer = SherlockDrummer(username_to_check)
    drummer.check_accounts()
    return drummer.display_results()
