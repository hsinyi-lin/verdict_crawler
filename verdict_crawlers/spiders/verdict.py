import scrapy
import re, json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

class VerdictSpider(scrapy.Spider):
    name = 'verdict'
    allowed_domains = ['judicial.gov.tw']
