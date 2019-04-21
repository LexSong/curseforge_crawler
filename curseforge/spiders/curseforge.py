from scrapy import Spider, Request


class CurseforgeSpider(Spider):
    name = 'curseforge'

    def parse_project_page(self, response):
        relations_url = f"./{self.project_name}/relations/"

        if self.relations == 'dependencies':
            relations_url += "dependencies"
        elif self.relations == 'include':
            relations_url += "dependents?filter-related-dependents=6"
        else:
            raise ValueError

        yield response.follow(relations_url, self.parse)

    def start_requests(self):
        project_url = f"https://minecraft.curseforge.com/projects/{self.project_name}"
        yield Request(project_url, self.parse_project_page)

    def parse(self, response):
        items = response.css("li.project-list-item div.details")
        for x in items:
            name = x.css("div.info.name a::text").get()
            count = x.css("div.info.stats p.e-download-count::text").get()
            count = int(count.replace(',', ''))
            yield {'name': name, 'download_count': count}

        next_page = response.css(
            "li.b-pagination-item-next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
