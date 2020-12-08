from .block_parser import BlockParser, BlockParserError

class SentenceParserError(Exception):

    def __init__(self, message):
        """Raise error when sentence parsing fails.

        Arguments:
        message -- Error message to be printed
        """
        self.message = message

def parse_type(preprocess, preserve, get_annotations):
    """Select function to be used for parsing"""

    def parse_s(block, sentence, sentences):
        sid = block.attributes['id']
        sentence = ' '.join(sentence)
        sentences[sid] = (sentence, block.attributes)
        sentence = []
        return sentence

    def parse_s_raw(block, sentence, sentences):
        sid = block.attributes['id']
        sentence.append(block.data.strip())
        sentence = ' '.join(sentence)
        sentences[sid] = (sentence, block.attributes)
        sentence = []
        return sentence

    def parse_w(block, sentence, id_set):
        s_parent = block.tag_in_parents('s')
        if s_parent and s_parent.attributes['id'] in id_set:
            data = block.data.strip()
            sentence.append(data)
        return sentence

    def parse_w_parsed(block, sentence, id_set):
        s_parent = block.tag_in_parents('s')
        if s_parent and s_parent.attributes['id'] in id_set:
            data = block.data.strip()
            data += get_annotations(block)
            sentence.append(data)
        return sentence

    def parse_time(block, sentence, id_set):
        s_parent = block.tag_in_parents('s')
        if s_parent and s_parent.attributes['id'] in id_set:
            sentence.append(block.get_raw_tag())
        return sentence


    def xml(block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w(block, sentence, id_set)
        return sentence

    def raw(block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s_raw(block, sentence, sentences)
        return sentence

    def parsed(block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w_parsed(block, sentence, id_set)
        return sentence

    def xml_preserve(block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w(block, sentence, id_set)
        elif block.name == 'time':
            sentence = parse_time(block, sentence, id_set)
        return sentence

    def raw_preserve(block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s_raw(block, sentence, sentences)
        elif block.name == 'time':
            sentence = parse_time(block, sentence, id_set)
        return sentence

    def parsed_preserve(block, sentence, sentences, id_set):
        if block.name == 's' and block.attributes['id'] in id_set:
            sentence = parse_s(block, sentence, sentences)
        elif block.name == 'w':
            sentence = parse_w_parsed(block, sentence, id_set)
        elif block.name == 'time':
            sentence = parse_time(block, sentence, id_set)
        return sentence

    if preserve:
        if preprocess == 'xml':
            return xml_preserve
        if preprocess == 'raw':
            return raw_preserve
        if preprocess == 'parsed':
            return parsed_preserve
    else:
        if preprocess == 'xml':
            return xml
        if preprocess == 'raw':
            return raw
        if preprocess == 'parsed':
            return parsed


class SentenceParser:

    def __init__(self, document, preprocessing=None, anno_attrs=['all_attrs'],
            delimiter='|', preserve=None):
        """Parse xml sentence files that have sentence ids in any order.

        Arguments:
        document -- Xml file to be parsed
        preprocessing -- Preprocessing type of the document
        anno_attrs -- Which annotations will be printed
        delimiter -- Annotation attribute delimiter
        preserve -- Preserve inline tags
        """

        self.document = document
        self.delimiter = delimiter
        self.anno_attrs = anno_attrs

        self.parse_block = parse_type(preprocessing, preserve, self.get_annotations)

        self.sentences = {}
        self.done = False

        self.data_tag = 's' if preprocessing == 'raw' else 'w'

    def store_sentences(self, id_set):
        """Read document and store sentences in a dictionary."""
        bp = BlockParser(self.document, data_tag=self.data_tag)
        sentence = []
        sid = None
        try:
            blocks = bp.get_complete_blocks()
            while blocks:
                for block in blocks:
                    sentence = self.parse_block(
                            bp, block, sentence, self.sentences, id_set)
                blocks = bp.get_complete_blocks()
            bp.close_document()
        except BlockParserError as e:
            raise SentenceParserError(
                'Error while parsing sentence file {file}: {error}'.format(file=self.document.name, error=e.args[0]))

    def get_annotations(self, block):
        if 'all_attrs' in self.anno_attrs:
            return self.delimiter.join(block.attributes[a] for a in sorted(block.attributes))
        else:
            return self.delimiter.join(block.attributes[a] for a in self.anno_attrs if a in block.attributes)

    # unused outside of test cases - not useful functionality - remove
    def get_sentence(self, sid):
        """Return a sentence based on given sentence id."""
        return self.sentences.get(sid, ('', {}))

    # unused outside of test cases - not useful functionality - remove
    def read_sentence(self, ids):
        """Return a sequence of sentences based on given sentence ids."""
        if len(ids) == 0 or ids[0] == '':
            return [], []

        return tuple(zip(*[self.get_sentence(sid) for sid in ids]))
