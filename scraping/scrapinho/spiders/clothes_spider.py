import logging
import scrapy
from scrapinho.items import PolyvoreItem, PolyvoreSet


def normalize_item_link(link):
    """
    >>> link = 'https://www.polyvore.com/tubes_cloches/thing?context_id=233025948&context_type=collection&id=228038397'
    "https://www.polyvore.com/tubes_cloches/thing?id=228038397"
    :param link:
    :return:
    """
    last_part = link.split('/')[-1]
    id = last_part.split('id=')[-1]
    normed_last_part = 'thing?id=' + id
    return link.replace(last_part, normed_last_part)


def norm(link):
    return link.replace('/../', '/')


class ClothesSpider(scrapy.Spider):
    name = "clothes"

    def start_requests(self):
        urls = ['https://www.polyvore.com/outfits/?p=%s' % i for i in range(100, 1000)]
        for i, url in enumerate(urls):
            yield scrapy.Request(url=url, callback=self.parse_listing)

            break

    def parse_listing(self, response):
        product_links = response.css('div .grid_item.hover_container.type_thing.span1w.span1h div.main a::attr(href)') \
            .extract()

        for link in product_links:
            link = normalize_item_link(link)
            yield scrapy.Request(url=response.urljoin(norm(link)), callback=self.parse_product)

        set_links = response.css('div .grid_item.hover_container.type_set.span2w.span2h div.main a::attr(href)') \
            .extract()

        for link in set_links:
            link = response.urljoin(link)
            # self.log('requesting set link | %s | %s |' % (link, norm(link)))
            yield scrapy.Request(url=link, callback=self.parse_set)

    def parse_product(self, response):
        thing = response.css('div .main_thing_right')
        title = thing.css('h1::attr(title)').extract_first()
        orig_price = thing.css('span.orig_price::text').extract_first()
        price = thing.css('span.price::text').extract_first()
        out_url = thing.css('a.outbound::attr(href)').extract_first()
        description = response.css('div#description.box.description div.bd div.tease::text').extract()
        img = response.css('div.page.thing div.clearfix#top a img::attr(src)').extract_first()
        crumbs = response.css('div.main_thing_right div.breadcrumb span.crumb a span::text').extract()

        yield PolyvoreItem(
            title=title,
            description=description,
            orig_price=orig_price,
            price=price,
            out_url=out_url,
            breadcrumbs=crumbs,
            url=response.request.url,
            image_urls=[img]
        )

    def parse_set(self, response):
        title = response.css('div#set_editor h1::text').extract_first()

        items = response.css('div.grid_item.hover_container.type_thing.span1w.span1h div.main a::attr(href)').extract()
        links = [response.urljoin(normalize_item_link(norm(link))) for link in items]

        for link in links:
            yield scrapy.Request(url=response.urljoin(norm(link)), callback=self.parse_product)

        similar_sets = response \
            .css('div.grid_item.hover_container.type_set.span2w.span2h div.main a::attr(href)').extract()

        for link in similar_sets:
            link = response.urljoin(link)
            yield scrapy.Request(url=response.urljoin(link), callback=self.parse_set)

        author = response.css('div.box div.createdby a::attr(href)').extract_first()
        commenters = response.css('div#comment_sink.comment_list div.title a::attr(href)').extract()
        likers = response.css('ul.layout_n.lookbook_fans li.size_t2 a::attr(href)').extract()

        for link in set(likers + commenters + [author]):
            for x in self.process_user(norm(link)):
                yield x

    def process_user(self, user):
        yield scrapy.Request(url=user + '?filter=sets&p=20', callback=self.parse_user_sets)
        yield scrapy.Request(url=user + '?filter=following&p=20', callback=self.parse_followed)
        yield scrapy.Request(url=user + '?filter=followers&p=20', callback=self.parse_followed)

    def parse_user_sets(self, response):
        sets = response.css('div.grid_item.hover_container.type_set.span2w.span2h div.main a::attr(href)').extract()

        for link in sets:
            link = norm(response.urljoin(link))
            yield scrapy.Request(url=link, callback=self.parse_set)

    def parse_followed(self, response):
        # same function can be used for the list of followers and the list of the followed
        followed = response.css('div.rec_follow.clearfix li.name a.clickable::attr(href)').extract()
        for user in followed:
            for x in self.process_user(user):
                yield x
