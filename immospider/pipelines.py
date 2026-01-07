# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import googlemaps
import datetime
import shelve
from scrapy.exceptions import DropItem
import json
import os
import requests
import logging

logger = logging.getLogger(__name__)

# see https://doc.scrapy.org/en/latest/topics/item-pipeline.html#duplicates-filter
class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = shelve.open("immo_items.db")

    def process_item(self, item, spider):
        immo_id = item['immo_id']

        if immo_id in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item['url'])
        else:
            self.ids_seen[immo_id] = item
            return item


class GooglemapsPipeline(object):

    # see https://stackoverflow.com/questions/14075941/how-to-access-scrapy-settings-from-item-pipeline
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        gm_key = settings.get("GM_KEY")
        return cls(gm_key)

    def __init__(self, gm_key):
        if gm_key:
            self.gm_client = googlemaps.Client(gm_key)
        with open("api/config.json", "r") as f:
            self.config = json.load(f)

    def _get_destinations(self, spider):
        destinations = []
        destinations.append((self.config['dest'], self.config['mode']))
        return destinations

    def _next_monday_eight_oclock(self, now):
        monday = now - datetime.timedelta(days=now.weekday())
        if monday < monday.replace(hour=8, minute=0, second=0, microsecond=0):
            return monday.replace(hour=8, minute=0, second=0, microsecond=0)
        else:
            return (monday + datetime.timedelta(weeks=1)).replace(hour=8, minute=0, second=0, microsecond=0)

    def process_item(self, item, spider):
        if hasattr(self, "gm_client"):
            # see https://stackoverflow.com/questions/11743019/convert-python-datetime-to-epoch-with-strftime
            next_monday_at_eight = (self._next_monday_eight_oclock(datetime.datetime.now())
                                         - datetime.datetime(1970, 1, 1)).total_seconds()

            destinations = self._get_destinations(spider)
            travel_times = []
            for destination, mode in destinations:
                result = self.gm_client.distance_matrix(item["address"],
                                                              destination,
                                                              mode=mode,
                                                              departure_time = next_monday_at_eight)
                #  Extract the travel time from the result set
                travel_time = None
                if result["rows"]:
                    if result["rows"][0]:
                        elements = result["rows"][0]["elements"]
                        if elements[0] and "duration" in elements[0]:
                            duration = elements[0]["duration"]
                            if duration:
                                travel_time = duration["value"]

                if travel_time is not None:
                    print(destination, mode, travel_time/60.0)
                    travel_times.append(travel_time/60.0)

            item["time_dest"] = travel_times[0] if len(travel_times) > 0 else None
            item["time_dest2"] = travel_times[1] if len(travel_times) > 1 else None
            item["time_dest3"] = travel_times[2] if len(travel_times) > 2 else None

        return item

class LLMAnalysisPipeline(object):
    def __init__(self):
        self.api_key = os.getenv("BLABLADOR_API_KEY")
        self.api_url = "https://api.helmholtz-blablador.fz-juelich.de/v1/chat/completions"

    def process_item(self, item, spider):
        if not self.api_key:
            logger.warning("BLABLADOR_API_KEY not found. Skipping LLM analysis.")
            return item

        prompt = f"""
        Please analyze the following property description and return a JSON object with the following structure:
        {{
            "analysis": "A brief, neutral summary of the property.",
            "strengths": ["A list of the top 3-5 positive aspects."],
            "weaknesses": ["A list of the top 3-5 potential problems or negative aspects."],
            "rating": "A price-to-benefit rating out of 10 (e.g., '7/10').",
            "message_points": ["A list of specific, individual points from the description that can be used to personalize a message to the owner."]
        }}

        Property Description:
        ---
        {item.get('full_description', 'No description available.')}
        ---
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "alias-large",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            llm_data = response.json()["choices"][0]["message"]["content"]
            llm_data = json.loads(llm_data) # The API returns the JSON as a string inside the content field

            item['llm_analysis'] = llm_data.get("analysis", "N/A")
            item['llm_rating'] = llm_data.get("rating", "N/A")
            item['llm_strengths'] = llm_data.get("strengths", [])
            item['llm_weaknesses'] = llm_data.get("weaknesses", [])
            item['llm_message_points'] = llm_data.get("message_points", [])
            logger.info(f"LLM analysis complete for item {item['immo_id']}.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get LLM analysis for item {item['immo_id']}: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response for item {item['immo_id']}: {e}")

        return item


class PersonalizedMessagePipeline(object):
    def __init__(self):
        with open("api/config.json", "r") as f:
            self.config = json.load(f)

    def process_item(self, item, spider):
        contact = item.get('contact_name', 'Sir/Madam')
        address = item.get('address', 'the property')
        points = item.get('llm_message_points', [])

        message = f"Dear {contact},\n\n"
        message += f"I am writing to express my strong interest in the apartment at {address}. "

        if points:
            message += f"I was particularly interested to read that {points[0].lower()}. "

        message += "I am very keen to arrange a viewing at your earliest convenience.\n\n"
        message += f"Sincerely,\n{self.config.get('contact_name', 'A Potential Tenant')}"

        item['personalized_message'] = message
        return item
