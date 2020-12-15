import xml.parsers.expat
from ..util import file_open

class BlockParserError(Exception):

    def __init__(self, message):
        """Raise error when block parsing fails.

        Arguments:
        message -- Error message to be printed
        """
        self.message = message

class Block:

    def __init__(self, parent=None, name=None, data='', attributes=None):
        """Xml block instance held in memory by BlockParser"""
        self.parent = parent
        self.name = name
        self.data = data
        self.attributes = attributes

    def get_raw_tag(self):
        astrings = ['{k}="{v}"'.format(k=k, v=v)
                for k, v in self.attributes.items()]
        tag_content = ' '.join([self.name]+astrings)
        if self.data == '':
            return '<{tag_content} />'.format(
                    tag_content=tag_content, name=self.name)
        else:
            return '<{tag_content}>{data}</{name}>'.format(
                    tag_content=tag_content, data=self.data, name=self.name)

    def tag_in_parents(self, tag):
        """Check if given tag is in block's ancestors and return the matching block"""
        if self.name == tag:
            return block
        elif self.parent:
            return self.parent.tag_in_parents(tag)

    def __str__(self):
        parent_name = None
        if self.parent:
            parent_name = self.parent.name
        return ('name: {name}, data: {data}, attributes: {attributes}, '
            'parent: {parent}'.format(name=self.name, data=repr(self.data),
                attributes=self.attributes, parent=parent_name))

class BlockParser:

    def __init__(self, document, data_tag=None):
        """Parse an xml document line by line removing each element
        from memory as soon as its end tag is found.

        Positional arguments:
        document -- Xml document to be parsed
        data_tag -- Tag for which char data is updated
        """

        self.document = document
        self.data_tag = data_tag
        self.current_block = Block(name='root')
        self.completeBlocks = []

        def start_element(name, attrs):
            """Update current block"""
            sub_block = Block(parent=self.current_block, name=name, attributes=attrs)
            self.current_block = sub_block

        def end_element(name):
            """Update complete blocks, and move up one level on block tree"""
            self.completeBlocks.append(self.current_block)
            self.current_block = self.current_block.parent

        def char_data(data):
            """Update current block's character data"""
            if self.current_block.name == self.data_tag:
                self.current_block.data += data

        self.p = xml.parsers.expat.ParserCreate()

        self.p.StartElementHandler = start_element
        self.p.EndElementHandler = end_element
        if data_tag:
            self.p.CharacterDataHandler = char_data

    def parse_line(self, line):
        try:
            self.p.Parse(line)
        except xml.parsers.expat.ExpatError as e:
            raise BlockParserError(
                "Document '{document}' could not be parsed: "
                "{error}".format(document=self.document.name, error=e.args[0]))

    # is this really necessary?
    # if the underlying document object is something that needs closing
    # then the code calling this BlockParser (or SentenceParser)
    # should already be handling that (with a with block for example)
    def close_document(self):
        self.document.close()

    def get_complete_blocks(self):
        """
        Read lines until one or more end tags are found on a single line,
        and return the block trees corresponding to those end tags.
        """
        for line in self.document:
            self.parse_line(line)
            if len(self.completeBlocks) > 0:
                yield from self.completeBlocks
                self.completeBlocks = []
