import warnings
import logging
import sklearn

from asl_data import SinglesData


logging.basicConfig(level=logging.INFO)
def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
    
    # go through each item in the test set one by one
    test_sequences = list(test_set.get_all_Xlengths().values())
    for test_X, test_Xlength in  test_sequences:
        logL = float("-inf")
        logLDict = {}
        for word, model in models.items():
            #score the current word in test_set
            try:
                if model == None:
                    continue
                logL = model.score(test_X, test_Xlength)
                logLDict[word] = logL           
            except RuntimeWarning as rw:
                    logging.warning('Recognizer: RuntimeWarning : %s', rw)
            except ValueError as ve:
                    logging.warning('Recognizer: ValueError : %s', ve) 
        #append the dict                  
        probabilities.append(logLDict)
        logging.info('length of logLDict=%d', len(logLDict)) 
        max_logl_word = max(logLDict,key=logLDict.get)  
        # the one with maximum LogL gets added to guesses            
        guesses.append(max_logl_word)
        
        
    return probabilities, guesses
    