# Import packages
import cPickle as pickle
import music21
import time, gzip, numpy, os
from os import listdir
from os.path import isfile, join

# Import modules
from midi_to_statematrix import *
import model_training
import lstm_model
from utils import *
from constants import *

# Main class
def music_composition_helper(m, pcs, times=20, keep_thoughts=False, name="final_piece"):
    """Function composes music according to trained LSTM models
    and stores them into 'output' folder
    """
    xIpt, xOpt = map(lambda x: numpy.array(x, dtype='int8'), model_training.getMidiSegmentInitialStep(pcs, 6, 1))
    all_outputs = [xOpt[0]]
    if keep_thoughts:
        all_thoughts = []
    m.start_slow_walk(xIpt[0])
    cons = 1
    for time in range(model_training.BATCH_LEN*times):
        resdata = m.slow_walk_fun( cons )
        nnotes = numpy.sum(resdata[-1][:,0])
        if nnotes < 2:
            if cons > 1:
                cons = 1
                cons -= 0.02
        else:
            cons += (1 - cons)*0.3
        all_outputs.append(resdata[-1])
        if keep_thoughts:
            all_thoughts.append(resdata)
    noteStateMatrixToMidi(numpy.array(all_outputs), name='./{}/{}/{}'.format(MODULE_NAME, OUTPUT_DIR, name))
    if keep_thoughts:
        pickle.dump(all_thoughts, open('./{}/{}/{}.p'.format(MODULE_NAME, OUTPUT_DIR, name),'wb'))

def music_composition_helper_final(m, pcs, times, sent_score_mapped, lex_score_mapped, read_score_mapped):
    """Function composes music according to trained LSTM models and mapped text features
    and stores them into 'output' folder
    """
    for i in xrange(len(sent_score_mapped)):
        print '\n' + green + '[+] Music bit # {} (out of {}) is being composed...'.format(i+1, len(sent_score_mapped)) + normal
        if i==0:
            xIpt, xOpt = map(lambda x: numpy.array(x, dtype='int8'), model_training.getMidiSegmentInitialStep(pcs, read_score_mapped[0], sent_score_mapped[0]))
            all_outputs = [xOpt[0]] # Random piece with requested complexity and key is retrieved
            m.start_slow_walk(xIpt[0])
            cons = 1

        else:
            new_pcs = midiToNoteStateMatrix('./{}/{}/{}.mid'.format(MODULE_NAME, RESULTS_DIR, i-1))
            xIpt, xOpt = map(lambda x: numpy.array(x, dtype='int8'), model_training.getMidiSegmentTextFeatures(new_pcs, read_score_mapped[i], sent_score_mapped[i]))
            all_outputs = [xOpt[0]] # Choose previously created midi file and pass desired complexity and key along
            m.start_slow_walk(xIpt[0])
            cons = 1

        for time in range(model_training.BATCH_LEN*times):
            resdata = m.slow_walk_fun( cons )
            nnotes = numpy.sum(resdata[-1][:,0])
            if nnotes < 2:
                if cons > 1:
                    cons = 1
                cons -= 0.02
            else:
                cons += (1 - cons)*0.3
            all_outputs.append(resdata[-1])
        noteStateMatrixToMidi(numpy.array(all_outputs), name='./{}/{}/{}'.format(MODULE_NAME, RESULTS_DIR, i), velocity=lex_score_mapped[i]*0.25)

    # Here goes tempo change
    available_files    = sorted([f for f in listdir("./{}/{}".format(MODULE_NAME, RESULTS_DIR)) if (isfile(join("./{}/{}".format(MODULE_NAME, RESULTS_DIR), f)) and (".mid" in f))],
                                key=lambda f: int(filter(str.isdigit, f)))
    tempo_scale_factor = 1.5 # Initial tempo slowed by half (120bpm down to 60bpm)

    for index, music in enumerate(available_files):
        score     = music21.converter.parse("./{}/{}/{}".format(MODULE_NAME, RESULTS_DIR, music))
        scale     = lex_score_mapped[index] * 0.25
        new_tempo = tempo_scale_factor - scale # If smaller than 1, then speed up, otherwise slow down

        print 'Changing tempo in {} from {} to {}'.format(music, tempo_scale_factor, new_tempo)
        newscore = score.scaleOffsets(new_tempo).scaleDurations(new_tempo)
        newscore.write('midi', './{}/{}/final_{}'.format(MODULE_NAME, RESULTS_DIR, music))

def run_music_composition(pcs, sent_score_mapped, lex_score_mapped, read_score_mapped, music_length= 30, epochs=5500):
    start = time.time()

    try:
        os.mkdir('./{}/{}'.format(MODULE_NAME, OUTPUT_DIR))
        print '\n===' + green + ' {} folder has been created '.format(OUTPUT_DIR) + normal + '==='
    except:
        print '\n===' + red + ' {} folder already exists '.format(OUTPUT_DIR) + normal + '==='
        pass

    try:
        os.mkdir('./{}/{}'.format(MODULE_NAME, RESULTS_DIR))
        print '\n===' + green + ' {} folder has been created '.format(RESULTS_DIR) + normal + '==='
    except:
        print '\n===' + red + ' {} folder already exists '.format(RESULTS_DIR) + normal + '==='
        pass

    print '\n===' + turquoise + ' LSTM model is being created... ' + normal + '==='
    m = lstm_model.Model([300,300],[100,50], dropout=0.5) # Create LSTM model

    print '\n===' + turquoise + ' LSTM model is being trained... ' + normal + '==='
    model_training.trainModel(m, pcs, epochs) # Train LSTM model

    # Save LSTM model configuration
    #print '\n===' + turquoise + ' LSTM model is being saved... ' + normal + '==='
    #pickle.dump( m.learned_config, open( "./{}/{}/final_learned_config.p".format(MODULE_NAME, OUTPUT_DIR), "wb" ) )

    # Just to see how model performs on its own
    # print '\n===' + turquoise + ' Music for final LSTM configuration is being generated... ' + normal + '==='
    # music_composition_helper(m, pcs, name="composition") # Generate music

    print '\n===' + turquoise + ' Music for given text is being generated... ' + normal + '==='
    music_composition_helper_final(m, pcs, music_length, sent_score_mapped, lex_score_mapped, read_score_mapped) # Generate music

    finish = time.time() - start
    print '\n===' + turquoise + ' Music composition has finished in ' + normal + '{} seconds'.format(str(finish)) + '==='
