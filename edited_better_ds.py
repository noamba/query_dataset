"""
Hello,

This is a primitive 'search engine'. It takes a file with queries and then
matchs and scores against a datatset of lines
consisting of 3 elements [id, item, brand].
It outputs the number of matches per query, the items matached and
their score ordered by descending score.

Scoring could be improved as only measuring:
Number of key-word occurances in entry
Full match (non-case sensitive)
Partial match on word beginning

names of files:

queries.txt
search_dataset.csv

Runs on Python 2 and 3
"""
import csv
from collections import defaultdict

def main():
    data_set = load_dataset()
    process_query_file('queries.txt', *data_set)


def load_dataset():
    """
    It is more efficient (O(n) vs. O(1)) to search a dictionary or a set 
    compared to a list as they are implemented with a hash.
    Therefore, the dataset is kept with 2 dictionaries where the values are sets.
    """
    items_original_form = defaultdict(set)
    items_by_keyword_start = defaultdict(set)
    items_by_id = defaultdict(set)

    with open('minimini.csv') as f:
        lines = csv.reader(f, delimiter=',')
        for line in lines:
            
            item_id, *descriptors = line 
            
            # save original form for output
            items_original_form[item_id] = descriptors

            # create 2 dictionaries for searching: 
            # 1. Key: 3 lower-case first letters of each word of item descriptors. Value: item ids. 
            # 2. Key: item id. Value: item descriptorsin lower-case.
            descriptors_set = set(" ".join(descriptors).lower().split())
            for d in descriptors_set:
                items_by_keyword_start[d[:3]].add(item_id) 
            items_by_id[item_id] = descriptors_set
            
    return (items_by_keyword_start,items_by_id, items_original_form)


def process_query_file(file, *data_set):
    with open(file) as f:
        for query_line in f:
            _process_one_query(query_line, *data_set)


def _process_one_query(query, items_by_keyword_start, items_by_id, items_original_form):
    keywords = query.lower().split()
    relevant_items_id = set()
    results = []

    # make set of items that have at least one word that starts the same as 
    # one word in query (first 3 letters)
    for k in keywords:
        relevant_items_id.update(items_by_keyword_start[k[:3]])
    
    # get score for each matching item
    for item_id in relevant_items_id:
        score = _calculate_score(keywords, items_by_id[item_id])
        if score > 0:
            results.append([str(score)] + items_original_form[item_id])

    _print_results(query, results)

    return 


def _calculate_score(keywords, item):
    score = 0
    item_length = len(item)
    # look for full words
    score, remaining_keywords, remaining_item =\
            _find_match(keywords, 
                            item,
                            "full_word",
                            1,
                            score)
    if remaining_keywords and remaining_item: 
        # look for partial words in remaining keywords and item words
        score, *__ =\
                _find_match(remaining_keywords, 
                                remaining_item,
                                "start_of_word",
                                0.3,
                                score)
    if score > 0:
        score = (float(score)/item_length)

    return score

def _find_match(keywords, item, match_type, points_for_similarity, score):

    # using local copies that will be consumed as item words and keywords are matched.
    # maintaining original items intact for next items and queries 
    remaining_item = item.copy() 
    remaining_keywords = keywords.copy()

    # using copies as cannot remove items from iterables as iterating on them
    remaining_keywords_copy = remaining_keywords.copy()
    for kw in remaining_keywords_copy:
        remaining_item_copy = remaining_item.copy()
        for word in remaining_item_copy:
            if (match_type == "full_word" and kw == word)\
                    or\
                    (match_type == "start_of_word" and (word.startswith(kw) or kw.startswith(word))):
            
                score += points_for_similarity 
                # if there was a match:
                # 1. remove words from remaining_item and query keywords 
                remaining_item.remove(word)
                remaining_keywords.remove(kw)
                # 2. stop looking for matches for this current keyword
                break

    return score, keywords, remaining_item


def _print_results(query_line, results):

    print (query_line, end="")
    print (len(results))

    results.sort(reverse=True)  # Will sort automatically by first element
    results = results[:10]
    for r in results:
        print (','.join(r))
    print ()

    return


if __name__ == "__main__":
    main()
