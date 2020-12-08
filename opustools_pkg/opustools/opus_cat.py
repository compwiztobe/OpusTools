import argparse
import zipfile
import os

from .opus_get import OpusGet
from .parse.sentence_parser import SentenceParser

def parse_type(preprocessing, get_annotations):
    def xml_parse(bp, block, sentence, sentences, id_set):
        if block.name == 's':
            sid = block.attributes['id']
            sentence = ' '.join(sentence)
            sentences[sid] = (sentence, block.attributes)
            sentence = []
        elif block.name == 'w':
            s_parent = bp.tag_in_parents('s', block)
            if s_parent:
                data = block.data.strip()
                sentence.append(data)
        return sentence

    def parsed_parse(bp, block, sentence, sentences, id_set):
        s_parent = bp.tag_in_parents('s', block)
        if block.name == 's':
            sid = block.attributes['id']
            sentence = ' '.join(sentence)
            sentences[sid] = (sentence, block.attributes)
            sentence = []
        elif block.name == 'w':
            s_parent = bp.tag_in_parents('s', block)
            if s_parent:
                data = block.data.strip()
                data += get_annotations(block)
                sentence.append(data)
        return sentence

    if preprocessing == 'xml':
        return xml_parse
    if preprocessing == 'parsed':
        return parsed_parse

class SentenceParser(SentenceParser):

    def __init__(self, document, preprocessing, set_attribute,
            change_annotation_delimiter):
        """Read sentence from a xml document.

        Arguments:
        document -- Xml document
        preprocessing -- Preprocessing type, xml or parsed
        set_attribute -- Set annotation attributes to be printed
        change_annotation_delimiter -- Change annotation delimiter
        """

        super().__init__(document, preprocessing, set_attribute,
                change_annotation_delimiter, None)

        self.parse_block = parse_type(preprocessing, self.get_annotations)

class OpusCat:

    def __init__(self, directory=None, language=None, no_ids=False,
            maximum=-2, plain=False, file_name=None, release='latest',
            print_annotations=False, set_attribute=['pos', 'lem'],
            change_annotation_delimiter='|',
            root_directory='/proj/nlpl/data/OPUS', download_dir='.' ):
        """Print the contents of a xml sentence file.

        Keyword arguments:
        directory -- Name of the corpus directory
        language -- Language of the corpus
        no_ids -- Print sentences without ids in plain mode
        maximum -- Maximum number of sentences to be printed (default all)
        plain -- Print sentence in plain text
        file_name -- Print a specific file within a corpus
        release -- Corpus release version (default latest)
        print_annotations -- Print annotations
        set_attribute -- Set annotation attributes (default pos,lem)
        change_annotation_delimiter -- Change annotation delimiter (default |)
        root_directory -- Root directory for corpus files
            (default /proj/nlpl/data/OPUS)
        download_dir -- Directory where files will be downloaded (default .)
        """

        self.maximum = maximum
        self.directory = directory
        self.language = language
        self.release = release
        self.download_dir = download_dir
        self.set_attribute = set_attribute
        self.change_annotation_delimiter = change_annotation_delimiter
        self.no_ids = no_ids
        self.file_name = file_name
        self.plain = plain

        self.preprocess = 'parsed' if print_annotations else 'xml'

        self.localfile = os.path.join(download_dir, directory+'_'+release+'_xml_'+
                language+'.zip')
        self.defaultpath = os.path.join(root_directory, directory, 'latest', 'xml',
                language+'.zip')

    def openFile(self):
        """Open zip file."""
        try:
            try:
                return zipfile.ZipFile(self.localfile)
            except FileNotFoundError:
                return zipfile.ZipFile(self.defaultpath)
        except FileNotFoundError:
            print('\nRequested file not found. The following files are '
                'availble for downloading:\n')
            arguments = ['-d', self.directory, '-s', self.language, '-t', ' ',
                '-p', 'xml', '-l', '-r', self.release, '-dl',
                self.download_dir]
            arguments={'directory': self.directory, 'source': self.language,
                'target': ' ', 'preprocess': 'xml', 'list_resources': True,
                'release': self.release, 'download_dir': self.download_dir}
            og = OpusGet(**arguments)
            og.get_files()
            arguments['list_resources'] = False
            og = OpusGet(**arguments)
            og.get_files()
            try:
                return zipfile.ZipFile(self.localfile)
            except FileNotFoundError:
                print('No file found')

    def printFile(self, f):
        """Print sentences from a document."""
        if self.maximum == 0:
            return
        xml_break = False
        if self.plain:
            spar = SentenceParser(f, self.preprocess,
                self.set_attribute, self.change_annotation_delimiter)
            spar.store_sentences({})
            print('\n# '+f.name+'\n') # move this outside this function
            for sid, attrs in spar.sentences.items():
                if self.no_ids:
                    print(attrs[0])
                else:
                    print('("{}")>{}'.format(sid, attrs[0]))
                self.maximum -= 1
                if self.maximum == 0:
                    break
        else:
            for line in f:
                line = line.decode('utf-8')
                print(line, end='')
                if '</s>' in line:
                    self.maximum -= 1
                    if self.maximum == 0:
                        break

    def printSentences(self):
        """Print sentences from documents in a zip file."""
        with self.openFile() as z:
            if self.file_name:
                with z.open(self.file_name, 'r') as f:
                    self.printFile(f)
            else:
                for name in z.namelist():
                    if name.endswith('.xml'):
                        with z.open(name, 'r') as f:
                            self.printFile(f)
