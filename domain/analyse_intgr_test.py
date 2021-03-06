import pytest
from datetime import timedelta
from unittest.mock import MagicMock

from domain.analyse import Analyser, Word, PartOfSpeach, WordIgnoreType
from domain.corpus import Corpus, CorpusDatabase
from domain.excerpt import Excerpt
from domain.parse import Parser, Sentence


CACHE = {}
CORPUS = Corpus(CorpusDatabase.MIN)


def cached_analyse(text):
    if text in CACHE:
        return CACHE[text]

    loader_mock = MagicMock()
    subtitle_mock = MagicMock(text=text)
    loader_mock.load = MagicMock(return_value=subtitle_mock)
    analyser = Analyser(loader_mock, Parser(), CORPUS)

    result = analyser.analyse('<id>')

    CACHE[text] = result
    return result


def test_analysis_yields_subtitle():
    text = '''\
1
00:01:00,000 --> 00:01:03,000
I hoped to see my friend
and shake his hand.
'''
    subtitle, _ = cached_analyse(text)
    assert subtitle.text == text


def test_analysis_yields_lang_frequencies():
    text = '''\
1
02:11:39,473 --> 02:11:42,375
I hoped to see my friend
and shake his hand.
'''
    _, analysis = cached_analyse(text)

    assert dict(analysis.token_with_lang_freq) == {
        'friend': 243502,
        'hand': 161068,
        'hop': 7928,
        'see': 1386818,
        'shake': 20029
    }


def test_analysis_yields_movie_frequencies():
    text = '''\
1
02:11:39,473 --> 02:11:42,375
I hoped to see my friend
and shake his hand.
'''
    _, analysis = cached_analyse(text)

    assert dict(analysis.word_with_movie_freq) == {
        Word('I', PartOfSpeach.OTHER): 1,
        Word('and', PartOfSpeach.OTHER): 1,
        Word('friend', PartOfSpeach.NOUN): 1,
        Word('hand', PartOfSpeach.NOUN): 1,
        Word('his', PartOfSpeach.OTHER): 1,
        Word('hop', PartOfSpeach.VERB): 1,
        Word('my', PartOfSpeach.OTHER): 1,
        Word('see', PartOfSpeach.VERB): 1,
        Word('shake', PartOfSpeach.VERB): 1,
        Word('to', PartOfSpeach.OTHER): 1
    }


def test_analysis_yields_excerpts():
    text = '''\
1
02:11:39,473 --> 02:11:42,375
I hoped to see my friend.
I hoped.
'''
    _, analysis = cached_analyse(text)

    s1 = Sentence('I hoped to see my friend.', timedelta(0, 7899, 473000))
    s2 = Sentence('I hoped.', timedelta(0, 7899, 473000))

    assert dict(analysis.word_with_excerpts) == {
        Word('I', PartOfSpeach.OTHER): [Excerpt([s1, s2], 'I'),
                                        Excerpt([s1, s2], 'I')],
        Word('hop', PartOfSpeach.VERB): [Excerpt([s1, s2], 'hoped'),
                                         Excerpt([s1, s2], 'hoped')],
        Word('to', PartOfSpeach.OTHER): [Excerpt([s1, s2], 'to')],
        Word('see', PartOfSpeach.VERB): [Excerpt([s1, s2], 'see')],
        Word('my', PartOfSpeach.OTHER): [Excerpt([s1, s2], 'my')],
        Word('friend', PartOfSpeach.NOUN): [Excerpt([s1, s2], 'friend')]
    }


def test_analysis_ignores_stopwords():
    text = '''\
1
00:01:00,000 --> 00:01:03,000
I hoped to see my friend
and shake his hand.
'''
    _, analysis = cached_analyse(text)

    expected_stopwords = set(['and', 'to', 'his', 'my'])
    actual_stopwords = set(w.token for w, r in analysis.word_with_ignore_reason.items()
                           if r == WordIgnoreType.STOPWORD)
    assert actual_stopwords == expected_stopwords

    actual_words = analysis.token_with_lang_freq.keys()
    expected_words = set(['shake', 'see', 'friend', 'hand', 'hop'])
    assert actual_words == expected_words


def test_analysis_ignores_unknown_words():
    text = '''\
1
00:01:00,000 --> 00:01:03,000
I hoped to see my friend
and shake his weirdnonsenseword.
'''
    _, analysis = cached_analyse(text)

    unknown_word = Word('weirdnonsenseword', PartOfSpeach.NOUN)
    assert unknown_word in analysis.word_with_ignore_reason
    assert analysis.word_with_ignore_reason[unknown_word] == WordIgnoreType.UNKNOWN


def test_analysis_skips_word_subtitle_entirely():
    text = '''\
1
00:01:00,000 --> 00:01:03,000
Subtitle ... subtitle ... SUBTITLE!
'''
    _, analysis = cached_analyse(text)

    assert not analysis.word_with_ignore_reason
    assert not analysis.token_with_lang_freq


def test_analysis_skips_non_words_entirely():
    text = '''\
1
00:01:00,000 --> 00:01:03,000
42! test0.
'''
    _, analysis = cached_analyse(text)

    assert not analysis.word_with_ignore_reason
    assert not analysis.token_with_lang_freq


def test_analysis_ignores_words_with_unknown_frequency():
    text = '''\
1
00:01:00,000 --> 00:01:03,000
I hoped to see my friend
and shake his moustache.
'''
    _, analysis = cached_analyse(text)

    unknown_freq_word = Word('moustache', PartOfSpeach.NOUN)
    assert unknown_freq_word in analysis.word_with_ignore_reason
    assert analysis.word_with_ignore_reason[unknown_freq_word] == WordIgnoreType.UNKNOWN_FREQ


def test_analysis_fails_when_no_subtitle():
    with pytest.raises(RuntimeError, message='no subtitle found for movie <id>'):
        loader_mock = MagicMock()
        loader_mock.load = MagicMock(return_value=None)

        analyser = Analyser(loader_mock, Parser(), CORPUS)
        analyser.analyse('<id>')
