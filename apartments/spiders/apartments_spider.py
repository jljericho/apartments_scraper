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
        property_name = response.css("h1::text").get().strip(" \r\n")
        print(response.css("span.stateZipContainer span::text").getall())
        state_zip = response.css("span.stateZipContainer span::text").getall()
        state = state_zip[0]
        zip_code = state_zip[1] if len(state_zip) > 1 else None
        basic_info = {
            "url": response.url,
            "property_name": property_name,
            "address": response.css("span.delivery-address").css("span::text").get() or property_name,
            "zip_code": zip_code,
            "state": state,
            "price": response.xpath("//p[text()='Monthly Rent']/following-sibling::p[1]/text()").get(),
            "bedrooms": response.xpath("//p[text()='Bedrooms']/following-sibling::p[1]/text()").get(),
            "bathrooms": response.xpath("//p[text()='Bathrooms']/following-sibling::p[1]/text()").get(),
            "square_feet": response.xpath("//p[text()='Square Feet']/following-sibling::p[1]/text()").get(),
            "neighborhood": response.css("a.neighborhood::text").get(),
            "walk_score": response.css("div#walkScoreValue::text").get(),
            "transit_score": response.css("div.transitScore::attr(data-score)").get(),
            "bike_score": response.css("div.bikeScore::attr(data-score)").get(),
            "description": response.css("section.descriptionSection p::text").get(),
            "rating": response.css("div.averageRating::text").get()
        }

        parking = list()
        basic_info["application_fee"] = response.xpath("//div[text()='Application Fee']/following-sibling::div[1]/text()").get()
        basic_info["admin_fee"] = response.xpath("//div[text()='Admin Fee']/following-sibling::div[1]/text()").get()
        basic_info["build_year"] = response.xpath("//div[contains(text(), 'Built in')]/text()").get()
        for fee_group in response.css("div.feespolicies"):
            if fee_group.css("h4::text").get() == "Parking":
                for parking_option in fee_group.css("li"):
                    parking.append({
                        "title": parking_option.css("div.column::text").get(),
                        "cost": parking_option.css("div.column-right::text").get(),
                        "description": parking_option.css("div.subTitle::text").get()
                    })

        basic_info["parking"] = parking
        if not response.css("div.pricingGridItem").get():
            yield basic_info
        else:
            for model in response.css("div.pricingGridItem"):
                beds, bath, sqft_range = model.css("span.detailsTextWrapper span::text").getall()[:3]

                model_info = {
                    "model": model.css("span.modelName::text").get(),
                    "bedrooms": beds,
                    "bathrooms": bath
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
                    basic_info = basic_info.copy()
                    basic_info.update(unit_info)
                    basic_info.update(model_info)
                    yield basic_info


def _combine_css_texts(text_list: list[str]) -> str:
    return "".join(text_list).strip(" \r\n")
