BOT_NAME = "tutorial"

SPIDER_MODULES = ["tutorial.spiders"]
NEWSPIDER_MODULE = "tutorial.spiders"

# settings.py

# Obey robots.txt rules
#ROBOTSTXT_OBEY = True


HTTPERROR_ALLOWED_CODES = [403, 404, 500, 502, 503, 504]  # Add the HTTP codes you want to handle

#SPIDER_MIDDLEWARES = {
#    "tutorial.middlewares.TutorialSpiderMiddleware": 543,
#}

DOWNLOADER_MIDDLEWARES = {
    "tutorial.middlewares.TutorialSpiderMiddleware": 543,
    #"tutorial.middlewares.SeleniumMiddleware": 544,

}


RETRY_ENABLED = False
RETRY_TIMES = 3  # Number of times to retry
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]  # Add the HTTP codes you want to retry

