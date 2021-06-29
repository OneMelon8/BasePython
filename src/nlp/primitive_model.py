import json
import os
import pickle

import nltk
import numpy as np
import tensorflow as tf
import tflearn
from nltk.stem.lancaster import LancasterStemmer

PATH_INTENT = "src/nlp/intents.json"
PATH_WORDS_DATA = "src/nlp/data/bag_of_words.pickle"
PATH_MODEL = "src/nlp/models/primitive.tflearn"

nltk.download("punkt")
stemmer = LancasterStemmer()

# Global data variables
dictionary = []  # dictionary of words we've seen (unique)
intents = []  # list of intents
utterances = {}  # dict of {intent => [utterances...]}
train_x, train_y = [], []  # training data lists

# Global model variables
model = None
model_changed = False


#######################
# DATA / FILE METHODS #
#######################
def load_or_generate_data(force_generate=False, save_data=True):
    """
    Load data if exists or generate data from intents

    Args:
        save_data (bool): whether to save the data to file
        force_generate (bool): set to True to force the re-generation of data
    """
    if not force_generate and load_data():
        return
    generate_data(save_data)


def generate_data(save_data=True):
    """
    Generate data from intents and load into global variables

    Args:
        save_data (bool): whether to save the data to file
    """
    global dictionary, intents, utterances, train_x, train_y

    # Step 1: load data from intents file
    with open(PATH_INTENT) as f:
        data = json.load(f)

    # Reset global variables (in case of re-train)
    dictionary = set()
    intents = []
    utterances = {}
    train_x, train_y = [], []

    # Step 2: convert intent sentences into token lists
    temp_x, temp_y = [], []
    for intent, intent_data in data.items():
        # Add intent to intent list
        intents.append(intent)
        # Get the list of patterns (utterances) in this intent
        patterns = intent_data["patterns"]

        # Process and save each pattern
        for sentence in patterns:
            # Save utterance
            utterances[intent] = utterances.get(intent, []) + [sentence]
            # Preprocess sentence
            words = preprocess(sentence)
            # Add words that appear in this sentence into the dictionary
            dictionary.update(words)
            # Add current sentence to training data
            temp_x.append(words)
            temp_y.append(intent)

    # Now:
    # - temp_x contains a list of list of tokens
    # - temp_y contains a list of intents
    # - dictionary contains all tokens in all sentences

    # Convert dictionary to sorted list to keep ordering
    # TODO: in the future, if this project gets bigger, this will need optimization
    #       the bag-of-words array is really sparse, consists of mostly 0's and only few 1's
    #       compress by only remembering the location of 1's?
    dictionary = sorted(dictionary)

    # Step 3: create training data by converting strings into bag of words
    for i, tokens in enumerate(temp_x):
        # TODO: optimize by converting dictionary to dict with {token => index}? O(1) lookup cost
        #       convert back to list afterwards? not sure, just an idea
        #       cause right now the complexity is O(len(tokens) * len(dictionary)) => O(n^2)

        # See bag_of_words method for more details here
        x = [1 if word in tokens else 0 for word in dictionary]

        # Y is basically an all-zero array but the target intent's index is 1
        # There should be only one 1 here
        # Example: target intent is "identity"
        # - Intents: ["greeting", "farewell", "identity", "age", ...]
        # - Y array: [         0,          0,          1,     0, ...]
        y = [0] * len(data)  # len(data) = how many classes (intents) there are
        y[intents.index(temp_y[i])] = 1
        train_x.append(x)
        train_y.append(y)

    # Training data is now in train_x and train_y

    # Save this bag-of-words training data for faster access in the future
    if save_data:
        with open(PATH_WORDS_DATA, "wb") as f:
            pickle.dump((dictionary, intents, utterances, train_x, train_y), f)


def load_data():
    """
    Load previously saved data into global variables

    Returns:
        bool: whether the load is successful
    """
    global dictionary, intents, utterances, train_x, train_y

    # Check file existence and permissions
    if not os.path.isfile(PATH_WORDS_DATA) or not os.access(PATH_WORDS_DATA, os.R_OK):
        return False
    # Open file and load data
    with open(PATH_WORDS_DATA, "rb") as f:
        dictionary, intents, utterances, train_x, train_y = pickle.load(f)
    return True


