import scrapy
class ImdbItem(scrapy.Item):
  film = scrapy.Field()
  year = scrapy.Field()
  director = scrapy.Field()
  prod_team = scrapy.Field()
  dir_team = scrapy.Field()
  camera_team = scrapy.Field()
  prod_manage_team = scrapy.Field()
  country = scrapy.Field()
