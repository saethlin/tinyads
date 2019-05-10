import os
import html
import requests
from flask import Flask, Response, request


ads_token = os.environ['ADS_TOKEN']

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def get_page():
    query = request.args.get('adsquery')

    output = '''<style>
body {
    margin:1em auto;
    max-width:40em;
    padding:0 .62em;
    font:20px/26px sans-serif;
    line-height: 1.0;
}
h1,h2,h3 {
    line-height:1.2;
}
h4 {
    line-height:1.0;
    margin-bottom:0.25em;
}
p {
    margin: 0.4em 0 0 0;
    padding: 0;
}
@media print {
    body{
        max-width:none
    }
}
</style>

<form action="/">
<center>
Search ADS:
<input type="text" name="adsquery" style="width: 40em; font:18px sans-serif;"><br>
</center>
</form>\n'''

    if query:
        headers = {"Authorization": f"Bearer {ads_token}"}

        params = {
            "q": query,
            "fl": "author,title,bibcode,pubdate,doi",
            "fq": "database:astronomy",
        }

        response = requests.get(
            "https://api.adsabs.harvard.edu/v1/search/query?sort=pubdate+desc",
            headers=headers,
            params=params,
        )
        response = response.json()


        output += f'<h3>ADS query results for "{query}"</h3>\n'

        for article in response["response"]["docs"]:
            title = html.unescape(article["title"][0])
            raw_authors = article["author"]
            authors = "; ".join(html.unescape(a) for a in raw_authors[:4])
            if len(raw_authors) > 3:
                authors += f' and {len(raw_authors) - 3} more'
            bibcode = article['bibcode']
            url = f"https://ui.adsabs.harvard.edu/abs/{bibcode}/abstract"
            date = '/'.join(article["pubdate"].split('-')[:2])
            doi = article.get('doi', [])
            if doi:
                doi = doi[0]

            output += f'<h4>{title}</h4>\n'
            output += f'<p>{authors}\n'
            output += f'<p><a href="{url}">{bibcode}</a>\n'
            if doi:
                output += f'<p><a href="https://doi.org/{doi}">{doi}</a>\n'
            output += '\n'
            #f.write('<a href="">BibTeX for this abstract</a><br>\n')

    return Response(output, mimetype="text/html")

app.run(port=80, host='0.0.0.0')