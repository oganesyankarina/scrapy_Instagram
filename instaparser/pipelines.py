# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import hashlib
from scrapy.utils.python import to_bytes


class InstaparserPipeline:
    def __init__(self):
        self.client = MongoClient("localhost:27017")
        self.db = self.client["Instagram"]

    def process_item(self, item, spider: scrapy.Spider):
        self.db[spider.name].update_one({'user_id': {"$eq": item["user_id"]}}, {'$set': item}, upsert=True)
        return item


class InstaImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['user_photo']:
            try:
                yield scrapy.Request(item['user_photo'])
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if results:
            item['user_photo'] = [itm[1] for itm in results]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'full/{item["user_name"]}/{image_guid}.jpg'
