from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_tags(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        tags = soup.find_all("a", class_="app_tag")
        return ", ".join([t.text.strip() for t in tags[:8]])
    except:
        return "нет тегов"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search():

    query = request.args.get("q", "")
    page = int(request.args.get("page", 1))

    max_price = request.args.get("max_price")
    tag_filter = request.args.get("tag")

    try:
        max_price = float(max_price) if max_price else None
    except:
        max_price = None

    url = f"https://store.steampowered.com/search/?term={query}&page={page}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    games = soup.find_all("a", class_="search_result_row")

    results = []

    for game in games:

        title = game.find("span", class_="title")
        title = title.text.strip() if title else "нет"

        link = game.get("href")

        price_tag = game.find("div", class_="discount_final_price")
        if not price_tag:
            price_tag = game.find("div", class_="search_price")

        price = price_tag.text.strip() if price_tag else "Free"

        discount_tag = game.find("div", class_="discount_pct")
        discount = discount_tag.text.strip() if discount_tag else "0%"

        tags = get_tags(link)

        # фильтр тегов
        if tag_filter and tag_filter.lower() not in tags.lower():
            continue

        # фильтр цены
        if max_price is not None:
            num = ""
            for c in price:
                if c.isdigit() or c == ".":
                    num += c

            if num:
                try:
                    if float(num) > max_price:
                        continue
                except:
                    pass

        results.append({
            "title": title,
            "link": link,
            "price": price,
            "discount": discount,
            "tags": tags
        })

    return jsonify({
        "count": len(results),
        "games": results
    })


import random

@app.route("/random")
def random_games():

    max_price = request.args.get("max_price")
    tag_filter = request.args.get("tag")

    try:
        max_price = float(max_price) if max_price else None
    except:
        max_price = None

    url = "https://store.steampowered.com/search/?term=&page=1"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    games = soup.find_all("a", class_="search_result_row")

    results = []

    for game in games:

        title = game.find("span", class_="title")
        title = title.text.strip() if title else "нет"

        link = game.get("href")

        price_tag = game.find("div", class_="discount_final_price")
        if not price_tag:
            price_tag = game.find("div", class_="search_price")

        price = price_tag.text.strip() if price_tag else "Free"

        discount_tag = game.find("div", class_="discount_pct")
        discount = discount_tag.text.strip() if discount_tag else "0%"

        tags = get_tags(link)

        # фильтр тегов
        if tag_filter and tag_filter.lower() not in tags.lower():
            continue

        # фильтр цены
        if max_price is not None:
            num = ""
            for c in price:
                if c.isdigit() or c == ".":
                    num += c

            if num:
                try:
                    if float(num) > max_price:
                        continue
                except:
                    pass

        results.append({
            "title": title,
            "link": link,
            "price": price,
            "discount": discount,
            "tags": tags
        })

    random.shuffle(results)

    return jsonify({
        "count": len(results),
        "games": results[:20]
    })

if __name__ == "__main__":
    app.run(debug=True)
