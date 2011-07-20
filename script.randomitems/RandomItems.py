# *  Thanks to:
# *
# *  Nuka for the original RecentlyAdded.py on which this is based
# *
# *  ppic, Hitcher & ronie for the updates

import xbmc, xbmcgui, xbmcaddon
import re, sys, os, random
import xml.dom.minidom

__scriptID__ = "script.randomitems"

class Main:
    # grab the home window
    WINDOW = xbmcgui.Window( 10000 )

    def _clear_properties( self ):
        # reset totals property for visible condition
        self.WINDOW.clearProperty( "RandomMovie.Count" )
        self.WINDOW.clearProperty( "RandomEpisode.Count" )
        self.WINDOW.clearProperty( "RandomSong.Count" )
        self.WINDOW.clearProperty( "RandomAlbum.Count" )
        self.WINDOW.clearProperty( "RandomAddon.Count" )
        # we clear title for visible condition
        for count in range( self.LIMIT ):
            self.WINDOW.clearProperty( "RandomMovie.%d.Title" % ( count ) )
            self.WINDOW.clearProperty( "RandomEpisode.%d.Title" % ( count ) )
            self.WINDOW.clearProperty( "RandomSong.%d.Title" % ( count ) )
            self.WINDOW.clearProperty( "RandomAlbum.%d.Title" % ( count ) )
            self.WINDOW.clearProperty( "RandomAddon.%d.Name" % ( count ) )

    def _parse_argv( self ):
        try:
            # parse sys.argv for params
            params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
        except:
            # no params passed
            params = {}
        # set our preferences
        self.LIMIT = int( params.get( "limit", "5" ) )
        self.UNPLAYED = params.get( "unplayed", "False" )
        self.PLAY_TRAILER = params.get( "trailer", "False" )
        self.ALARM = int( params.get( "alarm", "0" ) )
        self.ALBUMID = params.get( "albumid", "" )

    def _set_alarm( self ):
        # only run if user/skinner preference
        if ( not self.ALARM ): return
        # set the alarms command
        command = "XBMC.RunScript(%s,limit=%d&unplayed=%s&trailer=%s&alarm=%d)" % ( __scriptID__, self.LIMIT, str( self.UNPLAYED ), str( self.PLAY_TRAILER ), self.ALARM, )
        xbmc.executebuiltin( "AlarmClock(RandomItems,%s,%d,true)" % ( command, self.ALARM, ) )

    def __init__( self ):
        # parse argv for any preferences
        self._parse_argv()
        # check if we were executed internally
        if self.ALBUMID:
            self._Play_Album( self.ALBUMID )
        else:
            # clear properties
            self._clear_properties()
            # set any alarm
            self._set_alarm()
            # fetch media info
            self._fetch_movie_info()
            self._fetch_episode_info()
            self._fetch_album_info()
            self._fetch_song_info()
            self._fetch_addon_info()

    def _fetch_movie_info( self ):
        # query the database
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"fields": ["playcount", "year", "plot", "runtime", "fanart", "thumbnail", "file", "trailer", "rating"] }, "id": 1}')
        # separate the records
        json_response = re.compile( "{(.*?)}", re.DOTALL ).findall(json_query)
        json_response.pop(0)
        # get total value
        total = str( len( json_response ) )
        # enumerate thru our records
        count = 0
        while count < self.LIMIT:
            count += 1
            # check if we don't run out of items before LIMIT is reached
            if len( json_response ) == 0:
                return
            # select a random item
            item = random.choice( json_response )
            # remove the item from our list
            json_response.remove( item )
            # find values
            if self.UNPLAYED == "True":
                findplaycount = re.search( '"playcount":(.*?),"', item )
                if findplaycount:
                    playcount = findplaycount.group(1)
                    if int( playcount ) > 0:
                        count = count - 1
                        continue
            findtitle = re.search( '"label":"(.*?)","', item )
            if findtitle:
                title = findtitle.group(1)
            else:
                title = ''
            findrating = re.search( '"rating":(.*?),"', item )
            if findrating:
                rating = '%.1f' % float( findrating.group(1) )
            else:
                rating = ''
            findyear = re.search( '"year":(.*)', item )
            if findyear:
                year = findyear.group(1)
            else:
                year = ''
            findplot = re.search( '"plot":"(.*?)","', item )
            if findplot:
                plot = findplot.group(1)
            else:
                plot = ''
            findrunningtime = re.search( '"runtime":"(.*?)","', item )
            if findrunningtime:
                runningtime = findrunningtime.group(1)
            else:
                runningtime = ''
            findpath = re.search( '"file":"(.*?)","', item )
            if findpath:
                path = findpath.group(1)
            else:
                path = ''
            findtrailer = re.search( '"trailer":"(.*?)","', item )
            if findtrailer:
                trailer = findtrailer.group(1)
                if self.PLAY_TRAILER == "True":
                    path = trailer
            else:
                trailer = ''
            findfanart = re.search( '"fanart":"(.*?)","', item )
            if findfanart:
                fanart = findfanart.group(1)
            else:
                fanart = ''
            findthumb = re.search( '"thumbnail":"(.*?)","', item )
            if findthumb:
                thumb = findthumb.group(1)
            else:
                thumb = ''
            # set our properties
            self.WINDOW.setProperty( "RandomMovie.%d.Title" % ( count ), title )
            self.WINDOW.setProperty( "RandomMovie.%d.Rating" % ( count ), rating )
            self.WINDOW.setProperty( "RandomMovie.%d.Year" % ( count ), year)
            self.WINDOW.setProperty( "RandomMovie.%d.Plot" % ( count ), plot )
            self.WINDOW.setProperty( "RandomMovie.%d.RunningTime" % ( count ), runningtime )
            self.WINDOW.setProperty( "RandomMovie.%d.Path" % ( count ), path )
            self.WINDOW.setProperty( "RandomMovie.%d.Trailer" % ( count ), trailer )
            self.WINDOW.setProperty( "RandomMovie.%d.Fanart" % ( count ), fanart )
            self.WINDOW.setProperty( "RandomMovie.%d.Thumb" % ( count ), thumb )
            self.WINDOW.setProperty( "RandomMovie.Count", total )

    def _fetch_episode_info( self ):
        # query the database
        tvshowid = 2
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "fields": ["playcount", "season", "episode", "showtitle", "plot", "fanart", "thumbnail", "file", "rating"] }, "id": 1}')
        # separate the records
        json_response = re.compile( "{(.*?)}", re.DOTALL ).findall(json_query)
        json_response.pop(0)
        # get total value
        total = str( len( json_response ) )
        # enumerate thru our records
        count = 0
        while count < self.LIMIT:
            count += 1
            # check if we don't run out of items before LIMIT is reached
            if len( json_response ) == 0:
                return
            # select a random item
            item = random.choice( json_response )
            # remove the item from our list
            json_response.remove( item )
            # find values
            if self.UNPLAYED == "True":
                findplaycount = re.search( '"playcount":(.*?),"', item )
                if findplaycount:
                    playcount = findplaycount.group(1)
                    if int( playcount ) > 0:
                        count = count - 1
                        continue
            findtitle = re.search( '"label":"(.*?)","', item )
            if findtitle:
                title = findtitle.group(1)
            else:
                title = ''
            findshowtitle = re.search( '"showtitle":"(.*?)","', item )
            if findshowtitle:
                showtitle = findshowtitle.group(1)
            else:
                showtitle = ''
            findseason = re.search( '"season":(.*?),"', item )
            if findseason:
                season = findseason.group(1)
            else:
                season = ''
            findepisode = re.search( '"episode":(.*?),"', item )
            if findepisode:
                episode = findepisode.group(1)
            else:
                episode = ''
            findrating = re.search( '"rating":(.*?),"', item )
            if findrating:
                rating = "%.1f" % float( findrating.group(1) )
            else:
                rating = ''
            findplot = re.search( '"plot":"(.*?)","', item )
            if findplot:
                plot = findplot.group(1)
            else:
                plot = ''
            findpath = re.search( '"file":"(.*?)","', item )
            if findpath:
                path = findpath.group(1)
            else:
                path = ''
            findfanart = re.search( '"fanart":"(.*?)","', item )
            if findfanart:
                fanart = findfanart.group(1)
            else:
                fanart = ''
            findthumb = re.search( '"thumbnail":"(.*?)"', item )
            if findthumb:
                thumb = findthumb.group(1)
            else:
                thumb = ''
            episodeno = "s%se%s" % ( season,  episode, )
            # set our properties
            self.WINDOW.setProperty( "RandomEpisode.%d.ShowTitle" % ( count ), showtitle  )
            self.WINDOW.setProperty( "RandomEpisode.%d.EpisodeTitle" % ( count ), title )
            self.WINDOW.setProperty( "RandomEpisode.%d.EpisodeNo" % ( count ), episodeno )
            self.WINDOW.setProperty( "RandomEpisode.%d.EpisodeSeason" % ( count ), season )
            self.WINDOW.setProperty( "RandomEpisode.%d.EpisodeNumber" % ( count ), episode )
            self.WINDOW.setProperty( "RandomEpisode.%d.Rating" % ( count ), rating )
            self.WINDOW.setProperty( "RandomEpisode.%d.Plot" % ( count ), plot )
            self.WINDOW.setProperty( "RandomEpisode.%d.Path" % ( count ), path )
            self.WINDOW.setProperty( "RandomEpisode.%d.Fanart" % ( count ), fanart )
            self.WINDOW.setProperty( "RandomEpisode.%d.Thumb" % ( count ), thumb )
            self.WINDOW.setProperty( "RandomEpisode.Count", total )

    def _fetch_album_info( self ):
        # query the database
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"fields": ["artist", "year", "thumbnail", "fanart", "rating"] }, "id": 1}')
        # separate the records
        json_response = re.compile( "{(.*?)}", re.DOTALL ).findall(json_query)
        json_response.pop(0)
        # get total value
        total = str( len( json_response ) )
        # enumerate thru our records
        count = 0
        while count < self.LIMIT:
            count += 1
            # check if we don't run out of items before LIMIT is reached
            if len( json_response ) == 0:
                return
            # select a random item
            item = random.choice( json_response )
            # remove the item from our list
            json_response.remove( item )
            # find values
