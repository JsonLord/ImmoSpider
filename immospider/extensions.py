import logging
from scrapy import signals
import telegram
import asyncio


logger = logging.getLogger(__name__)


class SendTelegramMessage(object):

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.items = []

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        token = settings.get("TELEGRAM_API_TOKEN")
        chat_id = settings.get("TELEGRAM_CHAT_ID")

        ext = cls(token, chat_id)

        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        return ext

    async def send_messages_async(self):
        bot = telegram.Bot(token=self.token)
        tasks = []
        for item in self.items:
            message = f"<b>{item['title']}</b>\n"
            message += f"<a href='{item['url']}'>Link to offer</a>\n\n"
            message += f"<b>Address:</b> {item['address']}, {item['zip_code']} {item['city']}\n"
            message += f"<b>Rent:</b> {item['rent']}€\n"
            message += f"<b>Size:</b> {item['sqm']}m²\n"
            message += f"<b>Rooms:</b> {item['rooms']}\n\n"
            message += f"<b>LLM Analysis:</b>\n{item['llm_analysis']}\n\n"
            message += f"<b>Rating:</b> {item['llm_rating']}\n"
            message += f"<b>Strengths:</b> {', '.join(item['llm_strengths'])}\n"
            message += f"<b>Weaknesses:</b> {', '.join(item['llm_weaknesses'])}\n\n"
            message += f"<b>Personalized Message:</b>\n{item['personalized_message']}"
            tasks.append(bot.send_message(chat_id=self.chat_id, text=message, parse_mode='HTML'))
        await asyncio.gather(*tasks)

    def spider_closed(self, spider):
        if len(self.items) > 0:
            asyncio.run(self.send_messages_async())
            logger.info("Telegram messages sent.")
        else:
            logger.info("No new items found. No Telegram message sent.")

    def item_scraped(self, item, spider):
        self.items.append(item)
