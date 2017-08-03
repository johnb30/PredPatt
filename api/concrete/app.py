from concrete import Communication, AnnotationMetadata, Tokenization, TokenList, Token, TokenizationKind, TextSpan
from concrete.annotate import AnnotateCommunicationService
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory

from thrift.transport import TSocket, TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TNonblockingServer

import ParseyPredFace


def pp_update_communication(sentence, output):
    timestamp = int(time.time())

    augf = AnalyticUUIDGeneratorFactory(communication)
    aug = augf.create()

    deps, toks, pos = conll_to_concrete(output['conll'])

    #Tokenization
    tokenization = Tokenization(kind=TokenizationKind.TOKEN_LIST,
                                metadata=AnnotationMetadata(tool='syntaxnet',
                                                            timestamp=timestamp),
                                tokenList=[Token(tokenIndex=i, text=token,
#Do we need this?                                             textSpan=TextSpan(start=start,
#                                                                   ending=ending)
                                                 )
                                           for ix, token in enumerate(tokens)],
                                uuid=next(aug))
    sentence.tokenization.tokenList = tokenization

    #POS
    pos = TokenTagging(uuid=aug.next(),
                       metadata=AnnotationMetadata(
                           tool='syntaxnet POS',
                           timestamp=timestamp,
                           kBest=1),
                       taggingType='POS',
                       taggedTokenList=[TaggedToken(tokenIndex=ix, tag=pos) for
                                        ix, pos in enumerate(pos, 0)])
    sentence.tokenization.tokenTaggingList.append(pos)

    #Dep relation
    dep_tok = Tokenization(kind=TokenizationKind.TOKEN_LIST,
                           metadata=AnnotationMetadata(tool='syntaxnet',
                                                       timestamp=timestamp),
                           dependencyParseList=deps,
                           uuid=next(aug))
    sentence.tokenization.dependencyParseList.append(dep_tok)

    #PP output
    #TODO: implement
    pp_concrete = predpatt_to_concrete(output['predpatt'])

    return sentence


def sn_update_communication(sentence, output):
    timestamp = int(time.time())

    augf = AnalyticUUIDGeneratorFactory(communication)
    aug = augf.create()

    deps, toks, pos = conll_to_concrete(output['conll'])

    #Tokenization
    tokenization = Tokenization(kind=TokenizationKind.TOKEN_LIST,
                                metadata=AnnotationMetadata(tool='syntaxnet',
                                                            timestamp=timestamp),
                                tokenList=[Token(tokenIndex=i, text=token,
#Do we need this?                                             textSpan=TextSpan(start=start,
#                                                                   ending=ending)
                                                 )
                                           for ix, token in enumerate(tokens)],
                                uuid=next(aug))
    sentence.tokenization.tokenList = tokenization

    #POS
    pos = TokenTagging(uuid=aug.next(),
                       metadata=AnnotationMetadata(
                           tool='syntaxnet POS',
                           timestamp=timestamp,
                           kBest=1),
                       taggingType='POS',
                       taggedTokenList=[TaggedToken(tokenIndex=ix, tag=pos) for
                                        ix, pos in enumerate(pos, 0)])
    sentence.tokenization.tokenTaggingList.append(pos)

    #Dep relation
    dep_tok = Tokenization(kind=TokenizationKind.TOKEN_LIST,
                           metadata=AnnotationMetadata(tool='syntaxnet',
                                                       timestamp=timestamp),
                           dependencyParseList=deps,
                           uuid=next(aug))
    sentence.tokenization.dependencyParseList.append(dep_tok)

    return sentence


def conll_to_concrete(conll_tag):
    lines = []
    split = [line for line in conll_tag.split('\n') if line]
    for line in split:
        line = line.split('\t')  # data appears to use '\t'
        if '-' in line[0]:       # skip multi-tokens, e.g., on Spanish UD bank
            continue
        assert len(line) == 10, line
        lines.append(line)
    [_, tokens, _, tags, _, _, gov, gov_rel, _, _] = list(zip(*lines))
    triples = [Dependency(int(gov) - 1, dep, rel) for dep, (rel, gov) in
               enumerate(zip(gov_rel, gov))]

    return triples, tokens, tags


def predpatt_to_concrete(pp):
    print 'placeholder'


def get_ud_fragments(pp):
    predicates = []
    for predicate in pp.instances:
        # Get dep parses for the predicate.
        pred_deps = []
        for token in predicate.tokens:
            # (head, relation, dependent)
            dep = Dependency(token.gov.position, token.position, token.gov_rel)
            pred_deps.append(dep)

        # Get dep parses for the arguments.
        arg2deps = {}
        for argument in predicate.arguments:
            arg_deps = []
            for token in argument.tokens:
                dep = Dependency(token.gov.position, token.position,
                                 token.gov_rel)
                arg_deps.append(dep)
            arg2deps[argument.position] = arg_deps
        predicates.append((pred_deps, arg2deps))
    return predicates


class PredPattHandler():
    def annotate(self, communication):
        for section in communication.sectionList:
            if section.kind != "paragraph":
                continue
            for ix, sent in enumerate(section.sentenceList):
                text = communication.text[sent.textSpan.start:sent.textSpan.ending]
                output = ParseyPredFace.parse(text)

                #TODO: how do we handle this? Rewrite the sentence list?
                #Replace an individual sent?
                new_sent = pp_pdate_communication(sent, output)
                section.sentenceList[ix] = new_sent

        return communication


class SyntaxnetHandler():
    def annotate(self, communication):
        for section in communication.sectionList:
            if section.kind != "paragraph":
                continue
            for ix, sent in enumerate(section.sentenceList):
                text = communication.text[sent.textSpan.start:sent.textSpan.ending]
                output = ParseyPredFace.parse(text)

                #TODO: how do we handle this? Rewrite the sentence list?
                #Replace an individual sent?
                new_sent = sn_update_communication(sent, output)
                section.sentenceList[ix] = new_sent

        return communication


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", dest="port", type=int, default=9090)
    parser.add_argument("-h", "--handler", dest="handler", type=string,
                        default='ppf', choices=['pp', 'sn'])
    options = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if options.handler == 'pp':
        handler = PredPattHandler()
    elif options.handler == 'sn':
        handler = SyntaxnetHandler()
    processor = AnnotateCommunicationService.Processor(handler)
    transport = TSocket.TServerSocket(port=options.port)
    ipfactory = TCompactProtocol.TCompactProtocolFactory()
    opfactory = TCompactProtocol.TCompactProtocolFactory()

    server = TNonblockingServer.TNonblockingServer(processor, transport,
                                                   ipfactory, opfactory)
    logging.info('Starting the server...')
    server.serve()
