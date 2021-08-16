from conll_reader import DependencyStructure, DependencyEdge, conll_reader
from collections import defaultdict
import copy
import sys

import numpy as np
import keras
import tensorflow as tf
tf.compat.v1.disable_eager_execution()

from extract_training_data import FeatureExtractor, State

class Parser(object): 

    def __init__(self, extractor, modelfile):
        self.model = keras.models.load_model(modelfile)
        self.extractor = extractor
        
        # The following dictionary from indices to output actions will be useful
        self.output_labels = dict([(index, action) for (action, index) in extractor.output_labels.items()])

    def parse_sentence(self, words, pos):
        state = State(range(1,len(words)))
        state.stack.append(0)    

        while state.buffer: # buffer is not empty
            # TODO: Write the body of this loop for part 4 
            
            # use the feature extractor to get representation of curr state
            curr_state_feature = self.extractor.get_input_representation(words, pos, state)
            
            # call model.predict(features) and get a softmax activated vector of possible actions
           
            #softmax_output = self.model.predict(np.array([curr_state_feature]))
            softmax_output = self.model.predict(curr_state_feature.reshape(1,-1))
            # select the highest scoring permitted transition
            # create a list of possible actions and sort it according to their output prob
            # make sure largest prob comes first in the list
            
            sorted_softmax = []
            for i in range(0, len(softmax_output[0])):
                #key, value = self.output_labels[i]
                sorted_softmax.append((self.output_labels[i], softmax_output[0][i]))
            
            sorted_softmax = sorted(sorted_softmax, key=lambda x:x[1], reverse=True)
            #sorted_softmax = np.flip(np.sort(softmax_output, 1))
            
            # go through the list until we find a legal transition
            for i in range(0, len(sorted_softmax)):
            
                action = sorted_softmax[i][0] 
                if action[0] == "left_arc":
                    # left arc can only be done if stack isn't empty and we're not at root
                    if len(state.stack) > 0 and action[1] != "root":
                        state.left_arc(action[1])     
                elif action[0] == "right_arc":
                    # right arc can only be done if stack isn't empty'
                    if len(state.stack) > 0:
                        state.right_arc(action[1])         
                elif action[0] == "shift":
                    # shift can only be done when len(buffer) is one and sttack is empty, or len(buffer)>1
                    if len(state.buffer) > 1 or (len(state.buffer) == 1 and len(state.stack)==0):
                        state.shift()
                break
                
        # take the edge in state.deps and create a DependencyStructure object
        result = DependencyStructure()
        for p,c,r in state.deps: 
            result.add_deprel(DependencyEdge(c,words[c],pos[c],p, r))
        return result 
        

if __name__ == "__main__":

    WORD_VOCAB_FILE = 'data/words.vocab'
    POS_VOCAB_FILE = 'data/pos.vocab'

    try:
        word_vocab_f = open(WORD_VOCAB_FILE,'r')
        pos_vocab_f = open(POS_VOCAB_FILE,'r') 
    except FileNotFoundError:
        print("Could not find vocabulary files {} and {}".format(WORD_VOCAB_FILE, POS_VOCAB_FILE))
        sys.exit(1) 

    extractor = FeatureExtractor(word_vocab_f, pos_vocab_f)
    parser = Parser(extractor, sys.argv[1])

    with open(sys.argv[2],'r') as in_file: 
        for dtree in conll_reader(in_file):
            words = dtree.words()
            pos = dtree.pos()
            deps = parser.parse_sentence(words, pos)
            print(deps.print_conll())
            print()
        
