from typing import List
from nltk import corpus
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from stories.dict.the_eyes import corpus as the_eyes_corpus
from timeit import timeit

# python -m nltk.downloader 'punkt'
# python -m nltk.downloader 'stopwords'


# tokenized_corpus: List[str] = word_tokenize(the_eyes_corpus)
stop_words_init = set(stopwords.words("english"))
extra = {
    ",",
    ".",
    "*",
    ":",
    ";",
    "...",
    "'",
    "'s",
    "``",
    "''",
    "n't",
    "!",
    "?",
    "?!",
    "-",
    "--",
    "_",
    "(",
    ")",
    "'d",
    "'m",
}

def show_stats(word_count: int, chars: int):
    print("-----------Stats------------")
    print(f"word count = {word_count}")
    print(f"char length = {chars}")
    

def filter_with_stop_words():
    tokenized_corpus: List[str] = word_tokenize(the_eyes_corpus)
    stop_words = stop_words_init.union(extra)

    filtered_corpus = [
        word for word in tokenized_corpus if word.casefold() not in stop_words
    ]
    return filtered_corpus

def filter_extra_only():
    tokenized_corpus: List[str] = word_tokenize(the_eyes_corpus)
    filtered_corpus_with_stop = [
        word for word in tokenized_corpus if word.casefold() not in extra
    ]
    return filtered_corpus_with_stop

def split_tokenizer()->List[str]:
    splitted = the_eyes_corpus.split()
    return splitted

def _make_segment(splitted_corpus: List[str], segment_size: int = 50):
    corpus_word_count = len(splitted_corpus)
    print(f"len = {corpus_word_count}")

    # for idx, word in enumerate(splitted_corpus):
    segments = []
    counter = 0
    for i in range(0,corpus_word_count,segment_size):
        # segment.append(" ".join(splitted_corpus))
        print(f"i = {i}")
        segment = splitted_corpus[i:segment_size+i]
        print(f"segment length = {len(segment)}")
        print(f"segment = {segment}")
        joined = " ".join(segment)
        print(joined)
        counter += 1

    print(f">>>>>>>>>>>>count of segments = {counter}")
    # return " ".join(splitted_corpus)

def make_segment(splitted_corpus: List[str], segment_size: int = 50):
    
    corpus_word_count = len(splitted_corpus)
    segments = []
    counter = 0
    
    for i in range(0,corpus_word_count,segment_size):
        segment_words = splitted_corpus[i:segment_size+i]
        segment_text = " ".join(segment_words)

        if len(segment_words) < segment_size:
            n = len(segment_words)
            print(f"has residue => needs {segment_size - n} more words")
        segments.append(segment_text)
        counter += 1

    print(f"counter = {counter}")
    print(f"num segments {len(segments)}")



def analyse_time():
    exe_time_nltk = timeit(stmt=filter_extra_only, number=1)
    exe_time_split = timeit(stmt=split_tokenizer, number=1)

    print(f"Execution time with NLTK = {exe_time_nltk}")
    print(f"Execution time with split = {exe_time_split}")

    if exe_time_nltk > exe_time_split:
        print("NLTK took longer")
    else:
        print("split took longer")



if __name__ == '__main__':
    # filtered_corpus = filter_extra_only()
    
    # for w in filtered_corpus:
    #     print(w)
    
    # word_count = len(filtered_corpus)
    # print(word_count)

    # sp = split_tokenizer()
    # for w in sp:
    #     print(w)
    # print(len(sp))
    
    splitted = split_tokenizer()
    # segment = make_segment(splitted_corpus=splitted[0:51])
    make_segment(splitted_corpus=splitted)
    # print(segment)