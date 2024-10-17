from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

SUMMARIZER = LsaSummarizer()

# 文章の要約
def text_summarize(text):
    parser = PlaintextParser.from_string(text, Tokenizer("japanese"))

    summary = SUMMARIZER(parser.document, 5)

    for sentence in summary:
        print(sentence)

if __name__ == '__main__':
    text_summarize('今日はいいてんき')
