# Import packages
import time, re, collections, ebooklib, pickle, nltk
from contextlib import closing
from ebooklib import epub
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from operator import itemgetter
# Import modules

# Font effects for console/terminal output
black = "\x1b[1;30m"
red = "\x1b[1;31m"
green = "\x1b[1;32m"
yellow = "\x1b[1;33m"
blue = "\x1b[1;34m"
purple = "\x1b[1;35m"
turquoise = "\x1b[1;36m"
normal = "\x1b[0m"

# Main class
def read_in_epub(book_name):
    """Function reads in specific ePub book and
    outputs set of files that are believed to be different chapters.
    """
    book = epub.read_epub(book_name)

    #for item in book.get_items():
    #    print item
    i = 1
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        #print item.content # html format
        file_name = 'output_'+str(i)+'.txt'
        if item.is_chapter():
            with open(file_name, 'a') as output:
                output.write(item.get_body_content())
        #print item.get_body_content() # returns content inside tags with 'body' class
        i = i+1
        #print item.get_content() same to content attribute
        #print item.is_chapter() # returns True if object is a chapter

def extract_text():
    """Reads in an output of 'read_in_epub()' function
    and extracts only textual(important) data from those files
    and outputs files with clean text, that would be used for analysis
    """
    def clean_string(x):
        """Returns clean str, without 'p' tag and leftovers of convertion html-> str"""
        return x.replace('<p>','').replace('</p>','').replace("'",'`').replace('\xe2\x80\x94',' ').replace("\"",'')

    files = [f for f in listdir(".") if (isfile(join(".", f)) and ("output_" in f))]
    for file_name in files:
        page = open(file_name, 'r')
        soup = soup = BeautifulSoup(page, "lxml")
        page = soup.find_all('p')
        strings = list()

        for sub_str in page:
            strings.append(clean_string(str(sub_str)))

        file_name = "clean_"+file_name
        with open(file_name, 'a') as output:
            for string in strings:
                output.write("%s\n" % string)

def sentiment_analysis(text):
    """'text' variable: representation of the text to be analysed.
    Returns a sentiment score for given text piece.
    To access values, use following keys:
        'neg' - negative score
        'pos' - positive score
        'neu' - neural score
    """
    sentences = []
    scores = []
    sentences.extend(tokenize.sent_tokenize(text))

    # Use NLTK built-in sentiment analyzer
    sentiment_analyser = SentimentIntensityAnalyzer()
    for sentence in sentences:
        score = sentiment_analyser.polarity_scores(sentence)
        scores.insert(0,score) # Record polarity score

    # Sum up all scores within the key
    total_score = {key:sum(map(itemgetter(key), scores)) for key in scores[0]}

    if total_score['neg']>total_score['pos']:
        sc = -abs(total_score['neg']/len(scores))
        print ('\n' + yellow + '[+] Sentiment score... ' + normal + str(sc))
        return round(sc, 2)
    else:
        sc = total_score['pos']/len(scores)
        print ('\n' + yellow + '[+] Sentiment score... ' + normal + str(sc))
        return round(sc, 2)

