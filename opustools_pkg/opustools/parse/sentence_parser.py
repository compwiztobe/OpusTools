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
    def parsed_preserve(blocks):
        sentence = []
        for block in blocks:
            if block.name == 's':
                sid = block.attributes['id']
                if preprocess == 'raw':
                    sentence.append(block.data.strip())
                sentence = ' '.join(sentence)
                yield (sid, (sentence, block.attributes))
                sentence = []
            elif block.name == 'w' and preprocess != 'raw':
                data = block.data.strip()
                if preprocess == 'parsed':
                    data += get_annotations(block)
                sentence.append(data)
            elif block.name == 'time' and preserve:
                sentence.append(block.get_raw_tag())

    return parsed_preserve


class SentenceParser:

    def __init__(self, document, preprocessing=None, anno_attrs=['all_attrs'],
            delimiter='|', preserve=False):
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

        self.parse_blocks = parse_type(preprocessing, preserve, self.get_annotations)

        self.data_tag = 's' if preprocessing == 'raw' else 'w'

    # removed store functionality in favor of a sentence iterator, possibly filtered by id_set
    # possibly with post-processing for the different annotations etc. (although that should probably go outside)
    # one thing that could maybe go in here the raw flag, to parse out individual words, or return entire sentence xml unparsed
    def sentences(self, id_set=None):
        """Read document and store sentences in a dictionary."""
        bp = BlockParser(self.document, data_tag=self.data_tag)
        try:
            for sid, attrs in self.parse_blocks(bp.get_complete_blocks()):
                if not id_set or sid in id_set:
                    yield sid, attrs
        except BlockParserError as e:
            raise SentenceParserError(
                'Error while parsing sentence file {file}: {error}'.format(file=self.document.name, error=e.args[0]))

    def get_annotations(self, block):
        if 'all_attrs' in self.anno_attrs:
            return self.delimiter.join(block.attributes[a] for a in sorted(block.attributes))
        else:
            return self.delimiter.join(block.attributes[a] for a in self.anno_attrs if a in block.attributes)
