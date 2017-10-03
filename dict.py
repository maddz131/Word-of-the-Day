import requests
import random
import xml.etree.ElementTree as ET
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Rectangle, Color



total = ""
origin = ""
entry = None
KEY = "8e964aef-279a-4bd2-847f-cd34a2cfe4d9"

word_site = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
#word_site = "https://gist.githubusercontent.com/deekayen/4148741/raw/01c6252ccc5b5fb307c1bb899c95989a8a284616/1-1000.txt"
wordResponse = requests.get(word_site)
WORDS = wordResponse.content.splitlines()   #list of words from site
length = len(WORDS)         # num of words in the file

WCHECK = open("commonWords.txt").read().split()     #list of common words that we users would already know

def getWord(length): #gets a random word from the file
    check = True
    while(check==True):
        check = False
        index = random.randint(1,length)
        for word in WCHECK:     #checks that word from file is not a 'common word'
            if WORDS[index] == word:
                check = True     #if it is common, loop will continue until it gets uncommon word
                print(word)

    return index    #index of acceptable word is returned

def getInfo(index): #gets info on the word from webster api
    chosen = WORDS[index].decode('utf-8') #converts the bytes object to string
    requestURL = 'http://www.dictionaryapi.com/api/v1/references/collegiate/xml/'+ chosen +'?key=' + KEY #WORDS[index]
    dictResponse = requests.get(requestURL) #http GET request of URL using requests library
    xml = dictResponse.content #gets content of GET response which is xml
    root = ET.fromstring(xml)  #uses element tree library to convert xml into searchable tree
    return root

def mainfunction(total,origin,entry):
    #if no entry file exists, or if the entry is a location, get a new word and its merriam-webster info
    while(entry is None or entry.find('fl').text == "geographical name" or entry.find('fl').text == "biographical name" or entry.find('fl').text == "abbreviation"): #(entry is None) or
        index = getWord(length)  #gets a index of random acceptable word from the file and assigns it to index
        root = getInfo(index)    #gets xml tree of chosen word (found using index)
        entry = root.find('entry')    #'entry' branch of xml tree contains all other branches, so I dont have to write root.find('entry').find('pr')

    #print fields
    word = entry.find('ew').text
    total +=  "\nWord: " + word#print("\nWord: " + word)

    if entry.find('pr') is not None:
        pr = entry.find('pr').text
        prlabel = "\nPronunciation: " #print("Pronunciation: " +  pr)

    if entry.find('fl') is not None:
        wt = entry.find('fl').text
        total += "\nWord Type: " +  wt#print("Word Type: " +  wt)

    if entry.find('et') is not None:
        origin = entry.find('et').text
        total += "\nOrigin: " + str(origin)#print("Origin: " + str(origin))

    defs = entry.find('def')
    total += "\nDefinition:"#print "Definition:"
    #print "".join(defs.itertext())
    for count, dt in enumerate(defs.iter('dt'), start = 1): #iterate through all dt's(definitions) in defs
        total += "\n{}{}".format(count, "".join(dt.itertext()))#print "{}{}".format(count, "".join(dt.itertext())) #"".join(dt.itertext()) makes sure all branches within dt are also printed
    return total
    #gui(word, pr, wt, origin)

class Hello(RelativeLayout):
    def __init__(self,**kwargs):
        super(Hello,self).__init__(**kwargs)
        #self.l = Label(text=mainfunction(total,origin,entry),text_size=(None,None),
        #                      font_size="20sp",
        #                      pos_hint={'center_x': 0.5, 'center_y': .85},
        #                      size_hint_y=None,
        #                      height=self.texture_size[1],
        #                      halign="center",
        #                      valign = "middle",
        #                      color=(0.055, 0.235, 0.541, 1))
        self.l = Label(text=mainfunction(total,origin,entry))
        self.b = Button(text = "Next", size_hint=(.3, .1), on_press=self.update)
        self.add_widget(self.l)
        self.add_widget(self.b)
    def update(self,event):
        self.l.text = mainfunction(total,origin,entry)

class WordApp(App):
    def build(self):
        return Hello()
        #l = Label(text=mainfunction(total,origin,entry))
        #b = Button(text = "Next")
        #b.bind(on_press=self.update)
        #layout = BoxLayout(orientation='vertical')
        #layout.add_widget(l)
        #layout.add_widget(b)
        #return layout

    #def update():
    #    l.text = mainfunction(total,origin,entry)

WordApp().run()
