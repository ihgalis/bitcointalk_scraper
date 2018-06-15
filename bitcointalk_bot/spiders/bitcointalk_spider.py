import scrapy
import hashlib
import re
from bitcointalk_bot.items import BitcointalkPost


class BitcointalkSpider(scrapy.Spider):
    name = "bitcointalk"

    start_urls = [
        'https://www.bitcointalk.org/',
    ]

    def parse(self, response):
        # subforums
        for board in response.css('div#bodyarea td.windowbg2 a::attr(href)').re(r'https:\/\/bitcointalk.org\/index.php\?board=[0-9]{1,}.0'):
            yield scrapy.Request(url=board, callback=self.parse_topics)

    def parse_topics(self, response):
        # load all topics
        topic_links = set(response.css('div.tborder a::attr(href)').re(r'https:\/\/bitcointalk.org\/index.php\?topic=[0-9]{1,}.0'))

        # iterate through pages
        try:
            next_page = response.css('span.prevnext a::attr(href)').extract()[1]
        except:
            next_page = None

        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse_topics)

        # iterate through all topics
        for topic_link in topic_links:
            yield scrapy.Request(url=topic_link, callback=self.parse_posts)

    def parse_posts(self, response):
        # create item
        post = BitcointalkPost()

        # get authors
        post_authors1 = response.css('td.windowbg td.poster_info a::text').extract()
        post_authors2 = response.css('td.windowbg2 td.poster_info a::text').extract()

        post_authors = list()

        for author in post_authors1:
            # drop "ignore" and numbers
            if author != "Ignore" or re.match("^([^0-9]{1,})$", author):
                post_authors.append(author)

        for author in post_authors2:
            if author != "Ignore" or re.match("^([^0-9]{1,})$", author):
                post_authors.append(author)

        # date and time
        post_date1 = response.css('td.windowbg td.td_headerandpost div.smalltext::text').extract()
        post_date2 = response.css('td.windowbg2 td.td_headerandpost div.smalltext::text').extract()

        post_dates = post_date1 + post_date2

        # topics
        post_topic1 = response.css('td.windowbg td.td_headerandpost div.subject a::text').extract()
        post_topic2 = response.css('td.windowbg2 td.td_headerandpost div.subject a::text').extract()

        post_topics = post_topic1 + post_topic2

        # posttext
        post_text1 = response.css('td.windowbg td.td_headerandpost div.post::text').extract()
        post_text2 = response.css('td.windowbg2 td.td_headerandpost div.post::text').extract()

        post_texts = post_text1 + post_text2

        # signatures ... plain text
        post_signatures_unfiltered = response.css('div.signature').extract()

        # sometimes parts are missing but hey
        for idx, item in enumerate(post_authors):
            try:
                post['author'] = post_authors[idx]
            except:
                post['author'] = "None"

            try:
                post['datetime'] = post_dates[idx]
            except:
                post['datetime'] = "None"

            try:
                post['posttext'] = post_texts[idx]
            except:
                post['posttext'] = "None"

            try:
                post['topic'] = post_topics[idx]
            except:
                post['topic'] = "None"

            try:
                post['signature'] = post_signatures_unfiltered[idx]
            except:
                post['signature'] = "None"

            tohash = str(post['author']) + str(post['datetime']) + str(post['posttext'] + str(post['topic']) + str(post['signature']))
            hobject = hashlib.sha256(tohash.encode())
            hash_string = str(hobject.hexdigest())
            post['identityhash'] = hash_string

            # save to MongoDB
            yield post

        # post pagination
        try:
            next_page = response.css('span.prevnext a::attr(href)').re(r'https:\/\/bitcointalk.org\/index.php\?topic=[0-9]{1,}.[0-9]{1,}')[0]
        except:
            next_page = None

        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse_posts)


