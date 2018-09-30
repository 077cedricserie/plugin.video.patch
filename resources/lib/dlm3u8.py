#-*- coding: utf-8 -*-
#johngf
from resources.lib.comaddon import VSlog
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
import xbmc,xbmcvfs
import re
import threading
try:    
    import urllib3
except: 
    from requests.packages import urllib3

urllib3.disable_warnings()

Path = "special://temp"
video_file = xbmc.translatePath("/".join([Path ,'videotemp/']))

UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'
HEADERS = { 'User-Agent' : UA }

class cDlm3u8:

    def __init__(self):
        self.threads = ''
        self.event = threading.Event()
        self.urls_list = []
        self.filename = ''
        self.sHosterIdentifier = ''
        self.stop_all = False
        self.part_file = ''
        self.len_finish = 0
        self.modEXT = False
        
    def set_url_list(self,urlslist):
        self.urls_list = urlslist
        self.modEXT = True
        if xbmcvfs.exists(video_file) == 1:
            xbmcvfs.rmdir(video_file, True)
            xbmcvfs.mkdir("%s" % (video_file))
        else:
            xbmcvfs.mkdir("%s" % (video_file))

    def get_m3u8(self):
        Platforme = xbmc.getCondVisibility('System.Platform.Linux.RaspberryPi')

        if not Platforme == 1:
            oInputParameterHandler = cInputParameterHandler()
            sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')
            self.sHosterIdentifier = oInputParameterHandler.getValue('sHosterIdentifier')
            sFilename = oInputParameterHandler.getValue('sFileName')
            
            self.filename = re.sub(r'[\\/*?:"<>|, ]',".",sFilename)
            
            xHoster = __import__("resources.hosters."+self.sHosterIdentifier, fromlist=["cHoster"])

            self.part_file = "%s%s%s.%s" % (video_file, 'm3u8/', self.filename, self.sHosterIdentifier)

            if xbmcvfs.exists(self.part_file):
                from ast import literal_eval
                cFile = xbmcvfs.File(self.part_file)
                index,urls = literal_eval(cFile.read())
                if index[0] == 0 and urls == 0:
                    cFile.close()
                    self.sPlay()
                else:
                    self.urls_list = urls
                    cFile.close()
                
                    self.len_finish += index[0]
                    self.gen_listofThread(index[0])
                    self.start_thread()

            else:
                sHost = xHoster.cHoster()
                sHost.setUrl(sMediaUrl)
                sHost.setM3u8()
                api_call = sHost.getMediaLink()
                if api_call[0] == True:
                    test = self.set_m3u8(api_call[1])
                    if test == True:
                        self.gen_listofThread()
                        self.start_thread()
  
                else:
                    xbmc.executebuiltin('XBMC.Notification("Vstream","Format non supporté ou liens HS",3000)')
                
        else:
            xbmc.executebuiltin('XBMC.Notification("Vstream","Désactivé pour les raspberrys",3000)')

    def set_m3u8(self,sUrl):
        if xbmcvfs.exists(video_file) == 1:
            xbmcvfs.rmdir(video_file, True)
            xbmcvfs.mkdirs("%s%s" % (video_file, 'm3u8/'))
        else:
            xbmcvfs.mkdirs("%s%s" % (video_file, 'm3u8/'))

        req = urllib3.PoolManager(retries=False)
        rep = req.request('GET', sUrl, headers=HEADERS)
        stat = rep.status
        if stat:
            if not stat == 200:
                return False
            else:
                cFile = xbmcvfs.File("%s%s%s%s" % (video_file, 'm3u8/', self.filename, '.m3u8'), 'w')
                sHtmlContent = rep.data.splitlines()
                
                i = 0
                for x in sHtmlContent:  
                    if not x.startswith('#') and x != '':
                        cFile.write("%s%s%s%s" % (video_file, str(i), '.ts', '\n'))
                        if x.startswith('http'):
                            self.urls_list.append(x)
                        else:
                            self.urls_list.append('%s/%s' % (sUrl.rsplit('/',1)[0], x))
                            
                        i+=1

                    else:
                        if not x.startswith('#EXT-X-BYTERANGE'): #jawcloud
                            cFile.write("%s%s" % (x, '\n'))

                cFile.close()
                return True

        

    def gen_listofThread(self,start=0):
        self.threads = [threading.Thread(target=self.start_request, args=(sUrl[1], sUrl[0])) for sUrl in list(enumerate(self.urls_list,start))]


    def start_thread(self):
        #tune EXT-X-TARGETDURATION:4
        #netu EXT-X-TARGETDURATION:20 
        #rutube EXT-X-TARGETDURATION:8
        #vidlox EXT-X-TARGETDURATION:7
        #jawcloud EXT-X-TARGETDURATION:4
        
        if 'netu' in self.sHosterIdentifier:
            tD = 20
        elif 'tune' in self.sHosterIdentifier or 'jawcloud' in self.sHosterIdentifier:
            tD = 45
        elif 'rutube' in self.sHosterIdentifier or 'vidlox' in self.sHosterIdentifier:
            tD = 35   
        else:
            tD = 50
            
        splitlist = [self.threads[:5]] + [self.threads[5:][x:x+tD] for x in xrange(0, len(self.threads) - 5, tD)]
        
        self.event.set()
        for Treadlist in splitlist:
            self.len_finish += len(Treadlist)
            del self.urls_list[:len(Treadlist)]
            if not self.stop_all == True:
                self.Run(Treadlist)
            else:
                break

        if len(self.urls_list) ==  0 and self.modEXT == False:
            cFile = xbmcvfs.File(self.part_file,'w')
            cFile.write("%s" % ([[0],0]))
            cFile.close()

    def Run(self,Treadlist):
        for thread in Treadlist:
            thread.start()

        while self.event.is_set():                                                                                                                                       
            break

        self.event.clear()

        self.event.wait(0)

        while threading.activeCount() > 1 :
            pass
        else:
            self.event.set()
            
            if self.modEXT == False:
                if Treadlist[0].name == 'Thread-1':
                    self.sPlay()

                else:
                    if xbmc.getCondVisibility('Player.HasVideo') == 0 and xbmc.getCondVisibility('Window.IsActive(contextmenu)') == 1:
                        self.stop_all = False
                    if xbmc.getCondVisibility('Player.HasVideo') == 0 and xbmc.getCondVisibility('Window.IsActive(contextmenu)') == 0:
                        self.stop_all = True

                        cFile = xbmcvfs.File(self.part_file, 'w')
                        cFile.write("%s" % ([[self.len_finish],self.urls_list]))
                        cFile.close()

    def start_request(self,sUrl,Index):
        nbr_retry = urllib3.Retry(connect=3, backoff_factor=0.5)
        req = urllib3.PoolManager(retries=nbr_retry)
        rep = req.request('GET', sUrl, headers=HEADERS)

        cFile = xbmcvfs.File("%s%s%s" % (video_file, str(Index), '.ts'), 'w')
        cFile.write(rep.data)
        cFile.close()
        
    def sPlay(self):
        xbmc.executebuiltin("PlayMedia("+ video_file + "m3u8/" + self.filename + ".m3u8" + ")")

def merge_file():
    folders, files = xbmcvfs.listdir(video_file)
    tslist = sorted_nicely(files)
    nf = xbmcvfs.File("/".join([Path, 'myfile.ts']), 'w') 
    for ts in tslist:
        of = xbmcvfs.File(video_file + ts, 'r')
        nf.write(of.read())
        of.close()

    nf.close()    
    xbmcvfs.rmdir(video_file, True)

def sorted_nicely(X):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(X, key = alphanum_key)
