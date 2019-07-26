from scrapy import Spider, Request


def get_relations_url(project_url):
    prefix = "https://www.curseforge.com/minecraft/"
    if not project_url.startswith(prefix):
        raise ValueError(f"Wrong url: {project_url}")

    project_type = project_url[len(prefix):].split('/', 1)[0]
    if project_type == 'modpacks':
        relations = "dependencies"
    elif project_type == 'mc-mods':
        relations = "dependents"
    else:
        raise ValueError(f"Unknown project type: {project_type}")

    relations_url = project_url + f"/relations/{relations}?filter-related-{relations}=6"
    return relations_url


def parse_count_string(count):
    count = count.split(' ')[0]
    if count.endswith('M'):
        return int(float(count[:-1]) * 10) * 100000
    elif count.endswith('K'):
        return int(float(count[:-1]) * 10) * 100
    else:
        try:
            return int(count)
        except ValueError:
            return 0


class CurseforgeSpider(Spider):
    name = 'curseforge'

    def start_requests(self):
        yield Request(get_relations_url(self.url))

    def parse(self, response):
        items = response.css("li.project-listing-row div.flex.flex-col")
        for x in items:
            name = x.css("h3::text").get()
            count = x.css("span:nth-child(1)::text").get()
            count = parse_count_string(count)
            yield {'name': name, 'download_count': count}

        next_page = response.css("div.pagination-next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
