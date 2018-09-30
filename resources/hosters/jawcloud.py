#coding: utf-8
#Vstream https://github.com/Kodi-vStream/venom-xbmc-addons
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.hosters.hoster import iHoster

class cHoster(iHoster):

    def __init__(self):
        self.__sDisplayName = 'Jawcloud'
        self.__sFileName = self.__sDisplayName
        self.__sHD = ''
        self.m3u8 = False
        
    def getDisplayName(self):
        return  self.__sDisplayName

    def setDisplayName(self, sDisplayName):
        self.__sDisplayName = sDisplayName + ' [COLOR skyblue]'+self.__sDisplayName+'[/COLOR]'

    def setFileName(self, sFileName):
        self.__sFileName = sFileName

    def getFileName(self):
        return self.__sFileName

    def getPluginIdentifier(self):
        return 'jawcloud'

    def setHD(self, sHD):
        self.__sHD = ''

    def getHD(self):
        return self.__sHD

    def isDownloadable(self):
        return False
        
    def isM3u8(self):
        return ''
        
    def setM3u8(self):
        self.m3u8 = True

    def setUrl(self, sUrl):
        self.__sUrl = str(sUrl)

    def checkUrl(self, sUrl):
        return True

    def __getUrl(self, media_id):
        return
        
    def getMediaLink(self):
        return self.__getMediaLinkForGuest()

    def __getMediaLinkForGuest(self):

        api_call =''

        oRequest = cRequestHandler(self.__sUrl)
        sHtmlContent = oRequest.request()

        oParser = cParser()
        sPattern = '<source.+?src="(.+?)"'
        
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0]):
            api_call = aResult[1][0]

        if (api_call):
            if self.m3u8 == True:
                api_call = api_call.rsplit(',', 1)[0].replace(',','') + '/iframes-v1-a1.m3u8'
                return True, api_call
            else:
                return True, api_call
            
        return False, False
        
#https://s9.jawcloud.co/hls/,xxxxx,.urlset/master.m3u8
#https://s9.jawcloud.co/hls/xxxxx/iframes-v1-a1.m3u8
