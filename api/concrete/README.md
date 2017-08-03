ParseyPredFace
==============

This repo contains the resources required to build an
[`concrete`](https://github.com/hltcoe/concrete) annotator around
PredPatt and Google's SyntaxNet/DRAGNN/ParseyMcParseface. The build
instructions for the SyntaxNet Docker image are currently (7.21.17) broken,
so this repo makes use of the pre-built image.

Building and Running
--------

To build the image:

```
docker build -t ppf .
```

Note that the above requires pulling the rather large `tensorflow/syntaxnet`
image, so will take a bit of time.

TODO

Usage
-----

TODO
