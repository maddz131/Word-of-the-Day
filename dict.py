import requests
import random
import tkinter as tk
from tkinter import ttk, scrolledtext
import textwrap
import os
from ttkthemes import ThemedTk
from string import ascii_lowercase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Word:
    def __init__(self, name):
        self.name = name
        self.definitions = []

def get_random_word():
    """Load word lists and return a random advanced word that's not common."""
    with open("wordsList.txt", "r", encoding="utf-8") as word_list_file:
        advanced_words = word_list_file.read().split()
    with open("commonWords.txt", "r", encoding="utf-8") as common_words_file:
        common_words = common_words_file.read().split()
    
    # Limit attempts to prevent infinite loop
    max_attempts = 1000
    attempts = 0
    
    while attempts < max_attempts:
        attempts += 1
        if not advanced_words:
            raise ValueError("No valid words available in wordsList.txt")
        
        random_index = random.randint(0, len(advanced_words) - 1)
        selected_word = advanced_words[random_index].strip()
        
        if selected_word not in common_words and not selected_word[0].isupper():
            return selected_word
    
    raise RuntimeError(f"Could not find a suitable word after {max_attempts} attempts")

def fetch_word_definition(word):
    """Fetch word definition from dictionary API."""
    api_key = os.getenv("DICTIONARY_API_KEY")
    if not api_key:
        raise ValueError("DICTIONARY_API_KEY not found. Please set it in your .env file or environment variables.")
    api_url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'
    response = requests.get(api_url, timeout=10)
    return response.json()

def parse_word_entry(word_entry):
    """Parse word entry dictionary into structured format."""
    parsed_entry = {}
    definitions_dict = {}
    parsed_entry['class'] = word_entry.get('fl', 'No Class Type Specified')  # fl is the functional label aka class of the word
    short_definitions = word_entry.get('shortdef', [])
    
    for index, definition_text in enumerate(short_definitions, start=1):
        definitions_dict[index] = definition_text
    
    parsed_entry['definition'] = definitions_dict
    return parsed_entry

def generate_word_with_definition():
    """Generate a word with its definition, retrying if necessary."""
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        selected_word = get_random_word()
        api_response = fetch_word_definition(selected_word)
        
        if not api_response or not isinstance(api_response, list):
            retry_count += 1
            continue
        
        if not any(isinstance(entry, dict) for entry in api_response):
            retry_count += 1
            continue
        
        word_object = Word(selected_word)
        
        if api_response[0].get('hom'):
            parsed_definitions = [
                parse_word_entry(word_entry) 
                for word_entry in api_response 
                if isinstance(word_entry, dict) and word_entry.get('shortdef') and word_entry.get('hom')
            ]
            word_object.definitions = parsed_definitions
        elif api_response[0].get('shortdef'):
            word_object.definitions = [parse_word_entry(api_response[0])]
        else:
            retry_count += 1
            continue
        
        if word_object.definitions:
            return word_object
        
        retry_count += 1
    
    raise RuntimeError("Failed to generate valid word")

def format_definitions(definitions_dict):
    """Format definitions dictionary into readable string."""
    formatted_output = ''
    for index, (key, definition_text) in enumerate(sorted(definitions_dict.items())):
        formatted_output += f"{ascii_lowercase[index]}) "
        wrapped_lines = textwrap.wrap(str(definition_text), 80)
        for line in wrapped_lines:
            formatted_output += f"{line}\n"
    return formatted_output

def generate_word_handler(word_label, definition_text, status_label, root):
    """Handle the Generate Word button click."""
    status_label.config(text='', fg='red')
    definition_text.config(state='normal')
    definition_text.delete(1.0, tk.END)
    definition_text.insert(tk.END, 'Generating word... Please wait.')
    definition_text.config(state='disabled')
    word_label.config(text='Loading...')
    root.update()
    
    try:
        word_object = generate_word_with_definition()
        word_label.config(text=word_object.name, font=('Arial', 18, 'bold'))
        
        formatted_output = ''
        for definition_index in range(len(word_object.definitions)):
            if len(word_object.definitions) > 1:
                homonym_prefix = f'{definition_index+1}: '
            else:
                homonym_prefix = ''
            
            class_definitions = word_object.definitions[definition_index].get('definition', {})
            if class_definitions:
                formatted_output += f'{homonym_prefix}{word_object.definitions[definition_index]["class"]}\n{format_definitions(class_definitions)}\n\n'
        
        definition_text.config(state='normal')
        definition_text.delete(1.0, tk.END)
        definition_text.insert(tk.END, formatted_output)
        definition_text.config(state='disabled')
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg='red')

