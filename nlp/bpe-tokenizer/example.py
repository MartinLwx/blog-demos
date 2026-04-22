from collections import Counter, defaultdict
from pprint import pprint


class BPE:
    def __init__(
        self,
        corpus: list[str],
        vocab_size: int,
        max_iter: int | None = None,
        debug: bool = False,
    ):
        self.corpus = corpus
        self.vocab_size = vocab_size
        self.vocab = []
        self.word_freq = Counter()
        self.splits = {}  # e.g. highest: [high, est</w>]
        self.merges = {}  # e.g. [high, est</w>]: highest
        self.max_iter = max_iter
        self.debug = debug

    def train(self):
        """Train a BPE Tokenizer"""
        # count the word frequency
        for document in self.corpus:
            # split each document in corpus by whitespace
            words = document.split()
            self.word_freq += Counter(words)

        # initialize the self.splits
        for word in self.word_freq:
            self.splits[word] = list(word) + ["</w>"]

        if self.debug:
            print(f"Init splits: {self.splits}")

        alphabet = set()
        for word in self.word_freq:
            alphabet |= set(list(word))
        alphabet.add("</w>")

        self.vocab = list(alphabet)
        self.vocab.sort()

        cnt = 0
        while len(self.vocab) < self.vocab_size:
            if self.max_iter and cnt >= self.max_iter:
                break

            # find the most frequent pair
            pair_freq = self.get_pairs_freq()

            if len(pair_freq) == 0:
                print("No pair available")
                break

            pair = max(pair_freq, key=pair_freq.get)

            self.update_splits(pair[0], pair[1])

            if self.debug:
                print(f"Updated splits: {self.splits}")

            self.merges[pair] = pair[0] + pair[1]

            self.vocab.append(pair[0] + pair[1])

            if self.debug:
                print(
                    f"Most frequent pair({max(pair_freq.values())} times) "
                    f"is : {pair[0]}, {pair[1]}. Vocab size: {len(self.vocab)}"
                )

            cnt += 1

    def update_splits(self, lhs: str, rhs: str):
        """If we see lhs and rhs appear consecutively, we merge them"""
        for word, word_split in self.splits.items():
            new_split = []
            cursor = 0
            while cursor < len(word_split):
                if (
                    word_split[cursor] == lhs
                    and cursor + 1 < len(word_split)
                    and word_split[cursor + 1] == rhs
                ):
                    new_split.append(lhs + rhs)
                    cursor += 2
                else:
                    new_split.append(word_split[cursor])
                    cursor += 1
            self.splits[word] = new_split

            # if word_split != new_split:
            #     print(f"old: {word_split}")
            #     print(f"new: {new_split}")

    def get_pairs_freq(self) -> dict:
        """Compute the pair frequency"""
        pairs_freq = defaultdict(int)
        for word, freq in self.word_freq.items():
            split = self.splits[word]
            for i in range(len(split)):
                if i + 1 < len(split):
                    pairs_freq[(split[i], split[i + 1])] += freq

        return pairs_freq

    def tokenize(self, s: str) -> list[str]:
        splits = [list(t) + ["</w>"] for t in s.split()]

        for lhs, rhs in self.merges:
            for idx, split in enumerate(splits):
                new_split = []
                cursor = 0
                while cursor < len(split):
                    if (
                        cursor + 1 < len(split)
                        and split[cursor] == lhs
                        and split[cursor + 1] == rhs
                    ):
                        new_split.append(lhs + rhs)
                        cursor += 2
                    else:
                        new_split.append(split[cursor])
                        cursor += 1
                assert "".join(new_split) == "".join(split)
                splits[idx] = new_split

        return sum(splits, [])


corpus = ["highest", "higher", "lower", "lowest", "cooler", "coolest"]
bpe = BPE(corpus, vocab_size=17, debug=False)
bpe.train()
print(bpe.tokenize(" ".join(corpus)))
