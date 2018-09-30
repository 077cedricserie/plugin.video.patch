#-*- coding: utf-8 -*-
#Vstream https://github.com/Kodi-vStream/venom-xbmc-addons
from resources.lib.handler.requestHandler import cRequestHandler 
from resources.lib.parser import cParser 
from resources.hosters.hoster import iHoster
from resources.lib.comaddon import dialog, isKrypton

class cHoster(iHoster):

    def __init__(self):
        if not (isKrypton() == True):
            self.__sDisplayName = '(Windows\Android Nécessite Kodi17)' + ' ' + 'Vidlox'
        else:
            self.__sDisplayName = 'Vidlox'        
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
        return 'vidlox'
        
    def setHD(self, sHD):
        self.__sHD = ''
        
    def getHD(self):
        return self.__sHD
        
    def isM3u8(self):
        return ''
        
    def setM3u8(self):
        self.m3u8 = True
        
    def isDownloadable(self):
        return True

    def setUrl(self, sUrl):
        self.__sUrl = str(sUrl)

    def checkUrl(self, sUrl):
        return True

    def __getUrl(self, media_id):
        return
    
    def getMediaLink(self):
        return self.__getMediaLinkForGuest()

    def __getMediaLinkForGuest(self):
        api_call = ''
        
        oParser = cParser()
        oRequest = cRequestHandler(self.__sUrl)
        sHtmlContent = oRequest.request()
        #accelère le traitement
        sHtmlContent = oParser.abParse(sHtmlContent, 'var player', 'vvplay')
        
        if self.m3u8 == True:
            sPattern =  '([^"]+\.m3u8)'
            aResult = oParser.parse(sHtmlContent, sPattern)
            if (aResult[0] == True):
                api_call = aResult[1][0].rsplit(',', 1)[0].replace(',','') + '/index-v1-a1.m3u8'

        else:
            sPattern =  '([^"]+\.mp4)'
            aResult = oParser.parse(sHtmlContent, sPattern)
            if (aResult[0] == True):
                #initialisation des tableaux
                url=[]
                qua=["HD","SD"] #bidouille evite m3u8

                #Replissage des tableaux
                for i in aResult[1]:
                    url.append(str(i))

                #dialog qualiter
                api_call = dialog().VSselectqual(qua,url)
  
        if (api_call):
            return True, api_call 

        return False, False
