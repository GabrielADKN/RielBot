import requests
from bs4 import BeautifulSoup
from shortlink import shortlink


def get_bing_link(query):
    try:
        url = "https://www.bing.com/search?q=" + query
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"
        }

        links = []
        r = requests.get(url=url, headers=headers)

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            balise_a = soup.findAll("li", attrs={"class": "b_algo"})

            for a in balise_a:
                link = a.a["href"]
                links.append(link)

            all_links = (
                "<br><br><b> Some links that might help you: </b><br>"
                + "<a href='"
                + shortlink(links[0])
                + "' target='_blank'>"
                + shortlink(links[0])
                + "</a><br>"
                + "<a href='"
                + shortlink(links[1])
                + "' target='_blank'>"
                + shortlink(links[1])
                + "</a><br>"
                + "<a href='"
                + shortlink(links[2])
                + "' target='_blank'>"
                + shortlink(links[2])
                + "</a><br>"
                + "<a href='"
                + shortlink(links[3])
                + "' target='_blank'>"
                + shortlink(links[3])
                + "</a>"
            )
            return all_links
        else:
            return ''
    except Exception as e:
        print(e)
        return ''

def other_questions(query):
    try :
        lien_recherche = 'https://www.bing.com/search?q='
        lien = lien_recherche + query + ' +&qs=n&form=QBRE'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43'}
        response = requests.get(url=lien, headers=headers)
        if (response.ok):
            soup = BeautifulSoup(response.text, 'lxml')
            balises_alsocon = soup.findAll('span', {'class': 'df_alsocon'})
            balises_qntext = soup.findAll('div', {'class': 'df_qntext'})

            autre = "<br><br><i> Other questions : </i>"
            autre = autre + "<br><b>" + balises_qntext[0].text + "</b> : " + balises_alsocon[0].text
            autre = autre + "<br><b>" + balises_qntext[1].text + "</b> : " + balises_alsocon[1].text
            return autre
        else:
            return ''
    except Exception:
        return ''

# print(get_bing_link("how to grow rice"))
# print("-----------------------------------------------------")
# print(other_questions("how to grow rice"))