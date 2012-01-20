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
 

def imgur_album_pull(action):
  url = action[1]
  custom_name = action[2]
  html = get_html(url)
  if custom_name == '':
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

#QuickMeme image puller modeled after the one from old code, uses RegExes which is bad but I'm too tired to update it right now.
#UPDATE: Quickmeme's html code breaks the python html parser.  I want to keep this a simple script and avoid external libraries for simplicity to users, therefore I'll leave the RegExes until a better solution arrises.
def qm_img_pull(action):

  html = get_html(action[1])
  usefull = re.findall(b'<div id=\"leftside\">.*<div id=\"rightside\"', html, re.DOTALL)
  image = re.findall(b'src=\"(.*\.jpg)\"', usefull[0]).pop().decode('utf-8')
  print( 'Grabbing image from:', image) 
  title = re.findall(b'alt="([\w|\-|\s{1|2}]+)', usefull[0]).pop() 
  title = title.decode('utf-8') 
  tmp = title.split('-')
  title = tmp[1] +'-'+ tmp[0] + '.jpg'

  download_img(title, image)
  
    
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

def chk_setup(choice, path):
  try:
    f = open('set.txt', 'r')
    skip = False
  except:
    print('Config set.txt file not found:', IOError)
    f = open('set.txt', 'w')
    skip = True

  data = ''
  found = False
  if not skip:
    for line in f:
      l = line.split(':')
      if l[0] == choice:
        found = True
        if(DEBUG): print('---', l[0], choice)
        data += choice + ':' + path + '\n'
      else:
        if(DEBUG): print('+++', line)
        data += line 
    f.close()
    f = open('set.txt', 'w')
        
  if not found:
    data += choice + ':' + path + '\n' 
  f.write(data)
  f.close()

def parse_args(args):
  action = [None]*3
  action[0] = re.findall('[\w]+', args[0]).pop()
  
  #Setting Path to directories
  if args[0] == '-todir':
    cmd = re.findall('[\w]+', args[1]).pop()
    chk_setup(cmd, args[2]) 

    return None
  #Normal downloading functionality
  else:
    #set the url
    action[1] = args[1]
    #Get custom name
    action[2] = '_'.join(args[2:])
  return action
    

def main():
  pullers = {'im': imgur_album_pull, 'qm': qm_img_pull}

  args = sys.argv[1:]
  action = parse_args(args)

  if action != None:
    func = pullers[action[0]]
    chdir = read_setup(action[0])
    if chdir != None:
      set_dir(chdir)
    else:
      set_dir('.')

    print(func)
    func(action)

if __name__ == '__main__':
  url = 'http://imgur.com/a/WSP8q'
  #imgur_album_pull(url)
  main()



