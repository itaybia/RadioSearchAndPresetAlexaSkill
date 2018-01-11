from tunein import TuneIn

import urllib
import urllib2

from random import randint
import json as _json

BASE_URL = 'opml.radiotime.com/'


class AlexaTuneIn(TuneIn):
    def call_tunein_url(self, url):
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        result = _json.load(f)
        f.close()
        return result


    def browse_music(self):
        '''Creates a list of radio stations local to the caller, typically using IP geo-location.
        '''
        params = [{'param': 'c', 'value': 'music'}]
        result = self.call_tunein('Browse.ashx', params)
        if (self.result_ok(result)):
            raise TuneIn.TuneInError(self.result_status(
                result), self.result_fault(result), self.result_fault_code(result))
        else:
            return result['body']


    def get_artist_related_stations(self, query):
        '''Search for stations related to an artist.
        '''
        params = [{'param': 'query', 'value': query}]
        result = self.call_tunein('Search.ashx', params)
        if (self.result_ok(result)):
            raise TuneIn.TuneInError(self.result_status(
                result), self.result_fault(result), self.result_fault_code(result))

        for x in result['body']:
            if (x.get('type') is not None and x.get('text') is not None and x['type'] == 'link' and x['text'].startswith('Artist: ')):
                self.log_debug("Stations related to artist: " + query + " were found")

                params = {'param': 'types', 'value': 'station'}
                for param in self._global_params:
                    if (param['value']):
                        params[param['param']] = param['value']
                url = x['URL'] + '&' + urllib.urlencode(params)
                self.log_debug('search_artist_link - URL: %s' % url)
                result = self.call_tunein_url(url)
                if (self.result_ok(result)):
                    raise TuneIn.TuneInError(self.result_status(
                        result), self.result_fault(result), self.result_fault_code(result))
                else:
                    return result['body']
        return None


    def get_random_station_from_list(self, stations):
        if (stations is None or len(stations) == 0):
            return None
        randomIndex = (randint(0, len(stations) - 1))
        while len(stations) > 0 and ('item' not in stations[randomIndex] or stations[randomIndex]['item'] != 'station'):
            del stations[randomIndex]
            randomIndex = (randint(0, len(stations)))
        if len(stations) == 0:
            return None
        return stations[randomIndex]


    def get_secure_url(self, url):
        if url is None:
            return None
        elif url.startswith('https://'):
            return url
        elif url.startswith('http://'):
            return 'https://' + url[7:]
        else:
            self.log_debug("get_secure_url bad URL: " + url)
            return None


    def get_random_station(self, stations):
        if stations is None:
            return None
        station = self.get_random_station_from_list(stations)
        if station is None:
            return None
        secureUrl = self.get_secure_url(station['URL'])
        if (secureUrl is not None):
            station['URL'] = secureUrl
        return station


    def get_random_artist_station(self, artist):
        self.log_debug('get_artist_station for artist: ' + artist)
        stations = self.get_artist_related_stations(artist)
        return self.get_random_station(stations)


    def get_music_genre_stations_list(self, genre):
        genres = self.browse_music()
        for g in genres:
            # find the specific genre in the list of genres
            if g['text'].lower() == genre.lower() or g['text'].lower() == (genre.lower() + ' music'):
                # get the genre's url in json format
                params = {'filter': 's:popular'}
                for param in self._global_params:
                    if (param['value']):
                        params[param['param']] = param['value']
                genre_url = g['URL'] + '&' + urllib.urlencode(params)
                self.log_debug('get_music_genre_url - genre: %s, URL: %s' % (genre, genre_url))

                # access the genre url and find the stations in it
                result = self.call_tunein_url(genre_url)
                if (self.result_ok(result)):
                    raise TuneIn.TuneInError(self.result_status(
                        result), self.result_fault(result), self.result_fault_code(result))
                else:
                    return result['body']
        return None


    def get_random_music_genre_station(self, genre):
        stations = self.get_music_genre_stations_list(genre)
        return self.get_random_station(stations)


    def get_random_music_station(self, query):
        stations = self.search(query, types='station')
        return self.get_random_station(stations)


    @staticmethod
    def get_station_name(station):
        return station['text']


    @staticmethod
    def get_station_url(station):
        return station['URL']
