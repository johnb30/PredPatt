ParseyPredFace
==============

This repo contains the resources required to build a REST API around
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

To run:

```
docker run -p 5000:5000 ppf
```

This will run a REST API listening on port `5000` on `localhost`.

Usage
-----

```
<<<<<<< HEAD
=======
import json
import requests #Assumes this is installed

>>>>>>> upstream/master
headers = {'Content-Type': 'application/json'}
data = {'text': "John brought the pizza to Loren."
}
data = json.dumps(data)
r = requests.get('http://localhost:5000/ppf/extract', data=data, headers=headers)

#This has the output dictionary
r.json()
```

The final output will look something like:

```
 u'predpatt': {u'arg_deps': {u'0': [[u'brought', 1, u'nsubj', u'John', 0]],
   u'3': [[u'pizza', 3, u'det', u'the', 2],
    [u'brought', 1, u'obj', u'pizza', 3],
    [u'Loren', 5, u'case', u'to', 4],
    [u'pizza', 3, u'nmod', u'Loren', 5]]},
  u'predicate_deps': [[None, None, u'root', u'brought', 1]]}}
```

As shown above, the keys in the output dictionary are:

* `conll`: The CoNLL-U formatted parse returned by SyntaxNet
* `original`: The original text sent to the API
<<<<<<< HEAD
* `predpatt`: The PredPatt `pprint` output

Notes
-----

*Important:* Due to the use of a REST API, for now the returned data from
PredPatt is the formatted prettyprint string. Future iterations of the API will
hopefully return a data blob and/or a concrete object.
=======
* `predpatt`: A nested JSON object containing `predicate_deps` and `arg_deps`.
 The `predicate_deps` field contains the dependency fragments for the exracted
 predicates. The fragments are of the form `(governor_text, governor_position,
 relation, token_text, token_position)`. The `arg_deps` field is formatted as
 a dictionary with keys of integers representing the argument location, and
 values as the extracted argument fragments. The format is the same as with the
 `predicate_deps` field.
>>>>>>> upstream/master
