"""
6.1010 Spring '23 Lab 9: Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    """
    Tree of prefixes with optional values. The length of the
    prefixes increase as you go down the tree.
    """

    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        else:
            if len(key) == 1:
                if key not in self.children:
                    self.children[key] = PrefixTree()
                self.children[key].value = value
            else:
                if key[0] not in self.children:
                    self.children[key[0]] = PrefixTree()
                self.children[key[0]].__setitem__(key[1:], value)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        else:
            if key[0] not in self.children:
                raise KeyError("key not in prefix tree")
            elif len(key) == 1:
                if self.children[key].value is None:
                    raise KeyError("key has no value")
                else:
                    return self.children[key].value
            else:
                return self.children[key[0]].__getitem__(key[1:])

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        else:
            if key == "" or key[0] not in self.children:
                raise KeyError("key not in prefix tree")
            elif len(key) == 1:
                if self.children[key].value is None:
                    raise KeyError("key has no value")
                else:
                    self.children[key].value = None
            else:
                self.children[key[0]].__delitem__(key[1:])

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        else:
            if key == "" or key[0] not in self.children:
                return False
            elif len(key) == 1:
                if self.children[key].value is None:
                    return False
                else:
                    return True
            else:
                return self.children[key[0]].__contains__(key[1:])

    def iter_with_beginning(self, start):
        for child in self.children:
            if self.children[child].value is not None:
                yield (start + child, self.children[child].value)
            if self.children[child].children != {}:
                yield from self.children[child].iter_with_beginning(start + child)

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        return self.iter_with_beginning("")


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    word_freq_tree = PrefixTree()
    word_freq_dict = {}
    text_words = set()
    sentences = tokenize_sentences(text)
    for sentence in sentences:
        sentence_words = sentence.split()
        for word in sentence_words:
            if word in text_words:
                word_freq_dict[word] += 1
            else:
                text_words.add(word)
                word_freq_dict[word] = 1
            word_freq_tree[word] = word_freq_dict[word]
    return word_freq_tree


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError(" must be a string")
    else:
        parent = tree
        for char in prefix:
            if char not in parent.children:
                return []
            else:
                parent = parent.children[char]
        wordcounts = [
            (prefix + wordcount[0], wordcount[1]) for wordcount in iter(parent)
        ]
        if prefix in tree:
            wordcounts.append((prefix, tree[prefix]))
        if max_count is None:
            return [wordcount[0] for wordcount in wordcounts]
        else:
            num_words = min(max_count, len(wordcounts))
            wordcounts.sort(key=lambda x: x[1], reverse=True)
            return [wordcounts[i][0] for i in range(num_words)]


def update_autocorrect(word, auto_set, new_set, tree, wordcounts):
    if word not in auto_set and word not in new_set and word in tree:
        new_set.add(word)
        wordcounts.append((word, tree[word]))


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    autocomplete_words = autocomplete(tree, prefix, max_count)
    num_auto = len(autocomplete_words)
    prefix_length = len(prefix)
    wordcounts = []

    if max_count is None or max_count > num_auto:
        auto_set = set(autocomplete_words)
        new_set = set()
        for i in range(prefix_length + 1):
            for letter in "abcdefghijklmnopqrstuvwxyz":
                insert_word = prefix[:i] + letter + prefix[i:]
                update_autocorrect(insert_word, auto_set, new_set, tree, wordcounts)
                if i < prefix_length:
                    replace_word = prefix[:i] + letter + prefix[i + 1 :]
                    update_autocorrect(
                        replace_word, auto_set, new_set, tree, wordcounts
                    )
            if i < prefix_length:
                delete_word = prefix[:i] + prefix[i + 1 :]
                update_autocorrect(delete_word, auto_set, new_set, tree, wordcounts)
            if i < prefix_length - 1:
                for j in range(i + 1, prefix_length):
                    swap_word = (
                        prefix[:i]
                        + prefix[j]
                        + prefix[i + 1 : j]
                        + prefix[i]
                        + prefix[j + 1 :]
                    )
                    update_autocorrect(swap_word, auto_set, new_set, tree, wordcounts)

        if max_count is None or max_count - num_auto >= len(new_set):
            return autocomplete_words + list(new_set)
        else:
            wordcounts.sort(key=lambda x: x[1], reverse=True)
            return autocomplete_words + [
                wordcounts[i][0] for i in range(max_count - num_auto)
            ]
    else:
        return autocomplete_words


def remove_consecutive_asterisks(pattern):
    new_pattern = ""
    i = 0
    while i < len(pattern):
        new_pattern += pattern[i]
        if pattern[i] == "*":
            while i < len(pattern) and pattern[i] == "*":
                i += 1
        else:
            i += 1
    return new_pattern


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    new_pattern = remove_consecutive_asterisks(pattern)

    if new_pattern == "":
        if tree.value is None:
            return []
        else:
            return [("", tree.value)]
    else:
        first = new_pattern[0]
        if first != "*":
            if first != "?" and first not in tree.children:
                return []
            elif first != "?":
                next_filter = word_filter(tree.children[first], new_pattern[1:])
                return [
                    (first + wordcount[0], wordcount[1]) for wordcount in next_filter
                ]
            else:
                next_filter = []
                for child in tree.children:
                    child_filter = word_filter(tree.children[child], new_pattern[1:])
                    next_filter += [
                        (child + wordcount[0], wordcount[1])
                        for wordcount in child_filter
                    ]
                return next_filter
        else:
            words = set()
            next_filter = []
            for child in tree.children:
                child_filter1 = word_filter(tree.children[child], new_pattern)
                for wordcount in child_filter1:
                    if child + wordcount[0] not in words:
                        next_filter.append((child + wordcount[0], wordcount[1]))
                        words.add(child + wordcount[0])
            filter2 = word_filter(tree, new_pattern[1:])
            for wordcount in filter2:
                if wordcount[0] not in words:
                    next_filter.append((wordcount[0], wordcount[1]))
                    words.add(wordcount[0])
            return next_filter


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
