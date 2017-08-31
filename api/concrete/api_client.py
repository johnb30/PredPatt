import time
import nltk
import argparse

from concrete.util import create_comm

from concrete.structure.ttypes import (
    Section,
    Sentence,
    Token,
    Tokenization,
    TokenizationKind,
    TokenList
)
from concrete.spans.ttypes import TextSpan
from concrete.util import CommunicationWriter
from concrete.communication.ttypes import Communication
from concrete.metadata.ttypes import AnnotationMetadata
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory
from concrete.annotate import AnnotateCommunicationService as Annotator

from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol


def create_base_comm(comm_id, text, toolname="article_generator"):
    sentences = '\n'.join(nltk.sent_tokenize(text))

    comm = create_comm(comm_id, sentences, metadata_tool=toolname)

    return comm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", dest="port", type=int, default=9090)
    parser.add_argument("-H", "--host", dest="host", default="localhost")
    options = parser.parse_args()

    transport = TSocket.TSocket(options.host, options.port)
    transport = TTransport.TFramedTransport(transport)
    # Buffering is critical. Raw sockets are very slow
    #transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TCompactProtocol.TCompactProtocol(transport)

    # Create a client to use the protocol encoder
    client = Annotator.Client(protocol)

    # Connect!
    transport.open()

    c = create_base_comm('abc123', 'Chris loves silly dogs and clever cats.')
    new_c = client.annotate(c)

    with CommunicationWriter('sample_comm.concrete') as writer:
        writer.write(comm)
