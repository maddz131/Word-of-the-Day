import requests
import random
import PySimpleGUI as sg
import json
import textwrap

class Word:
    def __init__(self, name):
        self.name = name
        self.definitions = []

def getWord():
    with open("wordsList.txt", "r") as read_file:
        advanced_words = read_file.read().split()   #taken from "https://svnweb.freebsd.org/csrg/share/dict/words?revision=61569&view=co"
        common_words = open("commonWords.txt").read().split()  #list of common words that we users would already know
    while True:
        num = random.randint(0, len(advanced_words))
        chosen_word = advanced_words[num]
        if chosen_word not in common_words and not chosen_word[0].isupper():
            return chosen_word

def getDefinition(word):
    KEY = "8e964aef-279a-4bd2-847f-cd34a2cfe4d9" #used in API call
    requestURL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/'+ str(word) +'?key=' + KEY # str(chosen_word) 
    apiResponse = requests.get(requestURL) #http GET request of URL using requests library
    return json.loads(apiResponse.content)

def parseInfo(word_entry):
    definition_dict = {}
    definitions = []
    print(word_entry)
    try:
        definitions.append(word_entry['fl'])  #fl is the functional label aka class of the word
        print(word_entry['fl'])
    except Exception as e:
        definitions.append('No Class Type Specified')
        print("KeyError: fl")
    for index, definition in enumerate(word_entry['shortdef']):
        definition_dict[index+1] = definition
    definitions.append(definition_dict)
    return(definitions)

def generateWordAndDefenition():
    chosen_word = getWord()
    print(chosen_word)
    word_info = getDefinition(chosen_word)
    if not any(isinstance(info, dict) for info in word_info): #if the api response isn't a dictionary, that means it couldn't find the word and we need a new one
        ourWord = generateWordAndDefenition()
    else:
        ourWord = Word(chosen_word)
        definitions_list = []
        if 'hom' in word_info[0]: #if there are multiple homonym print them, otherwise just print the main definition
            definitions_list = [parseInfo(entry) for entry in word_info if entry.get('shortdef') and entry.get('hom')] #.get() checks that the hom and shortdef 1) exist and 2) are not null
            ourWord.definitions = definitions_list
        elif word_info[0].get('shortdef'):
            definitions_list  = [parseInfo(word_info[0])]
            ourWord.definitions = definitions_list
        else:    #if the chosen word didn't have a usable definition, get another
            ourWord = generateWordAndDefenition()
    return ourWord

def formatDefinitions(class_definitions):
    formatted_definitions = ''
    label = ['a','b','c','d','e','f','g','h','i'] #not ideal, but assumes there will be no more than 9 definitions per class
    for index, definition in enumerate(class_definitions):
        formatted_definitions += "{}) ".format(label[index])
        longtext = textwrap.wrap(class_definitions[definition], 80)
        for text in longtext:
            formatted_definitions += "{} \n".format(text)
    return formatted_definitions

#PROGRAM STARTING POINT
def main():
    column1 = [ [sg.Text('Welcome to the Word of the Day', key = '_intro_', font = 'Bold')],
                [sg.Text(key = '_text2_', visible = False)],
                [sg.Button('Generate Word'), sg.Exit()] ]
    layout = [[sg.Column(column1, size = (600,500))]]
    window = sg.Window("Word of the Day", layout, finalize = True) # Create the window
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED: # End program if user closes window or presses the Exit button
            break
        if event == "Generate Word":
            word = generateWordAndDefenition()
            text1 = word.name #the word
            text2 = '' #the definition
            classNum = '' #for words with multiple classes (nouns, adjectives, etc.)
            for i in range(len(word.definitions)): #word_definition[1]
                if len(word.definitions)>1:
                    classNum = f'{i+1}: '
                text2 += (f'{classNum}{word.definitions[i][0]}\n{formatDefinitions(word.definitions[i][1])}\n\n')
            window['_intro_'].update(text1)
            window['_text2_'].update(text2, visible = True)

if __name__ == "__main__":
    main()

''' 
Note:
    An example of a word.definitions is:
    [
        ['verb', {1: 'to accelerate the growth or progress of', 2: 'to bring or move forward', 3: 'to raise to a higher rank'}],
        ['noun', {1: 'a moving forward', 2: 'progress in development', 3: 'a progressive step : improvement'}],
        ['adjective', {1: 'made, sent, or furnished ahead of time', 2: 'going or situated before'}]
    ]

    Each word can have many classes (verb, noun, adjective, etc.) and each class is in it's own list along with it's corresponding definition(s).
    So each word list has:
        - word.name: a string of the word
        - word.definitions: a list made up of n number of lists (word_definition[1][n], one list per each class that the word has)
    Word.definitions[n] is a list containing two elements:
        - word.definition[n][0]: a string specifying the class (verb, adj, noun, etc.) 
        - word.definition[n][1]: a dictionary of the definitions for the class, because a single class can still have multiple definitions.
          The key is the definition number and the value is the defintition
'''