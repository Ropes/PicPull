from html.parser import HTMLParser, HTMLParseError
import urllib.request
from urllib.parse import urlparse
from xml.parsers.expat import ParserCreate, ExpatError, errors
import os, sys, re

DEBUG = False

#HTMLParser class definition for returning the list of image urls to an imgur 
class HtmlParse(HTMLParser):
  def __init__(self, imgs):
    HTMLParser.__init__(self)
    self.img = True 
    self.img_list = imgs

  def  handle_starttag(self, tag, attrs):
    #print(tag)
    if tag == 'img' and attrs[0] == ('class', 'unloaded'):
      self.img_list.append(attrs[1][1])
      if(DEBUG):print(attrs[1][1])
  def handle_endtag(self, tag):
    x = True
  def handle_data(self, data):
    if self.img:
      #print( 'Data:', data )
      self.img = False


def get_html(url):
  try:
    h = urllib.request.urlopen(url)
    return h.read()
  except(URLError):
    print('Error printing page')
    return None

def set_dir(todir):
  try:
    os.chdir(todir)
  except:
    print( 'Error setting directory:', OSError )

def download_img(file_name, url):
  
  #Open the http url
  try:
    f = urllib.request.urlopen(url)

    #Open a file to write(Needs to be set to allow bytes 'b')
    file_ = open(file_name, 'wb')
    file_.write(f.read())
    file_.close()

  except HTTPError as err:
    print('HttpError:',err, url)
  except URLError as err:
    print('URLError:', err, url)

def get_name(url):
  p = urlparse(url)
  path = p.path
  
  return re.findall('/a/(.*)', path).pop()
 

def imgur_album_pull(url, custom_name):
  #html = get_html('http://qkme.me/35p92k') 
  html = get_html(url)
  if custom_name == None:
    file_base = str(get_name(url))
  else:
    file_base = custom_name

  img_list = []

  try:
    hp = HtmlParse(img_list)
    hp.feed(str(html))
  except HTMLParseError as err:
    print('HTMLParse Error:', err)

  if(DEBUG):  print(img_list)
  
  i = 0
  for url in img_list:
    file_name  = file_base + str(i) + '.jpg'
    print('Downloading: ',file_name, 'from', url)
    download_img(file_name, url)
    i += 1

    
#Parses out the correct file directory from the set.txt file based on the given choice/mode
def read_setup(choice):
  f = open('set.txt', 'r')
  content = f.read()
  f.close()
  
  arr = content.split('\n')
  chdir = ''
  for line in arr:
    if(DEBUG): print('Parsing line:', line)
    x = line.split(':')
    if x[0] == choice:
      return x[1]

  #If choice not found return None
  return None
  
def parse_args(args):
  if len(args) > 2:
    p = ''
    x = args[2:]
    for i in x:
      p += str(i)


def main():
  args = sys.argv[1:]
  todir = '.'

  print(args) 

 if __name__ == '__main__':
  url = 'http://imgur.com/a/WSP8q'
  #imgur_album_pull(url)
  main()



