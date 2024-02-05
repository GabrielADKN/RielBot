import requests
from bs4 import BeautifulSoup
from shortlink import shortlink


def get_bing_link(query):
    try:
        url = "https://www.bing.com/search?q="
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"
        }

        links = []
        r = requests.get(url=url, headers=headers, params=params)

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            balise_a = soup.findAll("li", attrs={"class": "b_algo"})

            for a in balise_a:
                link = a.a["href"]
                links.append(link)
            all_links = ""

            if links:
                all_links = "<br><br><b> Some links that might help you: </b><br>"

                max_links = 3
                for link in links[:max_links]:
                    short_link = shortlink(link)
                    all_links += (
                        f"<a href='{short_link}' target='_blank'>{short_link}</a><br>"
                    )

            return all_links

        else:
            return ""
    except Exception as e:
        print(e)
        return ""


def other_questions(query):
    try:
        search_link = "https://www.bing.com/search"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43"
        }
        response = requests.get(url=search_link, headers=headers, params=params)
        if response.ok:
            soup = BeautifulSoup(response.text, "lxml")
            tags_alsocon = soup.findAll("span", {"class": "df_alsocon"})
            tags_qntext = soup.findAll("div", {"class": "df_qntext"})

            autre = "<br><br><i> Other questions : </i>"
            autre = (
                autre
                + "<br><b>"
                + tags_qntext[0].text
                + "</b> : "
                + tags_alsocon[0].text
            )
            autre = (
                autre
                + "<br><b>"
                + tags_qntext[1].text
                + "</b> : "
                + tags_alsocon[1].text
            )
            return autre
        else:
            return ""
    except Exception:
        return ""
