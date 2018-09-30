#-*- coding: utf-8 -*-
# https://github.com/Kodi-vStream/venom-xbmc-addons
from resources.hosters.hoster import iHoster
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.gui.gui import cGui
from resources.lib.comaddon import dialog

import urllib

class cHoster(iHoster):

    def __init__(self):
        self.__sDisplayName = 'RuTube'
        self.__sFileName = self.__sDisplayName
        self.m3u8 = False
        
    def getDisplayName(self):
        return  self.__sDisplayName

    def setDisplayName(self, sDisplayName):
        self.__sDisplayName = sDisplayName + ' [COLOR skyblue]'+self.__sDisplayName+'[/COLOR]'

    def setFileName(self, sFileName):
        self.__sFileName = sFileName

    def getFileName(self):
        return self.__sFileName

    def setUrl(self, sUrl):
        self.__sUrl = sUrl
        self.__sUrl = self.__sUrl.replace('http://', '')
        self.__sUrl = self.__sUrl.replace('https://', '')
        self.__sUrl = self.__sUrl.replace('rutube.ru/video/embed/', '')
        self.__sUrl = self.__sUrl.replace('video.rutube.ru/', '')
        self.__sUrl = self.__sUrl.replace('rutube.ru/video/', '')
        self.__sUrl = self.__sUrl.replace('rutube.ru/play/embed/', '')
        self.__sUrl = 'http://rutube.ru/play/embed/' + str(self.__sUrl)

    def __getIdFromUrl(self,url):
        sPattern = "\/play\/embed\/(\w+)" #au cas ou test \/play\/embed\/(\w+)(?:\?|\\?)
        oParser = cParser()
        aResult = oParser.parse(url, sPattern)
        if (aResult[0] == True):
            return aResult[1][0]

        return ''

    def __getRestFromUrl(self,url):
        #sPattern = "\?([\w]=[\w-]+)"
        sPattern = "\?([^ ]+)"
        oParser = cParser()
        aResult = oParser.parse(url, sPattern)
        if (aResult[0] == True):
            return aResult[1][0]

        return ''

    def getPluginIdentifier(self):
        return 'rutube'

    def isDownloadable(self):
        return False

    def isM3u8(self):
        return ''
        
    def setM3u8(self):
        self.m3u8 = True

    def checkUrl(self, sUrl):
        return True

    def getUrl(self):
        return self.__sUrl

    def getMediaLink(self):
        return self.__getMediaLinkForGuest()

    def __getMediaLinkForGuest(self):
        stream_url = False

        oParser = cParser()

        sID = self.__getIdFromUrl(self.__sUrl)
        sRestUrl = self.__getRestFromUrl(self.__sUrl)

        api = 'http://rutube.ru/api/play/options/' + sID+ '/?format=json&no_404=true&referer=' + urllib.quote(self.__sUrl,safe='')
        api = api + '&' + sRestUrl

        oRequest = cRequestHandler(api)
        sHtmlContent = oRequest.request()

        sPattern = '"m3u8": *"([^"]+)"'
        aResult = oParser.parse(sHtmlContent, sPattern)
       
        if not (aResult):
            sPattern = '"default": *"([^"]+)"'
            aResult = oParser.parse(sHtmlContent, sPattern)

        if (aResult[0] == True):
            url2 = aResult[1][0]
        else:
            return False,False

        oRequest = cRequestHandler(url2)
        sHtmlContent = oRequest.request()

        sPattern = '(http.+?\?i=)([0-9x_]+)'
        aResult = oParser.parse(sHtmlContent, sPattern)

        if (aResult[0] == True):
            url=[]
            qua=[]

            for aEntry in aResult[1]:
                url.append(aEntry[0]+aEntry[1])
                qua.append(aEntry[1])

            #tableau
            stream_url = dialog().VSselectqual(qua, url)

        if (stream_url):
            if self.m3u8 == True and stream_url.endswith('m3u8'):
                return True, stream_url
            else:
                return True, stream_url

        return False, False
