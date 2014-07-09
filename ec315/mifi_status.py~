#!/usr/bin/python
# -*- coding: utf8 -*-

# Copyright 2013 Kostyantyn Ovechko <fastinetserver@gmail.com>
#
# Author: Kostyantyn Ovechko <fastinetserver@gmail.com>

# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3, as published by the Free Software Foundation.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, 
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.

import appindicator
import pynotify
import gtk
import gobject

import time
import settings
import datetime
from tools import *
import os
from lxml import html
import hashlib

import re

pwtoken_search=re.compile('var pwtoken = "([\w]+)"', re.DOTALL)
stoken_search=re.compile('<input type="hidden" name="stoken" value="([\w]+)">', re.DOTALL)

class Inter():    
    def __init__(self):
        self.current_dir=os.path.dirname(os.path.abspath(__file__))+'/'
        self.tmp_dir=self.current_dir+'tmp/'
        self.img_dir=self.current_dir+'img/'
    
        self.indicator = appindicator.Indicator('inter_indicator', self.img_dir+'signal0.png', appindicator.CATEGORY_APPLICATION_STATUS)
        self.indicator.set_status( appindicator.STATUS_ACTIVE )
        self.indicator.set_icon_theme_path(self.img_dir)
        m = gtk.Menu()

        refresh_modem_now_item = gtk.MenuItem('Refresh Modem Status')
        restart_modem_item = gtk.MenuItem('Restart Modem')
        self.modem_signal_label = gtk.MenuItem('Signal: N/A')
        self.modem_connection_status_label = gtk.MenuItem('Connection: N/A')
        self.modem_tx_rx_label = gtk.MenuItem("Total: %s Mb, Tx: N/A Mb, Rx: N/A Mb")
        self.modem_ip_label = gtk.MenuItem('IP: N/A')
        self.modem_dns_label = gtk.MenuItem('DNS: N/A')
        self.modem_connect_clients_label = gtk.MenuItem('Clients connected: N/A')
        self.modem_bat_status_label = gtk.MenuItem('Battery: N/A')
        qi = gtk.MenuItem( 'Quit' )
        
        m.append(self.modem_signal_label)
        m.append(self.modem_connection_status_label)
        m.append(self.modem_tx_rx_label)
        m.append(self.modem_ip_label)
        m.append(self.modem_dns_label)
        m.append(self.modem_connect_clients_label)
        m.append(self.modem_bat_status_label)

        m.append(gtk.SeparatorMenuItem())
        m.append(refresh_modem_now_item)
        m.append(restart_modem_item)

        m.append(gtk.SeparatorMenuItem())
#        m.remove(restart_modem_item)
        m.append(qi)
        
        self.indicator.set_menu(m)
        m.show_all()
        
        refresh_modem_now_item.connect('activate', self.refresh_modem_status)
        restart_modem_item.connect('activate', self.restart_modem)
        qi.connect('activate', quit)
    
        self.source_id = gobject.timeout_add(200, self.refresh_modem_status)
    
    def quit(self, item):
            gtk.main_quit()
    
    def do_restart_modem(self):
        """This method restarts/reboots mifi modem"""
        stage='1 - get tokens'
        content, code=get_page('http://'+settings.MODEM_IP, self.tmp_dir, stage, None, False, None, False, True,'Get projects list')
        matches = pwtoken_search.search(content)
        if matches:
            pwtoken = matches.group(1)
        else:
            print "Can NOT find pwtoken"
            return
            
        matches = stoken_search.search(content)
        if matches:
            stoken = matches.group(1)
        else:
            print "Can NOT find stoken"
            return

        stage='2 - login'
        AdPassword=hashlib.sha1(settings.MODEM_PASS+pwtoken).hexdigest()        
        post_fields='buttonlogin=Login&AdPassword='+AdPassword+'&todo=login&nextfile=home.html&stoken='+stoken
        content, code=get_page('http://'+settings.MODEM_IP+'/login.cgi', self.tmp_dir, stage, None, False, post_fields, False, True,'Get projects list')

        stage='3 - restart'
        post_fields='todo=restart&nextfile=home.html&stoken='+stoken
        content, code=get_page('http://'+settings.MODEM_IP+'/login.cgi', self.tmp_dir, stage, None, False, post_fields, False, True,'Get projects list')

    def restart_modem(self, action=None):
        """This method is try...except a wrapper around self.do_restart_modem()"""
        try:
            self.do_restart_modem()
        except Exception as err:
            print err

    def do_refresh_modem_status(self):
        stage='1 - Get Modem Status'
        content, code=get_page('http://'+settings.MODEM_IP+'/getStatus.cgi?dataType=TEXT', self.tmp_dir, stage, None, False, None, False, True,'Get projects list')
#        print content
        if content is None:
            return
        
        content=content.replace('\x1b','&')
        name_value_list = content.split('&')
        res={}
        for name_value in name_value_list:
            name_value_splitted=name_value.split('=')
            if len(name_value_splitted)==2:
                res[name_value_splitted[0]]=name_value_splitted[1]
        
#        print res
        self.indicator.set_icon('signal'+res.get('WwRssi','0'))

        try:
            signal = "%d%%" % (int(res['WwRssi'])*20)
        except Exception:
            signal ="N/A"
        self.modem_signal_label.set_label('Signal: %s' % signal)

        if 'BaBattChg':
            charging = 'Charging'
        else:
            charging = 'Not charging'
        
        try:
            batt = "%d%%" % (int(res['BaBattStat'])*20)
        except Exception:
            batt ="N/A"
            
        self.modem_bat_status_label.set_label("Battery: %s (%s)" % (batt, charging))
        if res['WwConnStatus']=='2':
            connection_status='Connected'
        else:
            connection_status='Disconnected' 
        self.modem_ip_label.set_label("IP: %s" % (res.get('WwIpAddr','N/A')))
        self.modem_dns_label.set_label("DNS: %s" % (res.get('WwDNS1','N/A')))
        
        self.modem_connect_clients_label.set_label("Clients connected: %s" % res.get('WiConnClients','N/A'))
        try:
            tx = "%0.2f" % float(res['WwSessionTxMb'])
        except Exception:
            tx = 'N/A'

        try:
            rx = "%0.2f" % float(res['WwSessionRxMb'])
        except Exception:
            rx = 'N/A'
        
        try:
            tx_plus_rx = "%0.2f" % (float(res['WwSessionTxMb']) + float(res['WwSessionRxMb']))
        except Exception:
            tx_plus_rx = 'N/A'
        
        self.modem_tx_rx_label.set_label("Total: %s Mb, Tx: %s Mb, Rx: %s Mb" % (tx_plus_rx, tx, rx))
        try:
            seconds = int(res['WwSessionTimeSecs'])
        except Exception:
            time = "N/A" 
        else:
            time = str(datetime.timedelta(seconds=seconds))
        self.modem_connection_status_label.set_label('%s Time: %s' % (connection_status, time))

        while gtk.events_pending():
            gtk.main_iteration()
        
    def refresh_modem_status(self, action=None):
        """This method is try...except a wrapper around self.do_refresh_modem_status()"""
        try:
            self.do_refresh_modem_status()
        except Exception as err:
            print err

        try:
            gobject.source_remove(self.refresh_modem_timer)
        except Exception:
            pass
        self.refresh_modem_timer = gobject.timeout_add(settings.MODEM_REFRESH_TIMEOUT_SECS*1000, self.refresh_modem_status)
    
if __name__ ==  '__main__':
    inter=Inter()
    gtk.main()