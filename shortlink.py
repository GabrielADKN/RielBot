import pyshorteners
import requests

def shortlink(url):
    try:
        s = pyshorteners.Shortener()
        short = s.tinyurl.short(url)
        return short
    except requests.exceptions.ConnectionError:
        return "Check your connection"
    except requests.exceptions.MissingSchema:
        return "Invalid URL"
    except requests.exceptions.InvalidURL:
        return "Invalid URL"
    except requests.exceptions.InvalidSchema:
        return "Invalid URL"
    except requests.exceptions.InvalidHeader:
        return "Invalid URL"
    except requests.exceptions.InvalidProxyURL:
        return "Invalid URL"
    except requests.exceptions.InvalidURL:
        return "Invalid URL"
    except requests.exceptions.InvalidSchema:
        return "Invalid URL"
    except requests:
        return "Invalid URL"

# print(shortlink("https://www.google.com/search?q=hello&oq=hello&aqs=chrome..69i57j0i433j0i131i433j0i433j0i131i433j0i433j0i131i433j0i433l2j0i131i433.1003j0j7&sourceid=chrome&ie=UTF-8"))