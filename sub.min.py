#!/usr/bin/env python
import requests,re,os
def fetch(url):
  sublist = map(str.lower,open('showlist','r').read().split('\n')) 
  fields = ('l','n','s','e','a','d','k')
  tr_table = re.compile('<table.*?class="data".*?>(.*?)</table>',re.S)
  tr_split = re.compile('(\t|\n)+')
  tr_item = re.compile('<tr class="(?:even|odd)" id="torrent_uploaded_torrents\d+">.*?<a title="Download torrent file" href="(.*?)" class="idownload icon16">.*?<a href=".*?" class="cellMainLink">(.*?) (?:S(\d+)E(\d+)|(\d+) (\d+ \d+)).*?\[ettv\]</a>.*?<td class="center">(\d+)&nbsp;(?:hour|min)(?:s?)</td>.*?<td class="green center">(\d+)</td>.*?</tr>',re.S) 
  items = map(lambda e: dict(zip(fields, e+(("%s.%s.%s.torrent"%e[1:4]).lower(),))), map(lambda e: filter(bool, e), tr_item.findall(tr_split.sub('',tr_table.findall(requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0'}).text.encode('utf-8'))[0]))))
  return filter(bool,map(lambda e: (sorted(filter(lambda f: f['k']==e and f['n'].lower() in sublist,items),key=lambda e:int(e['d']),reverse=True)+[None])[0], set(map(lambda e: e['k'], items))))
def download(torrents,directory): 
  (lambda c,t,f: {True:t,False:f}[c]())(not os.path.isdir(directory), lambda: os.mkdir(directory), int)
  map(lambda e: (lambda f,d: f.write(d))(open('%s/%s'%(directory,e[0]),'wb'),requests.get(e[1],headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0'}).content),map(lambda e: (e['k'],e['l']), torrents))
if __name__ == '__main__': download(fetch('http://kickass.to/user/ettv/uploads/?page=1'),'torrents')