def lexical_density_and_readability_analysis(text, allow_digits=False):
    """'text' variable: representation of the text to be analysed.
    Returns a pair of values:
        lexical density score
        readability score
    """
    print "[+] Tokenizing text..."
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+|[^\w\s]+')
    tokens = tokenizer.tokenize(text)

    print "[+] Tagging tokens..."
    tagger = nltk.UnigramTagger(nltk.corpus.brown.tagged_sents())
    tagged_tokens = tagger.tag(tokens)

    print "[+] Tallying tags..."
    lexical_counter = collections.Counter()
    personal_pronoun_counter = collections.Counter()
    adjective_counter = collections.Counter()
    adverb_counter = collections.Counter()
    noun_counter = collections.Counter()
    verb_counter = collections.Counter()

    for token in tagged_tokens:

        if token[1] == None:
            continue

        # Adjectives
        elif 'JJ' in token[1]:
            lexical_counter[token[0]] += 1
            adjective_counter[token[0]] += 1

        elif 'JJR' in token[1]:
            lexical_counter[token[0]] += 1
            adjective_counter[token[0]] += 1

        elif 'JJS' in token[1]:
            lexical_counter[token[0]] += 1
            adjective_counter[token[0]] += 1

        # Nouns
        elif 'NN' in token[1]:
            lexical_counter[token[0]] += 1
            noun_counter[token[0]] += 1

        elif 'NNP' in token[1]:
            lexical_counter[token[0]] += 1
            noun_counter[token[0]] += 1

        elif 'NNPS' in token[1]:
            lexical_counter[token[0]] += 1
            noun_counter[token[0]] += 1

        elif 'NNS' in token[1]:
            lexical_counter[token[0]] += 1
            noun_counter[token[0]] += 1

        # Adverbs
        elif 'RB' in token[1]:
            lexical_counter[token[0]] += 1
            adverb_counter[token[0]] += 1

        elif 'RBR' in token[1]:
            lexical_counter[token[0]] += 1
            adverb_counter[token[0]] += 1

        elif 'RBS' in token[1]:
            lexical_counter[token[0]] += 1
            adverb_counter[token[0]] += 1

        # Verbs
        elif 'VB' in token[1]:
            lexical_counter[token[0]] += 1
            verb_counter[token[0]] += 1

        elif 'VBD' in token[1]:
            lexical_counter[token[0]] += 1
            verb_counter[token[0]] += 1

        elif 'VBG' in token[1]:
            lexical_counter[token[0]] += 1
            verb_counter[token[0]] += 1

        elif 'VBN' in token[1]:
            lexical_counter[token[0]] += 1
            verb_counter[token[0]] += 1

        elif 'VBP' in token[1]:
            lexical_counter[token[0]] += 1
            verb_counter[token[0]] += 1

        elif 'VBZ' in token[1]:
            lexical_counter[token[0]] += 1
            verb_counter[token[0]] += 1

        # Personal pronouns
        elif 'PPS' in token[1]:
            lexical_counter[token[0]] += 1
            personal_pronoun_counter[token[0]] += 1

    print "[+] Counting sentences..."
    total_sentences = len(nltk.sent_tokenize(text.decode('utf-8')))
    print ('|#|' + yellow + '[+] Total number of sentences... ' + normal + str(total_sentences))

    print "[+] Split text into words..."
    if allow_digits:
        words = re.findall(r"['\-\w]+", text)
    else:
        words = re.findall(r"['\-A-Za-z]+", text)

    total_words = 0.0
    total_chars = 0
    for word in words:

        word = word.strip(r"&^%$#@!")

        # Allow hyphenated words, but not hyphens as words on their own.
        if word == '-':
            continue

        # Record lengths of every word
        length = len(word)

        # Record total number of words and chars
        total_words += 1
        total_chars += length
    print ('|##|' + yellow + ' Total words... ' + normal + str(total_words))
    print ('|###|' + yellow + ' Total chars... ' + normal + str(total_chars))

    # Calculate the lexical density of the text.
    total_meaningful_words = sum(lexical_counter.values())
    lexical_density = 100.0 * total_meaningful_words / float(total_words)

    # Calculate the ARI (readability) score
    ASL = total_words / float(total_sentences)
    ALW = total_chars / float(total_words)
    ARI_score = (0.5 * ASL) + (4.71 * ALW) - 21.43

    print ('|####|' + yellow + ' Lexical density score... ' + normal + str(round(lexical_density, 2)) + '%')
    print ('|#####|' + yellow + ' Readability score... ' + normal + str(round(ARI_score, 2)))

    return round(lexical_density, 2), round(ARI_score, 2)