def create_window():
    """Create and configure the main application window with a nice theme.
    
    Available themes if ttkthemes is installed:
    - 'arc' (default): Modern, clean theme
    - 'equilux': Dark theme
    - 'azure': Light blue theme  
    - 'clearlooks': Clean, minimal look
    - 'winnative': Windows native style
    - 'keramik', 'plastik', 'radiance', 'smog', 'ubuntu': Various other themes
    """
    # Use ThemedTk if available for better-looking themes
    window = ThemedTk(theme="azure")  # Change theme name here to try different looks
    
    window.title("Word of the Day")
    window.resizable(True, True)
    
    return window

def create_ui_elements(parent_window):
    """Create all UI elements and return references to important widgets.
    
    Returns a dictionary with:
    - 'word_label': Label that displays the generated word
    - 'definition_text': Scrollable text area for definitions
    - 'status_label': Label for error messages
    """
    # Main container holds all UI elements
    main_container = ttk.Frame(parent_window, padding="8")
    main_container.pack(fill=tk.BOTH, expand=True)
    
    # Configure window to resize properly
    parent_window.columnconfigure(0, weight=1)
    parent_window.rowconfigure(0, weight=1)
    
    # === Title ===
    title_text = "Welcome to the Word of the Day"
    title_label = ttk.Label(main_container, text=title_text, font=('Arial', 16, 'bold'))
    title_label.pack(pady=(0, 8))
    
    # === Word Display ===
    # This label will show the generated word (starts empty)
    word_label = ttk.Label(main_container, text="", font=('Arial', 18, 'bold'))
    word_label.pack(pady=(0, 8))
    
    # === Definition Display ===
    # Scrollable text area to show word definitions
    definition_text = scrolledtext.ScrolledText(
        main_container, 
        wrap=tk.WORD,
        width=65, 
        height=12,
        font=('Arial', 10)
    )
    definition_text.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
    definition_text.config(state='disabled')  # Start as read-only
    
    # === Status/Error Message Display ===
    # Shows error messages in red text
    status_label = tk.Label(main_container, text="", fg='red', font=('Arial', 9))
    status_label.pack(pady=(0, 8))
    
    # === Buttons ===
    button_container = ttk.Frame(main_container)
    button_container.pack(pady=(0, 8))
    
    # Generate Word button - triggers word generation when clicked
    generate_button = ttk.Button(
        button_container, 
        text="Generate Word",
        command=lambda: generate_word_handler(word_label, definition_text, status_label, parent_window)
    )
    generate_button.pack(padx=5)
    
    # Return important widgets that need to be updated
    return {
        'word_label': word_label,
        'definition_text': definition_text,
        'status_label': status_label
    }

def main():
    """Main program entry point - sets up the GUI and starts the application."""
    window = create_window()
    ui_widgets = create_ui_elements(window)
    window.mainloop()

if __name__ == "__main__":
    main()

''' 
Note:

    Each word can have many classes (verb, noun, adjective, etc.) and each class is in it's own list along with it's corresponding definition(s).
    So each word list has:
        - word.name: a string of the word
        - word.definitions: a list made up of n dictionaries, n being the number of classes the word has
            - since each class can also have multiple definitions, the value of the 'definition' key is another dictionary
            
    An example of word.definitions is:
    [
        { class: 'verb', definition: {1: 'to accelerate the growth or progress of', 2: 'to bring or move forward', 3: 'to raise to a higher rank'}},
        { class: 'noun',  definition: {1: 'a moving forward', 2: 'progress in development', 3: 'a progressive step : improvement'}},
        { class: 'adjective',  definition: {1: 'made, sent, or furnished ahead of time', 2: 'going or situated before'}}
    ]
'''