def add_utterance(intent, utterance):
    """
    Add a new utterance to the target intent

    Args:
        intent (str): intent to be modified
        utterance (str): utterance to be added
    """
    global model_changed
    assert intent in intents, f"Invalid intent \"{intent}\""
    with open(PATH_INTENT) as f:
        data = json.load(f)
    data[intent]["patterns"].append(utterance)
    with open(PATH_INTENT, "w") as f:
        json.dump(data, f, indent=4)

    model_changed = True


##########################
# NEURAL NETWORK METHODS #
##########################

def create_and_train_model(epochs=1000, save_model=True):
    """
    Create and train the neural network

    Args:
        epochs (int): number of epochs to train for
        save_model (bool): whether to save the trained model to file
    """
    global model, train_x, train_y
    model = None

    # Build model
    with tf.Graph().as_default():
        # Input layer's shape is basically the number of unique words in the dictionary
        net = tflearn.input_data(shape=[None, len(train_x[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        # Output layer's shape is basically the number of intents
        # Softmax activation will output a "confidence" percentage, range=[0, 1]
        net = tflearn.fully_connected(net, len(train_y[0]), activation="softmax")
        net = tflearn.regression(net)
        model = tflearn.DNN(net)

        # Train model
        model.fit(train_x, train_y, n_epoch=epochs, batch_size=8)

        # Save model
        if save_model:
            model.save(PATH_MODEL)


def load_model():
    """ Load model from disk """
    # TODO: check correctness of this cause tflearn is wonk
    global model
    model = tflearn.DNN(None)
    model.load(PATH_MODEL)


def predict(message):
    """
    Generate an intent from the input message using the model

    Args:
        message (str): input message

    Returns:
        Tuple(str, float, Dict[str, float]): (predicted intent, confidence, entire result as a dict)
    """
    assert model is not None, "Model must be initialized before predicting!"

    # Since model uses softmax, results should look something like this:
    # > [0.003, 0.0001, 0.02, 0.34, 0.09, 0.80, 0.17, ...]
    # - float in each position representing confidence
    # - index represent index in the "intents" list (global)
    results = model.predict([bag_of_words(preprocess(message))])[0]

    # We save the index of the maximum confidence
    index = np.argmax(results)
    # Convert index into intent
    intent = intents[index]
    # Return the intent
    return intent, results[index], {intents[a]: results[a] for a in range(len(results))}


###################
# UTILITY METHODS #
###################

def preprocess(message):
    """
    Preprocesses the message into a list of tokens by tokenizing and stemming
    e.g.
        Before: "Why are you flying?"
        After:  ["why", "are", "you", "fly"]

        Before: "The foxes quickly jumped over the rabbits!"
        After:  ["the", "fox", "quick", "jump", "over", "the", "rabbit"]

    Args:
        message (str): message to preprocess

    Returns:
        List[str]: list of preprocessed tokens (tokenized and stemmed)
    """
    # Null check
    if not message:
        return []

    output = []
    # Tokenize message (split string into small tokens)
    words = nltk.word_tokenize(message)
    for word in words:
        # Stem each word (eg. flying becomes fly after stemming)
        word = stemmer.stem(word)
        # TODO: apply rules to filter tokens in the future, simple rules for now
        if word in ",.?!~" or len(word) <= 1:
            continue
        output.append(word)
    return output


def bag_of_words(tokens):
    """
    Generates a bag-of-words representation of the token list, uses the global dictionary
    e.g.
        Dict:   ["apple", "hello", "orange", "pineapple", "world", "again"]
        Before: [         "hello",                        "world", "again"]
        After:  [      0,       1,        0,           0,       1,       1]

    Args:
        tokens (List[str]): list of preprocessed tokens (tokenized and stemmed)

    Returns:
        np.array: numpy array of the bag-of-words representation of the token list
    """
    global dictionary
    tokens = set(tokens)
    # TODO: again, this could be faster with an improved dictionary data structure
    #       Currently O(len(dictionary)), can be improved to O(len(tokens))
    bag = [1 if word in tokens else 0 for word in dictionary]
    assert len(bag) == len(dictionary), "INVALID BAG-OF-WORDS MODEL! THIS SHOULDN'T HAPPEN"
    return np.array(bag)
