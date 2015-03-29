#!/usr/bin/env python
import requests,re,os

def fetch(url):
  sublist = map(str.lower,open('showlist','r').read().split('\n'))
  headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0'}
  
  fields = ('link','name','season','episode','age','seed','key')
  # precompiled regex's
  tr_table = re.compile('<table.*?class="data".*?>(.*?)</table>',re.S)
  tr_split = re.compile('(\t|\n|\r)+')
  tr_item = re.compile('<tr class="(?:even|odd)" id="torrent_uploaded_torrents\d+">.*?<a title="Download torrent file" href="(.*?)" class="idownload icon16">.*?<a href=".*?" class="cellMainLink">(.*?) (?:S(\d+)E(\d+)|(\d+) (\d+ \d+)).*?\[ettv\]</a>.*?<td class="center">(\d+)&nbsp;(?:hour|min)(?:s?)</td>.*?<td class="green center">(\d+)</td>.*?</tr>',re.S) 

  # fetch uploads page
  #TODO: fetch at least 3 pages
  feed = requests.get(url,headers=headers).text.encode('utf-8')
  # extracting table to narrow down search domain for tr_item
  table = tr_split.sub('',tr_table.findall(feed)[0])
  # 1. extract data from each row, then filter out "None" fields
  # 2. generate a unique key with the form "<name>.<season/year>.<episode/date>.torrent"
  #    keys are lowercased to increase the rate of collisions.
  # 3. combine data with fields and convert it to a dictionary
  items = map(lambda e: dict(zip(fields, e+(("%s.%s.%s.torrent"%e[1:4]).lower(),))), map(lambda e: filter(bool, e), tr_item.findall(table)))
  # for each unique key, cross-match it with subscription list and pick the most seeded torrent.
  # a "None" value is added to each match as a failsafe if there is no hit. 
  # they are removed at the end of the process.
  return filter(bool,map(lambda e: (sorted(filter(lambda f: f['key']==e and f['name'].lower() in sublist,items),key=lambda e:int(e['seed']),reverse=True)+[None])[0], set(map(lambda e: e['key'], items))))

def download(torrents,directory):
  headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0'}
  links = map(lambda e: (e['key'],e['link']), torrents)
  #create download dir
  write = lambda f,d: f.write(d) 
  check = lambda c,t,f: {True:t,False:f}[c]()
  check(not os.path.isdir(directory), lambda: os.mkdir(directory), int)
  #download torrent file and use key as filename
  map(lambda e: write(open('%s/%s'%(directory,e[0]),'wb'),requests.get(e[1],headers=headers).content),links)

if __name__ == '__main__':
    #subscription source
    subs_url  = 'http://kickass.to/user/ettv/uploads/?page=1'
    #download directory
    directory = 'torrents'

    download(fetch(subs_url),directory)
