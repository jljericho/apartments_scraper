from pathlib import Path

import scrapy


class ApartmentsSpider(scrapy.Spider):
    name = "apartments"

    def start_requests(self):
        urls = [
            'https://www.apartments.com/dupont-circle-washington-dc/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for property_div in response.css("div.property-information"):
            link = property_div.css("a.property-link::attr(href)")
            yield scrapy.Request(link.get(), callback=self.parse_result_page)

    def parse_result_page(self, response):
        print("Result page!" + response.url)
        property_name = response.css("h1::text").get().strip(" \r\n")
        basic_info = {
            "url": response.url,
            "property_name": property_name,
            "address": response.css("span.delivery-address").css("span::text").get() or property_name,
            "neighborhood": response.css("a.neighborhood::text").get(),
            "rent": response.css("p.rentInfoDetail::text").get(),
            "walk_score": response.css("div#walkScoreValue::text").get(),
            "transit_score": response.css("div.transitScore::attr(data-score)").get(),
            "bike_score": response.css("div.bikeScore::attr(data-score)").get(),
            "sound_score": response.css("div#soundScoreNumber::text").get(),
        }
        for model in response.css("div.pricingGridItem"):
            print(model.css("span.detailsTextWrapper span::text").getall())
            beds, bath, sqft_range = model.css("span.detailsTextWrapper span::text").getall()

            model_info = {
                "model": model.css("span.modelName::text").get(),
                "beds": beds,
                "bath": bath
            }
            for unit in model.css("li.unitContainer"):
                name_components = unit.css("button.unitBtn *::text").getall()
                unit_name = "".join(name_components).strip(" \r\n")

                unit_info = {
                    "unit": unit_name,
                    "price": "".join(unit.css("div.pricingColumn span *::text").getall()).replace("price ", "").strip(" \r\n"),
                    "square_feet": "".join(unit.css("div.sqftColumn span *::text").getall()).replace("square feet ", "").strip(" \r\n"),
                    "available": "".join(unit.css("span.dateAvailable *::text").getall()).replace("availibility ", "").strip(" \r\n"),
                }
                unit_info.update(model_info)
                unit_info.update(basic_info)
                yield unit_info


def _combine_css_texts(text_list: list[str]) -> str:
    return "".join(text_list).strip(" \r\n")