def sliding_window(text):
    """Function slides through given text with fixed window size and fixed
    sliding step:
    window_size and slid_size variables respectivelly
    Returns a set of data that is a representation of
    extraxted features from given text
    """
    window_size = 200 # Assumably average amount of words that could be read out load per minute
    slide_size = 50 # For efficiency purpose, slid_size should be 1/4 of window_size
    extracted_features = [] # Stores features extracted from text piece
    text_words = []

    for word in text.split(): # Get a list of all words in the teext sample
        text_words.append(word)

    if (len(text_words) <= window_size) or (len(text_words)-window_size <= slide_size):
        sample = ' '.join(text_words) # Join words into set of sentence, that would be analysed
        print '\n===' + blue + ' Analysing new sentence...' + normal + '==='
        print ('\n' + green + '[+] Start sentiment analysis...' + normal)
        sentiment = sentiment_analysis(sample)
        print ('\n' + green + 'Sentiment analysis is done!' + normal)

        print ('\n' + green + '[+] Start lexical density & \n readability analysis...' + normal)
        lexical, readability = lexical_density_and_readability_analysis(sample)
        print ('\n' + green + 'Lexical density & readability analysis is done!' + normal)
        extracted_features.append((sentiment, (lexical, readability)))
    else:
        for i in xrange(0, len(text_words)-window_size, slide_size):
            sample = ' '.join(text_words[i:i+200])
            print '\n===' + blue + ' Analysing new sentence...' + normal + '==='
            print ('\n' + green + '[+] Start sentiment analysis...' + normal)
            sentiment = sentiment_analysis(sample)
            print ('\n' + green + 'Sentiment analysis is done!' + normal)

            print ('\n' + green + '[+] Start lexical density & \n readability analysis...' + normal)
            lexical, readability = lexical_density_and_readability_analysis(sample)
            print ('\n' + green + 'Lexical density & readability analysis is done!' + normal)
            extracted_features.append((sentiment, (lexical, readability)))

    return extracted_features

def run_text_analysis():
    """Methods runs all functions described above over all text files and
    Returns a set of extracted features
    as an array of the form (sentiment, (lexical_score, readability_score))
    """
    # Find file that holds extracted features
    dump_results = [f for f in listdir(".") if (isfile(join(".", f)) and ("extracted_features" in f))]

    # If such file exists, then load file and return features
    if dump_results:
        print '\n===' + turquoise + ' PREVIOUS RESULTS FOUND... ' + normal + dump_results[0] + '==='
        print '\n===' + turquoise + ' LOADING RESULTS...' + normal + '==='
        results = pickle.load( open(dump_results[0], 'rb'))
        print '\n===' + turquoise + ' LOAD IS COMPLETED!' + normal + '==='
        return results
    # Otherwise initiate feature extraction process
    else:
        # Load text and clean it
        book_name = "o-henry.epub"
        print '\n===' + blue + ' READ IN THE BOOK... ' + normal + book_name + '==='
        read_in_epub(book_name)
        print '\n===' + blue + ' CLEAN UP THE TEXT...' + normal + '==='
        extract_text()

        # Give user a chance to manually clean output files to improve results
        while True:
            user_input = raw_input("\n You are given option to do manual cleaning. Type in [Done]/[done] or [d], when finished, otherwise press any key to skip: ")
            if user_input=='Done' or user_input=='done' or user_input=='d':
                print '\n===' + blue + ' MANUAL CLEANING IS DONE... ' + normal + '==='
                break
            else:
                print '\n===' + red + ' MANUAL CLEANING HAS BEEN SKIPPED... ' + normal + '==='
                break

        # Start sliding window to get text features
        files = [f for f in listdir(".") if (isfile(join(".", f)) and ("clean_output_" in f))]
        results = []
        print '\n===' + blue + ' STARTING ANALYSIS ' + normal + '==='
        for file_name in files:
            print "\n [+] Reading text from '" + file_name + "'..."
            text = open(file_name).read().lower()
            results.append(sliding_window(text))

        print '\n===' + blue + ' RESULTS ' + normal + '==='

        # Save results to save time on next run
        pickle.dump(results, open("extracted_features.p", "wb"))

        return results

# Test run
#start = time.time()
#features = run_text_analysis()
#print features
#print time.time() - start
