import requests
import random
import PySimpleGUI as sg
import json
import textwrap

def getWord(advanced_words, common_words, word_list_length):
    while True:
        num = random.randint(0, word_list_length)
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
    with open("wordsList.txt", "r") as read_file:
        advanced_words = read_file.read().split()   #taken from "https://svnweb.freebsd.org/csrg/share/dict/words?revision=61569&view=co"
        common_words = open("commonWords.txt").read().split()  #list of common words that we users would already know
    chosen_word = getWord(advanced_words, common_words, len(advanced_words))
    print(chosen_word)
    word_info = getDefinition(chosen_word)
    if not any(isinstance(info, dict) for info in word_info): #if the api response isn't a dictionary, that means it could find the word and we need a new one
        word_with_definitions = generateWordAndDefenition()
    else:
        word_with_definitions = [chosen_word]
        definitions_list = []
        if 'hom' in word_info[0]: #if there are multiple hominims print them, otherwise just print the main definition
            definitions_list = [parseInfo(entry) for entry in word_info if entry.get('shortdef') and entry.get('hom')] #.get() checks that the hom and shortdef 1) exist and 2) are not null
        else:
            print(word_info)
            if word_info[0].get('shortdef'):
                definitions_list  = [parseInfo(word_info[0])]

        if not definitions_list:    #if the chosen word didn't have a usable definition, get another
            word_with_definitions = getDefinition()
        else:
            word_with_definitions.append(definitions_list)
            print(word_with_definitions)

    return word_with_definitions

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
            word_definition = generateWordAndDefenition()
            text1 = word_definition[0] #the word
            text2 = '' #the definition
            classNum = '' #for words with multiple classes (nouns, adjectives, etc.)
            for i in range(len(word_definition[1])):
                if len(word_definition[1])>1:
                    classNum = f'{i+1}: '
                text2 += (f'{classNum}{word_definition[1][i][0]}\n{formatDefinitions(word_definition[1][i][1])}\n\n')
            window['_intro_'].update(text1)
            window['_text2_'].update(text2, visible = True)

if __name__ == "__main__":
    main()

''' 
Note:
    An example of a word_definition is:
    ['advance',
        [
            ['verb', {1: 'to accelerate the growth or progress of', 2: 'to bring or move forward', 3: 'to raise to a higher rank'}],
            ['noun', {1: 'a moving forward', 2: 'progress in development', 3: 'a progressive step : improvement'}],
            ['adjective', {1: 'made, sent, or furnished ahead of time', 2: 'going or situated before'}]
        ]
    ]

    Each word can have many classes (verb, noun, adjective, etc.) and each class is in it's own list along with it's corresponding definition(s).
    So each word list has:
        - word_definition[0]: a string of the word
        - word_definition[1]: a list made up of n number of lists (word_definition[1][n], one list per each class that the word has)
    Word_definition[1][n] is a list containing two elements:
        - word_definition[1][n][0]: a string specifying the class (verb, adj, noun, etc.) 
        - word_definition[1][n][1]: a dictionary of the definitions, because a single class can still have multiple definitions.
          The key is the definition number and the value is the defintition
'''