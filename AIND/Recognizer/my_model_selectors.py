import math
import statistics
import warnings
import sys
import logging

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from asl_utils import combine_sequences


logging.basicConfig(level=logging.WARNING)
class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        bestBicScore = float("+inf")
        bestModel = None
        log_n_samples = np.log(sum(self.lengths))
        
        for n_components in range(self.min_n_components,self.max_n_components+1): 
            logL = float("-inf")
            bicScore = float("+inf")
            hmm_model = None
            logging.info('BIC: Training word =%s with number of components=%d', self.this_word, n_components)
            
            try :
                hmm_model = GaussianHMM(n_components=n_components, covariance_type="diag", 
                n_iter=1000, random_state=self.random_state,verbose=False).fit(self.X, self.lengths)
                logL = hmm_model.score(self.X, self.lengths)
                # Bayesian information criteria: BIC = -2 * logL + p * logN
                # p is number of Free Parameters in the Model
                parameters = n_components * n_components + 2 * len(self.X[0]) * n_components - 1
                bicScore = -2 * logL + parameters * log_n_samples
                if bicScore < bestBicScore:
                    logging.debug('BIC: found lower bic score=%f for word =%s with components=%d', bicScore, self.this_word, n_components)
                    bestBicScore = bicScore
                    bestModel = hmm_model
                    
            except RuntimeWarning as rw:
                    logging.warning('BIC: RuntimeWarning : %s', rw)
            except ValueError as ve:
                    logging.warning('BIC: ValueError : %s', ve)  
        
        if bestModel == None:
            return None
        
        logging.info('BIC: returning : best model with BIC score=%f for word=%s with number of components=%d', bestBicScore, self.this_word, bestModel.n_components)        
        return bestModel


class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        
        bestDicScore = float("-inf")
        bestModel = None
        
        for n_components in range(self.min_n_components,self.max_n_components+1):
            hmm_model = None
            antiLogL = 0.0
            m = 0
            logging.info('DIC: Training word =%s with number of components=%d', self.this_word, n_components)
          
            try :
                hmm_model = GaussianHMM(n_components=n_components, covariance_type="diag", 
                n_iter=1000, random_state=self.random_state,verbose=False).fit(self.X, self.lengths)
                logL = hmm_model.score(self.X, self.lengths)
                
                #compute Anti-Likelihood
                for word in self.hwords:
                    if word == self.this_word:
                        continue
                    X, lengths = self.hwords[word]
                    try:
                        antiLogL += hmm_model.score(X, lengths)
                        m += 1
                    except:   
                        continue
                        
                #DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))        
                dicScore = logL - antiLogL / (m-1)     
                
                if dicScore > bestDicScore:
                    logging.debug('DIC: found larger/better dic score=%f for word =%s with components=%d', dicScore, self.this_word, n_components)
                    bestDicScore = dicScore
                    bestModel = hmm_model
                    
            except RuntimeWarning as rw:
                    logging.warning('DIC: RuntimeWarning : %s', rw)
            except ValueError as ve:
                    logging.warning('DIC: ValueError : %s', ve)    
         
        if bestModel == None:
            return None
        
        logging.info('DIC: returning : best model with DIC score=%f for word=%s with number of components=%d', bestDicScore, self.this_word, bestModel.n_components)               
        return bestModel


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''
    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # train the model for various CV Folds
        bestNComponents = None
        bestLogL = float("-inf")
        
        for n_components in range(self.min_n_components,self.max_n_components+1):    
            logL = float("-inf")
            scores = []
            hmm_model = None
            logging.info('CV: Training word =%s with number of components=%d', self.this_word, n_components)
            # cannot split of length of sequences is 1
            if len(self.sequences) == 1:
                try :
                    hmm_model = GaussianHMM(n_components=n_components, covariance_type="diag", 
                    n_iter=1000, random_state=self.random_state,verbose=False).fit(self.X, self.lengths)
                    logL = hmm_model.score(self.X, self.lengths)
                    logging.debug('len(seq)==1: logL=%f , bestLogL=%f for word =%s with components=%d', logL,bestLogL, self.this_word, n_components)
                except RuntimeWarning as rw:
                    logging.warning('CV: RuntimeWarning : %s', rw)
                except ValueError as ve:
                    logging.warning('CV: ValueError : %s', ve)    
                if logL > bestLogL:
                    bestLogL = logL
                    bestNComponents = n_components
                    logging.debug('CV: updating: best LogL=%f for word =%s with components=%d', bestLogL,self.this_word, n_components)
            else:
                split_method = KFold(n_splits=min(3,len(self.lengths)))
                #perform KFold Split into Train and Test Sets
                for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
                    logging.debug("CV: Train fold indices:{} Test fold indices:{}".format(cv_train_idx, cv_test_idx))
                    cvX, cvlengths = combine_sequences(cv_train_idx,self.sequences)
                    try:
                        #The hmmlearn library may not be able to train or score all models. 
                        #Implement try/except contructs as necessary to eliminate non-viable 
                        #models from consideration.
                        hmm_model = GaussianHMM(n_components=n_components, covariance_type="diag",
                        n_iter=1000, random_state=self.random_state,verbose=False).fit(cvX, cvlengths)
                        cvX, cvlengths = combine_sequences(cv_test_idx,self.sequences)
                        scores.append(hmm_model.score(cvX, cvlengths))
                    except RuntimeWarning as rw:
                        logging.warning('CV: RuntimeWarning : %s', rw)
                    except ValueError as ve:
                        logging.warning('CV: ValueError : %s', ve)            
                if len(scores) > 0:        
                    nps = np.array(scores)
                    logL = nps.mean()
                    logging.debug('CV: KFold Split: logL=%f , bestLogL=%f for word =%s with components=%d', logL,bestLogL, self.this_word, n_components)
                    if logL > bestLogL:
                        bestLogL = logL
                        bestNComponents = n_components
                        logging.debug('CV: updating: best logL=%f for word=%s with components=%d', bestLogL,self.this_word, n_components)
                        
        logging.info('CV: returning : best LogL = %f for word=%s with number of components=%d', bestLogL, self.this_word, bestNComponents) 
        bestModel = None
        try:
            if bestNComponents == None:
                return None
            bestModel = GaussianHMM(n_components=bestNComponents, covariance_type="diag",
            n_iter=1000, random_state=self.random_state,verbose=False).fit(self.X, self.lengths)
        except RuntimeWarning as rw:
            logging.warning('CV: RuntimeWarning : %s', rw)
        except ValueError as ve:
            logging.warning('CV: ValueError : %s', ve) 
            
        return bestModel
    