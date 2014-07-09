#!/usr/bin/python
# -*- coding: utf8 -*-

# Copyright 2014 Sergiy Khalymon  <sergiykhalimon@gmail.com>
#
# Author: Sergiy Khalymon  <sergiykhalimon@gmail.com>

# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3, as published by the Free Software Foundation.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, 
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.

from bs4 import BeautifulSoup
from functools import wraps

import appindicator
import pynotify
import gtk
import gobject

import settings
import datetime
import os
import base64

import requests

current_dir = os.path.dirname(os.path.abspath(__file__))+'/'
img_dir = current_dir+'img/'

def notify(msg, title='Modem EC315', image=img_dir+'signal0.png'):
    pynotify.Notification(title, msg, image).show()
    

def try_exept(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            print err
            notify(str(err), 'Modem EC315 Extention')
            return err
    return wrapper

class Inter():     

    def __init__(self):
        pynotify.init('Intertelecom indicator EC315')
        self.current_dir = current_dir
        self.img_dir = img_dir
        
        notify('Indicator is starting worked')

        self.old_connection_status = ''

        self.indicator = appindicator.Indicator('inter_indicator', self.img_dir+'signal0.png', 
            appindicator.CATEGORY_APPLICATION_STATUS)
        self.indicator.set_status(appindicator.STATUS_ACTIVE)
        self.indicator.set_icon_theme_path(self.img_dir)
        m = gtk.Menu()

        refresh_modem_now_item = gtk.MenuItem('Refresh Modem Status')
        restart_modem_item = gtk.MenuItem('Restart Modem')
        change_modem_connection_mode_item = gtk.MenuItem('Change Connection Mode')
        self.modem_connection_mode = gtk.MenuItem('Connection mode: N/A')
        self.modem_connection_status_label = gtk.MenuItem('Connection: N/A')
        self.modem_tx_rx_label = gtk.MenuItem('Total: %s Mb, Tx: N/A Mb, Rx: N/A Mb')
        self.modem_connect_clients_label = gtk.MenuItem('Clients connected: N/A')
        self.modem_connection_mode_label = gtk.MenuItem('Connectoin mode: N/A')
        qi = gtk.MenuItem('Quit')
        
        m.append(self.modem_connection_status_label)
        m.append(self.modem_tx_rx_label)
        m.append(self.modem_connect_clients_label)
        m.append(self.modem_connection_mode_label)

        m.append(gtk.SeparatorMenuItem())
        m.append(refresh_modem_now_item)
        m.append(restart_modem_item)
        m.append(change_modem_connection_mode_item)

        m.append(gtk.SeparatorMenuItem())
        m.append(qi)
        
        self.indicator.set_menu(m)
        m.show_all()
        
        refresh_modem_now_item.connect('activate', self.refresh_modem_status)
        restart_modem_item.connect('activate', self.restart_modem)
        change_modem_connection_mode_item.connect('activate', self.change_connect_mode_modem)
        qi.connect('activate', quit)
    
        self.source_id = gobject.timeout_add(200, self.refresh_modem_status)
    
    def quit(self, item):
            gtk.main_quit()

    @try_exept
    def getpost_data(self, url, method='post', payload=''):
        '''Universal method to get and post data'''
        if method == 'get':
            response = requests.get(url)
        elif method == 'post':
            response = requests.post(url, payload)
        
        if response.ok:
            print '%s:%s OK' % (method.upper(), url)
        else:
            print '%s:%s ERROR' % (method.upper(), url)
        return BeautifulSoup(response.content, 'xml')
    
    @try_exept
    def change_connect_mode_modem(self, action=None):
        '''This method changing connect mode to Auto or Manual'''
        response = self.getpost_data(settings.CONNECTION_URL, 'get')
        connectmode = int(response.ConnectMode.text)
        new_connectmode = response.new_tag('ConnectMode')
        new_connectmode.string = '0' if connectmode else '1'
        response.ConnectMode.replace_with(new_connectmode)
        self.getpost_data(settings.CONNECTION_URL, 'post', str(response).replace('response', 'request'))

        new_connectmode = int(new_connectmode.text)
        notify('Changing connect mode to %s' % settings.CONNECTION_MODE[new_connectmode])
        self.get_status()
        
    @try_exept
    def login(self):
        '''This method provide loggin'''
        AdPassword = base64.encodestring(settings.MODEM_PASS).rstrip()
        payload = "<?xml version='1.0' encoding='UTF-8'?><request><Username>admin</Username><Password>%s</Password></request>" % AdPassword
        self.getpost_data(settings.LOGIN_URL, 'post', payload)

    @try_exept
    def restart_modem(self,  action=None):
        '''This method restarts/reboots modem'''
        payload = "<?xml version='1.0' encoding='UTF-8'?><request><Control>1</Control></request>"
        self.getpost_data(settings.CONTROL_URL, 'post', payload)
        notify('Restarting')
        self.get_status()
    
    def get_status(self):
        status = self.getpost_data(settings.STATUS_URL, 'get')    
        self.indicator.set_icon('signal'+status.SignalIcon.text)
        connectionstatus_code = int(status.ConnectionStatus.text)
        self.connection_status = settings.CONNECTIONSTATUS_CODES[connectionstatus_code]
        self.modem_connect_clients_label.set_label('Clients connected: %s' % status.CurrentWifiUser.text)        
        
        print 'before'+self.old_connection_status+' = '+self.connection_status
        if self.old_connection_status != self.connection_status:
            notify(self.connection_status)
        self.old_connection_status = self.connection_status
        print 'after'+self.old_connection_status+' = '+self.connection_status

    def get_trafficstat(self):
        trafficstat = self.getpost_data(settings.TRAFFICSTATS_URL, 'get')
        tx = float(trafficstat.CurrentDownload.text)/1024/1024
        rx = float(trafficstat.CurrentUpload.text)/1024/1024
        self.modem_tx_rx_label.set_label('Total: %0.2f Mb, Tx: %0.2f Mb, Rx: %0.2f Mb' % (tx + rx, tx, rx))
        self.seconds = int(trafficstat.CurrentConnectTime.text)

    
    def get_connectmode(self):
        connection_mode = self.getpost_data(settings.CONNECTION_URL, 'get')
        connectmode = int(connection_mode.ConnectMode.text)
        self.modem_connection_mode_label.set_label('Connection mode: %s' % settings.CONNECTION_MODE[connectmode])                

    @try_exept
    def refresh_modem_status(self, action=None):
        '''This method provide refresh interface'''
        try:
            gobject.source_remove(self.refresh_modem_timer)
        except Exception:
            pass
        finally:
            self.refresh_modem_timer = gobject.timeout_add(settings.MODEM_REFRESH_TIMEOUT_SECS*1000, self.refresh_modem_status)
        
        self.login()
        self.get_status()              
        self.get_trafficstat()
        self.get_connectmode()
        
        time = datetime.timedelta(seconds=self.seconds)
        self.modem_connection_status_label.set_label('%s Time: %s' % (self.connection_status, time))

        while gtk.events_pending():
            gtk.main_iteration()


if __name__ ==  '__main__':
    inter=Inter()
    gtk.main()
