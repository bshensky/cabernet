"""
MIT License

Copyright (C) 2021 ROCKY4546
https://github.com/rocky4546

This file is part of Cabernet

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
"""

import json
import logging
import re
import time
import urllib.request
from datetime import datetime

from lib.common.decorators import handle_url_except
from lib.common.decorators import handle_json_except
import lib.common.exceptions as exceptions
import lib.common.utils as utils


class Geo:

    def __init__(self, _config_obj, _section):
        self.logger = logging.getLogger(__name__)
        self.config_obj = _config_obj
        self.section = _section
        self.geoId = None
        self.channelListId = None
        self.get_geo()

    @handle_json_except 
    @handle_url_except 
    def get_geo(self):
        """
        Geo info comes from json object on the home page
        If the request fails, we will use the last data available in config
        """
        if self.config_obj.data[self.section]['geoid'] is not None and \
                self.config_obj.data[self.section]['channellistid'] is not None:
            self.geoId = self.config_obj.data[self.section]['geoid']
            self.channelListId = self.config_obj.data[self.section]['channellistid']
            self.logger.debug('Reusing XUMO geoId and channelListId from provider')
        else:
            geo_url = 'https://www.xumo.tv'
            login_headers = {'Content-Type': 'application/json', 'User-agent': utils.DEFAULT_USER_AGENT}
            req = urllib.request.Request(geo_url, headers=login_headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                matchOrg = re.findall(b'__JOBS_REHYDRATE_STATE__=(.+?);</script>', (resp.read()), flags=re.DOTALL)
                if len(matchOrg) > 0:
                    results = json.loads(matchOrg[0])
                    self.geoId, self.channelListId = results["jobs"]["1"]["data"]["geoId"], results["jobs"]["1"]["data"]["channelListId"]
                    self.config_obj.write(self.section, 'geoid', self.geoId)
                    self.config_obj.write(self.section, 'channellistid', self.channelListId)
        
