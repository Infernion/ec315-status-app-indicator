ec315-status-app-indicator
=========================

This solution based on https://github.com/fastinetserver/mifi-status-app-indicator

Gnome Applet Indicator for Huawei ec315 modem (Displays signal strength, , allows and to change connection mode and reboot modem)

Tested under:
- elementary os 0.2 Luna

![ScreenShot](https://raw2.github.com/Infernion/ec315-status-app-indicator/master/screenshots/Tooltip_002.png)

ec315-status-app-indicator is `BSD licensed` ( http://www.linfo.org/bsdlicense.html ).

Please let me know if you have any questions.


1) Specify correct settings in the settings.py file, e.g.:

```
MODEM_IP = '192.168.1.1'
MODEM_PASS = 'admin'
```

2) Run
./ec315_status.py

3) If indicator doesn't appear in your gnome panel, then follow this tutorial to install "Indicator Applet Complete"
http://www.webupd8.org/2011/11/indicator-applet-ported-to-gnome-3-can.html


GENERAL LINKS:

`BSD licensed`: http://www.linfo.org/bsdlicense.html
