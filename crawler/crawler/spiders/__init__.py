# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import os

if not os.path.exists('error/cpd'):
    os.makedirs('error/cpd')

if not os.path.exists('log/cpd'):
    os.makedirs('log/cpd')
