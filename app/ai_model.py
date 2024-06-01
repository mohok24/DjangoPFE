from keras.models import load_model
import pickle
from nltk.tokenize import RegexpTokenizer,word_tokenize
from keras.models import load_model
from nltk.tokenize import RegexpTokenizer
import numpy as np
import re 
class AI:
    def __init__(self, model_path):
        self.model = load_model(model_path)

        with open("train_joined_text.txt", "r",encoding="utf-8") as file:
            train_joined_text = file.read()
    
        self.tokenizer = RegexpTokenizer(r"\w+")
        tokens = self.tokenizer.tokenize(train_joined_text.lower())
        self.unique_tokens = np.unique(tokens)
        self.unique_token_index = {token: index for index, token in enumerate(self.unique_tokens)}
        
    def preprocess(text):
        characters_to_remove = "':,0123456789"
        replacement_mapping = {
            "’": " "
        }
        for char, replacement in replacement_mapping.items():
            text = text.replace(char, replacement)
        text = re.sub('[' + re.escape(characters_to_remove) + ']', '', text)
        text = text.strip()
        return text

    def predict_next_word(self, text, n_best):
        print("Input text:", text)
        text = text.lower()
        print("Lowercased text:", text)

        words = text.split()
        if len(words) > 2:
            words = words[-2:]  
        print("Words considered for prediction:", words)

        X = np.zeros((1, 2, len(self.unique_tokens)))
        print("Shape of X:", X.shape)

        valid_words = []
        for i, word in enumerate(words):
            if word in self.unique_token_index:
                X[0, i, self.unique_token_index[word]] = 1
                valid_words.append(word)
        print("Valid words in input text:", valid_words)

        if not valid_words:
            print("No valid words found in input text.")
            return None 

        predictions = self.model.predict(X)[0]
        top_index = np.argmax(predictions)
        top_word = self.unique_tokens[top_index]
        return top_word


