# -*- coding: utf-8 -*-
#import sys
import xbmcaddon,xbmc,xbmcvfs,xbmcgui
#import xbmcplugin
import urllib2
import datetime, time
UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'
HEADERS = { 'User-Agent' : UA } 
    
addon = xbmcaddon.Addon(id='plugin.video.vstream')
rootDir = addon.getAddonInfo('path')
writeDir = xbmc.translatePath("/".join([rootDir ,'resources/']))

URL_MAIN = "https://raw.githubusercontent.com/johngf/plugin.video.patch/master/resources/"

list_urls = ["default.py",
            "lib/dlm3u8.py",
            "lib/gui/hoster.py",
            "hosters/jawcloud.py",
            "hosters/netu.py",
            "hosters/rutube.py",
            "hosters/vidlox.py",
            "hosters/tune.py"]

class main:
    def __init__(self):
        addons = xbmcaddon.Addon('plugin.video.patch')
        service_time = addons.getSetting('service_time')
        #xbmc.log('\t[PLUGIN] patch: '+str(service_time), xbmc.LOGNOTICE)
        if not (service_time):
            addons.setSetting('service_time', str(datetime.datetime.now()))
            self.run()
            
        if (service_time):         
            time_sleep = datetime.timedelta(hours=1)
            time_now = datetime.datetime.now()
            time_service = self.__strptime(service_time, "%Y-%m-%d %H:%M:%S.%f")

            if (time_now - time_service > time_sleep):
                addons.setSetting('service_time', str(datetime.datetime.now()))
                self.run()

    def run(self):
        updialog = xbmcgui.DialogProgress()
        updialog.create("dlm3u8", "mise a jours des fichiers")
        num_urls = len(list_urls)
        for index,x in enumerate(list_urls):
            if updialog.iscanceled():
                break
                
            # xbmc.log('\t[PLUGIN] patch: '+str(URL_MAIN + x), xbmc.LOGNOTICE)
            # xbmc.log('\t[PLUGIN] patch: '+str(writeDir + x), xbmc.LOGNOTICE)

            req = urllib2.Request(URL_MAIN + x, None, HEADERS)
            rep = urllib2.urlopen(req)
            sHtmlContent = rep.read()
            rep.close()
            
            cFile = xbmcvfs.File((writeDir + x), 'w')
            cFile.write(sHtmlContent)
            cFile.close()
            
            percent = ((index + 1) * 100) / num_urls
            updialog.update(percent, ("mise a jours des fichiers"), ("%s / %s") % (index + 1, num_urls))
            
        updialog.close()
        return
        
    def __strptime(self, date, format):
        try:
            date = datetime.datetime.strptime(date, format)
        except TypeError:
            date = datetime.datetime(*(time.strptime(date, format)[0:6]))
        return date    
        #xbmcplugin.endOfDirectory(int(sys.argv[1]))
main()
    
