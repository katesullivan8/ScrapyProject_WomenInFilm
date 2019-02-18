from scrapy import Spider
from imdb2.items import Imdb2_Item
from scrapy import Request
import time

class ImdbSpider(Spider):
  name = "imdb_spider2"
  allowed_urls =["https://www.imdb.com/"]
  start_urls = ['https://www.imdb.com/search/title?title_type=feature']

  def parse(self, response):
    # creates urls for each decade from 2018 - 1919
    decades_list = ['https://www.imdb.com/search/title?title_type=feature&release_date={}-01-01,{}-12-31&view=simple&sort=moviemeter'.format(x, x+9) for x in range(1989, 1969, -10)]

    # for each url in decades_list,
    list_urls = []
    for decade in decades_list:
        # list of pages that hold the general movie lists
        list_urls.extend([decade+'&start={}&ref_=adv_nxt'.format(x) for x in range(1,9951, 50)])

    for url in list_urls:
      yield Request(url=url, callback=self.parse_list)

  def parse_list(self, response):
    # get crew urls
    title_hrefs = response.xpath('.//*[@class="lister-item-header"]/span/a/@href').extract()

    title_nums = []
    for t in title_hrefs:
      tn = t.split('/')[2]
      title_nums.append(tn)

    # form url for cast and crew pages and release date url
    crew_urls = []
    release_urls = []

    for n in title_nums:
      crew_url = 'https://www.imdb.com/title/{}/fullcredits?ref_=tt_ql_1'.format(n)
      release_url = 'https://www.imdb.com/title/{}/releaseinfo?ref_=tt_ql_dt_2#releases'.format(n)
      yield Request(url=crew_url, callback=self.cast_crew_detail, meta={'refpath': release_url})


  def cast_crew_detail(self, response):
    item = Imdb2_Item()
    film = response.xpath('.//*[@itemprop="name"]/a/text()').extract_first()


    table_rows = response.xpath('//*[@id="fullcredits_content"]/h4[@class="dataHeaderWithBorder"]/text()').extract()


    table_rows = [x.strip().lower().replace(' ', '') for x in table_rows]

    table_rows = list(filter(None, table_rows))

    dir_number = -1
    prod_number = -1
    cam_number = -1
    prod_manage_number = -1

    dept_tags = ['secondunitdirectororassistantdirector', 'producedby', 'cameraandelectricaldepartment', 'productionmanagement']
    if dept_tags[0] in table_rows:
      dir_number = table_rows.index(dept_tags[0]) +1
    if dept_tags[1] in table_rows:
      prod_number = table_rows.index(dept_tags[1]) + 1
    if dept_tags[2] in table_rows:
      cam_number = table_rows.index(dept_tags[2]) + 1
    if dept_tags[3] in table_rows:
      prod_manage_num = table_rows.index(dept_tags[3]) +1
    prod_names = []
    dir_names = []
    camera_team = []
    prod_manage_team = []

    director = response.xpath('//*[@id="fullcredits_content"]/table[1]/tbody/tr/td[1]/a/text()').extract()
    if prod_number > -1:
      prod_names = response.xpath('//*[@id="fullcredits_content"]/table[{}]/tbody/tr/td/a/text()'.format(prod_number)).extract()
    if dir_number > -1:
      dir_names = response.xpath('//*[@id="fullcredits_content"]/table[{}]/tbody/tr/td/a/text()'.format(dir_number)).extract()
    if cam_number > -1:
      camera_team = response.xpath('//*[@id="fullcredits_content"]/table[{}]/tbody/tr/td[1]/a/text()'.format(cam_number)).extract()
    if prod_manage_number > -1:
      prod_manage_team = response.xpath('//*[@id="fullcredits_content"]/table[{}]/tbody/tr/td/a/text()'.format(prod_manage_num)).extract()


    item['film'] = film
    item['prod_team'] = [x.strip() for x in prod_names]
    item['dir_team'] = [x.strip() for x in dir_names]
    item['director'] = [x.strip() for x in director]
    item['camera_team'] = [x.strip() for x in camera_team]
    item['prod_manage_team'] = [x.strip() for x in prod_manage_team]

    release_url = response.meta['refpath']

    yield Request(url = release_url, callback=self.release_detail, meta= item)

  def release_detail(self, response):
    item = response.meta
    year = response.xpath('//td[@class="release-date-item__date"]/text()').extract_first()
    country = response.xpath('//td[@class="release-date-item__country-name"]/a/text()').extract()
    item['year'] = year
    item['country'] = [x.strip() for x in country]

    print (item)
    print ('-' * 100)
    yield item


