# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re

from itemadapter import ItemAdapter


class ApartmentsPipeline:
    def process_item(self, item, spider):
        return item


class PricePipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("price"):
            adapter["price"] = int(re.sub('\D', '', adapter["price"]))
        return item


class BedroomPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("bedrooms"):
            adapter["bedrooms"] = int(
                adapter["bedrooms"]
                .lower()
                .replace("bds", "")
                .replace("bd", "")
                .replace("beds", "")
                .replace("bed", "")
                .strip()
                .replace("studio", "0")
            )
        return item


class BathroomPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("bathrooms"):
            adapter["bathrooms"] = float(
                adapter["bathrooms"]
                .lower()
                .replace("baths", "")
                .replace("bath", "")
                .replace("bas", "")
                .replace("ba", "")
                .strip()
            )
        return item


class SquareFeetPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("square_feet"):
            adapter["square_feet"] = int(re.sub('\D', '', adapter["square_feet"]))
        return item


class ScorePipeline:
    scores = ["walk_score", "transit_score", "bike_score"]
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        for score in self.scores:
            if adapter.get(score):
                adapter[score] = int(adapter[score])
        return item


class BuildYearPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("build_year"):
            adapter["build_year"] = int(re.sub('\D', '', str(adapter["build_year"])))
        return item


class FeePipeline:
    fees = ["admin_fee", "application_fee"]

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        for fee in self.fees:
            if adapter.get(fee):
                adapter[fee] = int(re.sub('\D', '', str(adapter[fee])))
        return item


class RatingPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("rating"):
            adapter["rating"] = float(adapter["rating"])
        return item
