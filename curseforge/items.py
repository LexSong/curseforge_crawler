from scrapy import Item, Field


class CurseforgeItem(Item):
    name = Field()
    download_count = Field()
