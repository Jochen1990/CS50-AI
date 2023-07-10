import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # For example, if the corpus were {"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}},
    # the page was "1.html", and the damping_factor was 0.85, then the output of transition_model should be
    # {"1.html": 0.05, "2.html": 0.475, "3.html": 0.475}. This is because with probability 0.85,
    # we choose randomly to go from page 1 to either page 2 or page 3 (so each of page 2 or page 3 has probability
    # 0.425 to start), but every page gets an additional 0.05 because with probability 0.15 we choose randomly
    # among all three of the pages.

    # create empty dict for the return
    output = {}
    #get access to the sets of the page, if there are any
    dict_values = corpus[page]
    # handle the parsing if there are no outgoing links from ther page
    if len(dict_values) == 0:
        keys_list = list(corpus.keys())
        n = len(keys_list)
        for key in keys_list:
            probability = round(1/n, 3)
            output[key] = probability
        return output
    else:
        # set length as an int (including the page)
        keys_list = list(corpus.keys())
        n = len(keys_list)
        output[page] = round(((1-damping_factor)/n), 3)
        for i in dict_values:
            probability = (damping_factor * (1/(n-1)) + ((1-damping_factor)/n))
            output[i] = round(probability, 3)
        return output


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    dict_values = corpus.keys()
    dict_values = list(dict_values)
    start = random.choice(dict_values)
    sample = []
    sample.append(start)
    i = 0
    while i < n-1:
        k = []
        v = []
        for keys, values in transition_model(corpus, start, damping_factor).items():
            k.append(keys)
            v.append(values)

        data = random.choices(k, weights=v,k=100)
        start = random.choice(data)
        sample.append(start)
        i += 1
    rank = {}
    for keys in corpus:
        rank[keys] = sample.count(keys)/len(sample)

    return rank



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    rank = {}
    change = {}
    for keys in corpus:
        rank[keys] = 1/N
        change[keys] = True
    while True:
        if True not in change.values():
            break
        for keys in corpus:
            s = 0
            old_val = rank[keys]
            for i in corpus:
                if keys in corpus[i]:
                    s += (rank[i] / len(corpus[i]))
                elif corpus[i] == set():
                    s += rank[i] / N
            rank[keys] = (1 - damping_factor) / N + damping_factor * s
            new_val = rank[keys]
            if abs(new_val-old_val) <= 0.001:
                change[keys] = False
    s = 0
    for keys in rank:
        rank[keys] = rank[keys]
    for keys in rank:
        s += rank[keys]
    for keys in rank:
        rank[keys] /= s
    return rank


if __name__ == "__main__":
    main()
