# Import modules
from text_analysis_module import run_text_analysis_in_parallel, plot_features
from music_generation_module import run_music_composition
from mapping_module import map_text_parameters

# Main class
def run_application():
    """Main function that runs whole application:
    Starting with text analysis -> train LSTM model ->
    Use text features to generate music
    """
    # Run text analysis (using multiprocessing package)
    #run_text_analysis_in_parallel()

    # Run text feature mapping onto music parameters
    #sent_score, lex_score, read_score = map_text_parameters()
    #print 'Length of sentiment array: {}, lexical density score: {}, readability score: {}'.format(len(sent_score), len(lex_score), len(read_score))

    # Run music generation
    run_music_composition(epochs=7500) # - FOR TEST PURPOSES



if __name__ == '__main__':
    run_application() # - ONLY COMMAND TO EXIST HERE
