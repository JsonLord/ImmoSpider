# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ImmoscoutItem(scrapy.Item):
    # Basic property info
    immo_id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    full_description = scrapy.Field()

    # Address and location
    address = scrapy.Field()
    city = scrapy.Field()
    zip_code = scrapy.Field()
    district = scrapy.Field()
    lat = scrapy.Field()
    lng = scrapy.Field()

    # Travel times
    time_dest = scrapy.Field()
    time_dest2 = scrapy.Field()
    time_dest3 = scrapy.Field()

    # Financials and size
    rent = scrapy.Field()
    sqm = scrapy.Field()
    rooms = scrapy.Field()
    extra_costs = scrapy.Field()

    # Features
    kitchen = scrapy.Field()
    balcony = scrapy.Field()
    garden = scrapy.Field()
    private = scrapy.Field()
    area = scrapy.Field()
    cellar = scrapy.Field()

    # Contact and media
    contact_name = scrapy.Field()
    media_count = scrapy.Field()

    # LLM Analysis fields
    llm_analysis = scrapy.Field()
    llm_rating = scrapy.Field()
    llm_strengths = scrapy.Field()
    llm_weaknesses = scrapy.Field()
    llm_message_points = scrapy.Field()
    personalized_message = scrapy.Field()
