# -*- coding: utf-8 -*-

from datetime import datetime from dateutil import tz
utc = tz.tzutc()
local = tz.tzlocal()
utc_now = datetime.utcnow() utc_now # Not timezone-aware.
utc_now = utc_now.replace(tzinfo=utc) utc_now # Timezone-aware.
local_now = utc_now.astimezone(local) local_now # Converted to local time.
