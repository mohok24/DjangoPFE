from keras.models import load_model
import pickle
from nltk.tokenize import RegexpTokenizer,word_tokenize
from keras.models import load_model
from nltk.tokenize import RegexpTokenizer
import numpy as np
import re 
class AI:
    def __init__(self, model_path):
        with open("joined_text.txt", "r",encoding="utf-8") as file:
            joined_text = file.read()
    
        partial_text = joined_text
        tokenizer = RegexpTokenizer(r"\w+")
        tokens = tokenizer.tokenize(partial_text.lower())
        self.unique_tokens = np.unique(tokens)
        self.unique_token_index = {token: index for index, token in enumerate(self.unique_tokens)}
        self.n_words = 10
        self.model = load_model("text_gen_model2.h5")
        self.history = pickle.load(open("history2.p", "rb"))
        
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
        if len(words) > 10:
            words = words[-10:]  # Keep only the last ten words
        print("Words considered for prediction:", words)

        X = np.zeros((1, self.n_words, len(self.unique_tokens)))
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
        top_indices = np.argpartition(predictions, -n_best)[-n_best:]
        top_words = [self.unique_tokens[idx] for idx in top_indices]
        return top_words