#            if self.UNPLAYED == "True":
#                findplaycount = re.search( '"playcount":(.*?),"', item )
#                if findplaycount:
#                    playcount = findplaycount.group(1)
#                    if int( playcount ) > 0:
#                        count = count - 1
#                        continue
            findtitle = re.search( '"label":"(.*?)","', item )
            if findtitle:
                title = findtitle.group(1)
            else:
                title = ''
            findrating = re.search( '"rating":(.*?),"', item )
            if findrating:
                rating = findrating.group(1)
                if rating == '48':
                    rating = ''
            else:
                rating = ''
            findyear = re.search( '"year":(.*)', item )
            if findyear:
                year = findyear.group(1)
            else:
                year = ''
            findartist = re.search( '"artist":"(.*?)","', item )
            if findartist:
                artist = findartist.group(1)
            else:
                artist = ''
            findpath = re.search( '"albumid":(.*?),"', item )
            if findpath:
                path = 'XBMC.RunScript(' + __scriptID__ + ',albumid=' + findpath.group(1) + ')'
            else:
                path = ''
            findfanart = re.search( '"fanart":"(.*?)","', item )
            if findfanart:
                fanart = findfanart.group(1)
            else:
                fanart = ''
            findthumb = re.search( '"thumbnail":"(.*?)","', item )
            if findthumb:
                thumb = findthumb.group(1)
            else:
                thumb = ''
            # set our properties
            self.WINDOW.setProperty( "RandomAlbum.%d.Title" % ( count ), title )
            self.WINDOW.setProperty( "RandomAlbum.%d.Rating" % ( count ), rating )
            self.WINDOW.setProperty( "RandomAlbum.%d.Year" % ( count ), year )
            self.WINDOW.setProperty( "RandomAlbum.%d.Artist" % ( count ), artist )
            self.WINDOW.setProperty( "RandomAlbum.%d.Path" % ( count ), path )
            self.WINDOW.setProperty( "RandomAlbum.%d.Fanart" % ( count ), fanart )
            self.WINDOW.setProperty( "RandomAlbum.%d.Thumb" % ( count ), thumb )
            self.WINDOW.setProperty( "RandomAlbum.Count", total )

    def _fetch_song_info( self ):
        # query the database
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"fields": ["playcount", "artist", "album", "year", "file", "thumbnail", "fanart", "rating"] }, "id": 1}')
        # separate the records
        json_response = re.compile( "{(.*?)}", re.DOTALL ).findall(json_query)
        json_response.pop(0)
        # get total value
        total = str( len( json_response ) )
        # enumerate thru our records
        count = 0
        while count < self.LIMIT:
            count += 1
            # check if we don't run out of items before LIMIT is reached
            if len( json_response ) == 0:
                return
            # select a random item
            item = random.choice( json_response )
            # remove the item from our list
            json_response.remove( item )
            # find values
            if self.UNPLAYED == "True":
                findplaycount = re.search( '"playcount":(.*?),"', item )
                if findplaycount:
                    playcount = findplaycount.group(1)
                    if int( playcount ) > 0:
                        count = count - 1
                        continue
            findtitle = re.search( '"label":"(.*?)","', item )
            if findtitle:
                title = findtitle.group(1)
            else:
                title = ''
            findrating = re.search( '"rating":(.*?),"', item )
            if findrating:
                rating = str( int( findrating.group(1) ) - 48)
            else:
                rating = ''
            findyear = re.search( '"year":(.*)', item )
            if findyear:
                year = findyear.group(1)
            else:
                year = ''
            findartist = re.search( '"artist":"(.*?)","', item )
            if findartist:
                artist = findartist.group(1)
            else:
                artist = ''
            findalbum = re.search( '"album":"(.*?)","', item )
            if findalbum:
                album = findalbum.group(1)
            else:
                album = ''
            findpath = re.search( '"file":"(.*?)","', item )
            if findpath:
                path = findpath.group(1)
            else:
                path = ''
            findfanart = re.search( '"fanart":"(.*?)","', item )
            if findfanart:
                fanart = findfanart.group(1)
            else:
                fanart = ''
            findthumb = re.search( '"thumbnail":"(.*?)","', item )
            if findthumb:
                thumb = findthumb.group(1)
            else:
                thumb = ''
            # set our properties
            self.WINDOW.setProperty( "RandomSong.%d.Title" % ( count ), title )
            self.WINDOW.setProperty( "RandomSong.%d.Rating" % ( count ), rating )
            self.WINDOW.setProperty( "RandomSong.%d.Year" % ( count ), year )
            self.WINDOW.setProperty( "RandomSong.%d.Artist" % ( count ), artist )
            self.WINDOW.setProperty( "RandomSong.%d.Album" % ( count ), album )
            self.WINDOW.setProperty( "RandomSong.%d.Path" % ( count ), path )
            self.WINDOW.setProperty( "RandomSong.%d.Fanart" % ( count ), fanart )
            self.WINDOW.setProperty( "RandomSong.%d.Thumb" % ( count ), thumb )
            self.WINDOW.setProperty( "RandomSong.Count", total )

    def _fetch_addon_info( self ):
        # initialize our list
        addonlist = []
        # list the contents of the addons folder
        addonpath = xbmc.translatePath( 'special://home/addons/' )
        addons = os.listdir(addonpath)
        # find directories in the addons folder
        for item in addons:
            if os.path.isdir(os.path.join(addonpath, item)):
                # find addon.xml in the addon folder
                addonfile = os.path.join(addonpath, item, 'addon.xml')
                if os.path.exists(addonfile):
                    # find addon id
                    addonfilecontents = xml.dom.minidom.parse(addonfile)
                    for addonentry in addonfilecontents.getElementsByTagName("addon"): 
                        addonid = addonentry.getAttribute("id")
                    # find plugins and scripts
                    try:
                        addontype = xbmcaddon.Addon(id=addonid).getAddonInfo('type')
                        if (addontype == 'xbmc.python.script') or (addontype == 'xbmc.python.pluginsource'):
                            addonlist.append(addonid)
                    except:
                        pass
                    addonfilecontents.unlink()
        # get total value
        total = str( len( addonlist ) )
        # count thru our addons
        count = 0
        while count < self.LIMIT:
            count += 1
            # check if we don't run out of items before LIMIT is reached
            if len(addonlist) == 0:
                return
            # select a random item
            addonid = random.choice(addonlist)
            # remove the item from our list
            addonlist.remove(addonid)
            # set properties
            self.WINDOW.setProperty( "RandomAddon.%d.Name" % ( count ), xbmcaddon.Addon(id=addonid).getAddonInfo('name') )
            self.WINDOW.setProperty( "RandomAddon.%d.Author" % ( count ), xbmcaddon.Addon(id=addonid).getAddonInfo('author') )
            self.WINDOW.setProperty( "RandomAddon.%d.Summary" % ( count ), xbmcaddon.Addon(id=addonid).getAddonInfo('summary') )
            self.WINDOW.setProperty( "RandomAddon.%d.Version" % ( count ), xbmcaddon.Addon(id=addonid).getAddonInfo('version') )
            self.WINDOW.setProperty( "RandomAddon.%d.Path" % ( count ), xbmcaddon.Addon(id=addonid).getAddonInfo('id') )
            self.WINDOW.setProperty( "RandomAddon.%d.Fanart" % ( count ), xbmcaddon.Addon(id=addonid).getAddonInfo('fanart') )
            self.WINDOW.setProperty( "RandomAddon.%d.Thumb" % ( count ), xbmcaddon.Addon(id=addonid).getAddonInfo('icon') )
            self.WINDOW.setProperty( "RandomAddon.Count", total )

    def _Play_Album( self, ID ):
        # query the database
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"fields": ["file", "fanart"], "albumid":%s }, "id": 1}' % ID)
        # separate the records
        json_response = re.compile( "{(.*?)}", re.DOTALL ).findall(json_query)
        json_response.pop(0)
        # create a playlist
        playlist = xbmc.PlayList(0)
        # clear the playlist
        playlist.clear()
        # enumerate thru our records
        for item in json_response:
            # find values
            findsongpath = re.search( '"file":"(.*?)","label"', item )
            if findsongpath:
                song = findsongpath.group(1)
            else:
                song = ''
            findfanart = re.search( '"fanart":"(.*?)","file"', item )
            if findfanart:
                fanart = findfanart.group(1)
            else:
                fanart = ''
            # create playlist item
            listitem = xbmcgui.ListItem()
            # add fanart image to the playlist item
            listitem.setProperty( "fanart_image", fanart )
            # add item to the playlist
            playlist.add( url=song, listitem=listitem )
        # play the playlist
        xbmc.Player().play( playlist )

if ( __name__ == "__main__" ):
    Main()
