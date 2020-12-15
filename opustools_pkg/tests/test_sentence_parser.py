import unittest
import tempfile
import shutil
import os

from opustools.parse.block_parser import BlockParser
from opustools.parse.sentence_parser import SentenceParser
from opustools.util import file_open

class TestSentenceParser(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tempdir = tempfile.mkdtemp()

        self.books_path = os.path.join(self.tempdir, 'books.xml')
        with open(self.books_path, 'w') as books_xml:
            books_xml.write("""<?xml version="1.0" encoding="utf-8"?>
                <text><head>
                <meta id="1">
                 <w id="w1.1">Notre-Dame</w>
                 <w id="w1.2">de</w>
                 <w id="w1.3">Paris</w>
                 <w id="w1.4">by</w>
                 <w id="w1.5">Victor</w>
                 <w id="w1.6">Hugo</w>
                 <w id="w1.7">Aligned</w>
                 <w id="w1.8">by</w>
                 <w id="w1.9">:</w>
                 <w id="w1.10">Unknown</w>
                 <w id="w1.11">&amp;</w>
                 <w id="w1.12">András</w>
                 <w id="w1.13">Farkas</w>
                 <w id="w1.14">(</w>
                 <w id="w1.15">fully</w>
                 <w id="w1.16">reviewed</w>
                 <w id="w1.17">)</w>
                </meta></head><body>
                <s id="s1">
                 <chunk type="NP" id="c1-1">
                  <w hun="NN" tree="NN" lem="source" pos="NN" id="w1.1">Source</w>
                 </chunk>
                 <w hun=":" tree=":" lem=":" pos=":" id="w1.2">:</w>
                 <chunk type="NP" id="c1-3">
                  <w hun="NNP" tree="NP" lem="Project" pos="NNP" id="w1.3">Project</w>
                  <w hun="NNP" tree="NP" pos="NNP" id="w1.4">GutenbergTranslation</w>
                 </chunk>
                </s>
                """)

        self.books_raw_path = os.path.join(self.tempdir, 'books_raw.xml')
        with open(self.books_raw_path, 'w') as books_raw_xml:
            books_raw_xml.write("""<?xml version="1.0" encoding="UTF-8"?>

                <text>
                 <head>
                  <meta> Notre-Dame de Paris
                 by Victor Hugo
                 Aligned by: Unknown &amp; András Farkas (fully reviewed)
                 </meta>
                 </head>
                 <body>
                  <s id="s1">Source: Project GutenbergTranslation: Isabel F. HapgoodAudiobook available here</s>
                  <s id="s2">Hunchback of Notre-Dame</s>
                  <s id="s3">Victor Hugo</s>
                """)

        self.os_path = os.path.join(self.tempdir, 'os.xml')
        with open(self.os_path, 'w') as os_xml:
            os_xml.write("""<?xml version="1.0" encoding="utf-8"?>
                <document id="4296906">
                  <s id="1">
                    <time id="T1S" value="00:00:05,897" />
                    <w id="1.1">-</w>
                    <w id="1.2">How</w>
                    <w id="1.3">'d</w>
                    <w id="1.4">you</w>
                    <w id="1.5">score</w>
                    <w id="1.6">that</w>
                    <w id="1.7">?</w>
                  </s>
                  <s id="2">
                    <w id="2.1">-</w>
                    <w id="2.2">Mike</w>
                    <w id="2.3">the</w>
                    <w id="2.4">groundskeeper</w>
                    <w id="2.5">.</w>
                    <time id="T1E" value="00:00:08,654" />
                  </s>
                  """)

        self.os_raw_path = os.path.join(self.tempdir, 'os_raw.xml')
        with open(self.os_raw_path, 'w') as os_raw_xml:
            os_raw_xml.write("""<?xml version="1.0" encoding="utf-8"?>
                <document id="4296906">
                  <s id="1">
                    <time id="T1S" value="00:00:05,897" />
                - How'd you score that?
                  </s>
                  <s id="2">
                - Mike the groundskeeper.
                    <time id="T1E" value="00:00:08,654" />
                  </s>
                  """)


    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.tempdir)

    def test_store_sentences(self):
        with file_open(self.books_path) as f:
            sp = SentenceParser(f, preprocessing='xml')
            sp.sentences = get_dict(sp.sentences({'s1'}))
            self.assertEqual(sp.sentences['s1'][0],
                    'Source : Project GutenbergTranslation')
        with file_open(self.books_raw_path) as f:
            sp = SentenceParser(f, preprocessing='raw')
            sp.sentences = get_dict(sp.sentences({'s1'}))
            self.assertEqual(sp.sentences['s1'][0],
                    'Source: Project GutenbergTranslation: Isabel F. '
                    'HapgoodAudiobook available here')
        with file_open(self.os_path) as f:
            sp = SentenceParser(f, preprocessing='xml')
            sp.sentences = get_dict(sp.sentences({'1'}))
            self.assertEqual(sp.sentences['1'][0], "- How 'd you score that ?")
        with file_open(self.os_raw_path) as f:
            sp = SentenceParser(f, preprocessing='raw')
            sp.sentences = get_dict(sp.sentences({'1'}))
            self.assertEqual(sp.sentences['1'][0], "- How'd you score that?")

    def test_get_annotations(self):
        with file_open(self.books_path) as f1, file_open(self.books_path) as f2:
            bp = BlockParser(f1, data_tag='w')
            sp = SentenceParser(f2)
            blocks = list(bp.get_complete_blocks())
            self.assertEqual(sp.get_annotations(blocks[17]), '|NN|w1.1|source|NN|NN')
        with file_open(self.books_path) as f1, file_open(self.books_path) as f2:
            bp = BlockParser(f1, data_tag='w')
            sp = SentenceParser(f2, anno_attrs=['pos'])
            blocks = list(bp.get_complete_blocks())
            self.assertEqual(sp.get_annotations(blocks[17]), '|NN')

    def test_get_sentence(self):
        with file_open(self.books_raw_path) as f:
            sp = SentenceParser(f, preprocessing='raw')
            sp.sentences = get_dict(sp.sentences({'s2', '0'}))
            self.assertEqual(sp.sentences['s2'][0], 'Hunchback of Notre-Dame')
            self.assertEqual('0' in sp.sentences, False)

    def test_read_sentence(self):
        with file_open(self.books_raw_path) as f:
            sp = SentenceParser(f, preprocessing='raw')
            sp.sentences = get_dict(sp.sentences({'s1', 's2'}))
            self.assertEqual(sp.sentences['s2'][0],
                    'Hunchback of Notre-Dame')
            self.assertEqual([sp.sentences['s1'][0], sp.sentences['s2'][0]],
                    ['Source: Project GutenbergTranslation: Isabel F. '
                    'HapgoodAudiobook available here', 'Hunchback of '
                    'Notre-Dame'])

    def test_read_sentence_new(self):
        with file_open(self.books_raw_path) as f:
            sp = SentenceParser(f, preprocessing='raw')
            sp.sentences = get_dict(sp.sentences({'s1', 's2'}))
            self.assertEqual(sp.sentences['s2'],
                    ('Hunchback of Notre-Dame', {'id': 's2'}))
            self.assertEqual([sp.sentences['s1'][0], sp.sentences['s2'][0]],
                    ['Source: Project GutenbergTranslation: Isabel F. HapgoodAudiobook '
                        'available here', 'Hunchback of Notre-Dame'])

def get_dict(sentences):
    return {sid: attrs for sid, attrs in sentences}
