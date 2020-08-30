# Example 4-14. Code for the news scraper

# To obtain and run the Splash container, run these commands in
# your shell:
# 	$ docker pull scrapinghub/splash
# 	$ docker run --rm -p 8050:8050 scrapinghub/splash
# Our server backend will call the Splash API at http://localhost:8050.

# Run: python news_scraper.py
# and go to http://0.0.0.0:8080/news

import os

from asyncio import gather, create_task
from string import Template
from aiohttp import web, ClientSession
from bs4 import BeautifulSoup

INDEX_HTML_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(
    __file__)), '../../appendixB/2/index.html')


# The news() function is the handler for the /news URL on our server. It
# returns the HTML page showing all the headlines.
async def news(request):
    sites = [
        # Here, we have only two news websites to be scraped: CNN and
        # Al Jazeera. More could easily be added, but then additional
        # postprocessors would also have to be added, just like the
        # cnn_articles() and aljazeera_articles() functions that are
        # customized to extract headline data.
        ('http://edition.cnn.com', cnn_articles),
        ('http://www.aljazeera.com', aljazeera_articles),
    ]
    # For each news site, we create a task to fetch and process the HTML page
    # data for its front page. Note that we unpack the tuple ( (*s) ) since
    # the news_fetch() coroutine function takes both the URL and the
    # postprocessing function as parameters. Each news_fetch() call will
    # return a list of tuples as headline results, in the form
    # <article URL>, <article title>.
    tasks = [create_task(news_fetch(*s)) for s in sites]
    # All the tasks are gathered together into a single Future (gather()
    # returns a future representing the state of all the tasks being
    # gathered), and then we immediately await the completion of that future.
    # This line will suspend until the future completes.
    await gather(*tasks)

    # Since all the news_fetch() tasks are now complete, we collect all of the
    # results into a dictionary. Note how nested comprehensions are used to
    # iterate over tasks, and then over the list of tuples returned by each
    # task. We also use f-strings to substitute data directly, including even
    # the kind of page, which will be used in CSS to color the div background.
    items = {
        # In this dictionary, the key is the headline title, and the value is
        # an HTML string for a div that will be displayed in our result page.
        text: (
            f'<div class="box {kind}">'
            f'<span>'
            f'<a href="{href}">{text}</a>'
            f'</span>'
            f'</div>'
        )
        for task in tasks for href, text, kind in task.result()
    }
    content = ''.join(items[x] for x in sorted(items))
    # Our web server is going to return HTML. We’re loading HTML data from a
    # local file called index.html. This file is presented in Example B-1 if
    # you want to recreate the case study yourself.
    page = Template(open(INDEX_HTML_FILE_PATH).read())
    return web.Response(
        # We substitute the collected headline div into the template and
        # return the page to the browser client.
        body=page.safe_substitute(body=content),
        content_type='text/html',
    )


async def news_fetch(url, postprocess):
    # Here, inside the news_fetch() coroutine function, we have a tiny
    # template for hitting the Splash API (which, for me, is running in a
    # local Docker container on port 8050). This demonstrates how aiohttp can
    # be used as an HTTP client.
    proxy_url = (
        f'http://localhost:8050/render.html?'
        f'url={url}&timeout=60&wait=1'
    )
    async with ClientSession() as session:
        # The standard way is to create a ClientSession() instance, and then
        # use the get() method on the session instance to perform the REST
        # call. In the next line, the response data is obtained. Note that
        # because we’re always operating on coroutines, with async with and
        # await, this coroutine will never block: we’ll be able to handle many
        # thousands of these requests, even though this operation
        # (news_fetch()) might be relatively slow since we’re doing web calls
        # internally.
        async with session.get(proxy_url) as resp:
            data = await resp.read()
            data = data.decode('utf-8')
        # After the data is obtained, we call the postprocessing function. For
        # CNN, it’ll be cnn_articles(), and for Al Jazeera it’ll be
        # aljazeera_articles().
    return postprocess(url, data)


# We have space only for a brief look at the postprocessing. After getting the
# page data, we use the Beautiful Soup 4 library for extracting headlines.
def cnn_articles(url, page_data):
    soup = BeautifulSoup(page_data, 'lxml')

    def match(tag):
        return (
            tag.text and tag.has_attr('href')
            and tag['href'].startswith('/')
            and tag['href'].endswith('.html')
            # and tag.find(class_='cd__headline-text')
        )
        # The match() function will return all matching tags (I’ve manually
        # checked the HTML source of these news websites to figure out which
        # combination of filters extracts the best tags), and then we return
        # a list of tuples matching the format <article URL> , <article title>.
    headlines = soup.find_all(match)
    return [(url + hl['href'], hl.text, 'cnn')
            for hl in headlines]


# This is the analogous postprocessor for Al Jazeera. The match() condition is
# slightly different, but it is otherwise the same as the CNN one.
def aljazeera_articles(url, page_data):
    soup = BeautifulSoup(page_data, 'lxml')

    def match(tag):
        return (
            tag.text and tag.has_attr('href')
            and tag['href'].startswith('/news')
            and tag['href'].endswith('.html')
        )
    headlines = soup.find_all(match)
    return [(url + hl['href'], hl.text, 'aljazeera')
            for hl in headlines]


app = web.Application()
app.router.add_get('/news', news)
web.run_app(app, port=8080)
