import unittest
import tempfile
import shutil
import os

from opustools.util import file_open
from opustools.parse.block_parser import BlockParser

class TestBlockParser(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tempdir = tempfile.mkdtemp()

        self.xml_path = os.path.join(self.tempdir, 'test.xml')
        with open(self.xml_path, 'w') as test_xml:
            test_xml.write("""<?xml version="1.0"?>
                <parent id="top"> <child1 name="paul">Text <stamp>123</stamp>
                goes here</child1>
                <child2 name="fred">More <stamp>321</stamp>text</child2>
                </parent>""")

        self.align_path = os.path.join(self.tempdir, 'align.xml')
        with open(self.align_path, 'w') as align_xml:
            align_xml.write("""<?xml version="1.0" encoding="utf-8"?>
                <!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">
                <cesAlign version="1.0">
                <linkGrp targType="s" fromDoc="en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" toDoc="fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" >
                <link xtargets="s1;s1" id="SL1"/>
                <link xtargets="s2;s2" id="SL2"/>
                  </linkGrp>
                </cesAlign>
                """)

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

    def test_initialize_block_parser(self):
        with file_open(self.xml_path) as f:
            bp = BlockParser(f)

    def test_parse_line(self):
        with file_open(self.xml_path) as f:
            bp = BlockParser(f)
            line = bp.document.readline()
            bp.parse_line(line)

    def test_get_complete_blocks(self):
        with file_open(self.xml_path) as f:
            bp = BlockParser(f, data_tag='stamp')
            blocks = list(bp.get_complete_blocks())
            self.assertEqual(blocks[0].name, 'stamp')
            self.assertEqual(blocks[0].data, '123')
            self.assertEqual(blocks[0].parent.name, 'child1')
            self.assertEqual(blocks[1].name, 'stamp')
            self.assertEqual(blocks[1].data, '321')
            self.assertEqual(blocks[1].parent.name, 'child2')

    def test_parse_document(self):
        with file_open(self.xml_path) as f:
            bp = BlockParser(f)
            for block in bp.get_complete_blocks():
                pass

    def test_parsing_alignment(self):
        with file_open(self.align_path) as f:
            bp = BlockParser(f, data_tag='link')
            blocks = list(bp.get_complete_blocks())
            self.assertEqual(blocks[0].parent.name, 'linkGrp')
            self.assertEqual(blocks[0].attributes['xtargets'], 's1;s1')

    def test_parsing_books(self):
        with file_open(self.books_path) as f:
            bp = BlockParser(f, data_tag='w')
            blocks = list(bp.get_complete_blocks())
            self.assertEqual(blocks[19].name, 'w')
            self.assertEqual(blocks[19].data, 'Project')
            self.assertEqual(blocks[19].attributes['tree'], 'NP')
            self.assertEqual(blocks[19].parent.name, 'chunk')
            self.assertEqual(blocks[19].parent.parent.name, 's')
            self.assertEqual(blocks[19].parent.parent.attributes['id'], 's1')

    def test_parsing_books_raw(self):
        with file_open(self.books_raw_path) as f:
            bp = BlockParser(f, data_tag='s')
            blocks = list(bp.get_complete_blocks())
            self.assertEqual(blocks[2].name, 's')
            self.assertEqual(blocks[2].attributes['id'], 's3')
            self.assertEqual(blocks[2].data, 'Victor Hugo')

    def test_parsing_os(self):
        with file_open(self.os_path) as f:
            bp = BlockParser(f, data_tag='s')
            blocks = list(bp.get_complete_blocks())
            self.assertEqual(blocks[0].children[0].name, 'time')
            self.assertEqual(blocks[0].name, 's')
            self.assertEqual(blocks[0].children[1].name, 'w')
            self.assertEqual(blocks[0].children[1].parent.name, 's')
            self.assertEqual(blocks[1].children[0].name, 'w')
            self.assertEqual(blocks[1].children[0].parent.attributes['id'], '2')

    def test_parsing_os_raw(self):
        with file_open(self.os_raw_path) as f:
            bp = BlockParser(f, data_tag='s')
            blocks = list(bp.get_complete_blocks())
            self.assertEqual(blocks[0].children[0].name, 'time')
            self.assertEqual(blocks[0].name, 's')
            self.assertEqual(blocks[1].name, 's')
            self.assertEqual(blocks[0].data.strip(), '- How\'d you score that?')
            self.assertEqual(blocks[0].parent.name, 'document')

    def test_get_raw_tag(self):
        with file_open(self.os_path) as f:
            bp = BlockParser(f, data_tag='s')
            blocks = list(bp.get_complete_blocks())
            self.assertEqual(blocks[0].children[0].get_raw_tag(),
                    '<time id="T1S" value="00:00:05,897" />')
            self.assertEqual(blocks[0].children[1].get_raw_tag(), '<w id="1.1">-</w>')
