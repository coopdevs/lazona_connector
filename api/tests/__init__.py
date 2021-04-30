import httpretty
import os

import koiki

httpretty.enable(allow_net_connect=False)

koiki.wcfmmp_api_base = 'https://wcfmmp_testing_host'
