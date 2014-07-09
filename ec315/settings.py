#!/usr/bin/python
MODEM_IP = 'http://192.168.1.1'
MODEM_PASS = 'admin'

CONNECTION_URL = MODEM_IP + '/api/dialup/connection'
CONTROL_URL = MODEM_IP + '/api/device/control'
LOGIN_URL = MODEM_IP + '/api/user/login'
STATUS_URL = MODEM_IP + '/api/monitoring/status'
TRAFFICSTATS_URL = MODEM_IP + '/api/monitoring/traffic-statistics'
CONNECTION_MODE = {
	0: 'Auto', 
	1: 'Manual',
	2: 'Ondemand'
	}

CONNECTIONSTATUS_CODES = {
    900: 'Connectings',
    901: 'Connected',
    902: 'Disconected',
    903: 'X3',
    904: 'Connection failed'
	}

# In most cases you don't need to change these:
proxy=None
DEBUG_ON=True
SHOW_ON=True
FETCH_TIMEOUT_SECS=20
MODEM_REFRESH_TIMEOUT_SECS=30