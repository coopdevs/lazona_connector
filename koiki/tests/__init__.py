import httpretty

import koiki

httpretty.enable(allow_net_connect=False)

koiki.host = 'https://testing_host'
koiki.wcfmmp_host = 'https://wcfmmp_testing_host'
