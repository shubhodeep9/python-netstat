import threading
from collections import deque
import time
import psutil
import signal
from gi.repository import GLib
from gi.repository import Gtk as gtk
try:
    from gi.repository import AppIndicator3 as AppIndicator
except:
    from gi.repository import AppIndicator

class pythonNet:
    def __init__(self):
        APPINDICATOR_ID = 'myappindicator'
        self.indicator = AppIndicator.Indicator.new(APPINDICATOR_ID, 'network-transmit-receive', AppIndicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        
        self.transfer_rate = deque(maxlen=1)
        self.t = threading.Thread(target=self.calc_ul_dl, args=(self.transfer_rate,))
        self.t.daemon = True
        self.t.start()
        self.indicator.set_menu(self.build_menu())
        
        self.indicator.set_label("Detecting..","Speed")
        GLib.timeout_add(500, self.setLabel)
        
    def setMenuLabel(self, item_upload, item_download):
        item_upload.set_label(self.print_upload(self.transfer_rate))
        item_download.set_label(self.print_download(self.transfer_rate))
        return True


    def calc_ul_dl(self,rate, dt=0.5, interface='wlan0'):
        t0 = time.time()
        counter = psutil.net_io_counters(pernic=True)[interface]
        tot = (counter.bytes_sent, counter.bytes_recv)

        while True:
            last_tot = tot
            time.sleep(dt)
            counter = psutil.net_io_counters(pernic=True)[interface]
            t1 = time.time()
            tot = (counter.bytes_sent, counter.bytes_recv)
            ul, dl = [(now - last) / (t1 - t0) / 1000.0
                      for now, last in zip(tot, last_tot)]
            rate.append((ul, dl))
            t0 = time.time()


    def print_rate(self,rate):
        try:
            return (u'\u25b4'+'{0:.1f}kB/s '+u'\u25be'+'{1:.1f}kB/s').format(*rate[-1])
        except IndexError:
            return 'Detecting...'

    def print_upload(self,rate):
        try:
            return ('Upload: {0:.1f}kB/s').format(*rate[-1])
        except IndexError:
            return 'Detecting..'

    def print_download(self,rate):
        try:
            return ('Download: {1:.1f}kB/s').format(*rate[-1])
        except IndexError:
            return 'Detecting..'

    def build_menu(self):
        menu = gtk.Menu()

        item_upload = gtk.MenuItem('Up_Speed')
        menu.append(item_upload)

        item_download = gtk.MenuItem('Down_Speed')
        menu.append(item_download)

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        GLib.timeout_add(500, self.setMenuLabel,item_upload, item_download)
        return menu

    def quit(self,source):
        gtk.main_quit()
        
    def setLabel(self):
        self.indicator.set_label(self.print_rate(self.transfer_rate),"Speed")
        return True

if __name__ == '__main__':
    ob = pythonNet()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    gtk.main()