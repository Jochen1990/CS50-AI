import nltk
import sys
import os
from nltk.tokenize import word_tokenize
import math
import string

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    dictionary = {}
    for filename in os.listdir(directory):
        file = open(os.path.join(directory, filename), "r")
        dictionary[filename] = file.read()
    return dictionary


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = nltk.word_tokenize(document.lower())

    stopwords = set(nltk.corpus.stopwords.words('english'))

    punctuation = set(string.punctuation)

    to_be_removed = set()

    n = len(words)


    for i in range(0, n):
        word = words[i]
        if word in stopwords or word in punctuation:
            to_be_removed.add(word)

    return [word for word in words if word not in to_be_removed]



def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = dict()

    for filename in documents.keys():
        for word in documents[filename]:
            if word in idfs.keys():
                idfs[word] += 1
            else:
                idfs[word] = 1

    num_docs = len(documents.keys())
    for word in idfs.keys():
        frequency = idfs[word]
        idf = math.log(num_docs / frequency)
        idfs[word] = idf
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidfs = []
    for file in files:
        tfidf = 0
        for q in query:
            if q in files[file]:
                tfidf += idfs[q] * files[file].count(q)
        if tfidf == 0:
            continue
        tfidfs.append((file, tfidf))

    tfidfs.sort(key=lambda tfidf: tfidf[1])
    return [x[0] for x in tfidfs[:n]]



def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentences_idfs = []
    for sentence in sentences:
        idf = 0
        matches = 0
        for q in query:
            if q in sentences[sentence]:
                idf += idfs[q]
                matches += 1
        query_dense = float(matches/len(sentences[sentence]))
        sentences_idfs.append((sentence, idf, query_dense))

    sentences_idfs.sort(key=lambda x: (x[1], x[2]), reverse=True)

    return [x[0] for x in sentences_idfs[:n]]


if __name__ == "__main__":
    main()
