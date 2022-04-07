import sys
from rdflib import Graph, BNode, Literal, URIRef, Namespace

#sh:property [ sh:path ex:visitsLecture; sst:inControlledVocabulary ex:Lecture ; ] ; -> ISO vocabulary aus gaia-x (https://gitlab.com/gaia-x/gaia-x-community/gaia-x-self-descriptions/-/blob/master/implementation/ontology/ControlledVocabularies/Certifications.ttl)

    #sh:property [ sh:path ex:hasStudentID; sst:sum 1 ; ] ;
	#sh:property [ sh:path rdfs:type; sst:equivalentClass "ex:Human" ; ] ;

#command sst:classEquivalence must be present for both targetClass shapes

def addQueryNodes(shaclGraph, nodeShape, message, mapping):
    node = BNode()
    shaclGraph.add((nodeShape, URIRef('http://www.w3.org/ns/shacl#sparql'), node))
    shaclGraph.add((node, URIRef('http://www.w3.org/ns/shacl#message'), Literal(message)))
    shaclGraph.add((node, URIRef('http://www.w3.org/ns/shacl#select'), Literal(mapping)))

def constraint3Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?target ?input
           WHERE {
               ?nodeShape sh:targetClass ?target .
               ?nodeShape sst:equivalentClass ?input .
           }""")

    for row in constraints:
        tag = row.input.rstrip().lstrip()
        targetClass = row.target.n3(shaclGraph.namespace_manager)
        message = "Constraints of the constraint type class equivalence assert that two classes have the same instances."
        mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\t$this a %s .\nFILTER (!EXISTS { $this a %s } )\n\t\t\t} \n\t\t\t" % (targetClass, tag)
        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.equivalentClass, None))

def constraint7Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?target ?input
           WHERE {
               ?nodeShape sh:targetClass ?target .
               ?nodeShape sst:disjointClass ?input .
           }""")

    for row in constraints:
        tag = row.input.rstrip().lstrip()
        targetClass = row.target.n3(shaclGraph.namespace_manager)
        message = "The constraint type disjoint classes states that no individual can be at the same time an instance of both classes."
        mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\t$this a %s .\n\t\t\t\tFILTER (EXISTS { $this a %s } )\n\t\t\t} \n\t\t\t" % (targetClass, tag)
        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)


    shaclGraph.remove((None, sst.disjointClass, None))

def constraint32Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:inControlledVocabulary ?input .
           }""")

    for row in constraints:
        inputs = row.input.split(",")
        property = inputs[0].rstrip().lstrip()
        tag = inputs[1].rstrip().lstrip()
        message = "Constraints of this type guarantee that individuals of a given class are assigned to the class skos:Concept and are included in at least one of possibly multiple controlled vocabularies."
        mapping = "\n\t\t\tSELECT "+str("$this")+"\n\t\t\tWHERE {\n\t\t\t\t"+str("$this")+" %s ?object .\n\t\t\t\tFILTER (!EXISTS{?object a skos:Concept} || !EXISTS{?object skos:inScheme %s} )\n\t\t\t} \n\t\t\t" % (property, tag)
        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.inControlledVocabulary, None))

def constraint47Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:languageTagDefinition ?input .
           }""")

    for row in constraints:
        inputs = row.input.split(",")
        message = "Values of the data property \'language tag definition\' must contain literals with a defined language tag."
        if len(inputs) < 3:
            property = inputs[0].rstrip().lstrip()
            tag = inputs[1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tFILTER NOT EXISTS {\n\t\t\t\t\t$this %s ?value .\n\t\t\t\t\tFILTER (isLiteral(?value) && langMatches(lang(?value), \'%s\'))\n\t\t\t\t}\n\t\t\t}\n\t\t\t" % (property, tag)
        else:
            properties = []
            for i in range(len(inputs)-1):
                properties.append(inputs[i])
            targets="{ $this "+properties[0]+" ?value }"
            properties.pop(0)
            for property in properties:
                targets += " UNION { $this "+property+" ?value }"
            tag = inputs[-1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tFILTER NOT EXISTS {\n\t\t\t\t\t%s\n\t\t\t\t\tFILTER (isLiteral(?value) && langMatches(lang(?value), \'%s\'))\n\t\t\t\t}\n\t\t\t}\n\t\t\t" % (targets, tag)

        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)


    shaclGraph.remove((None, sst.languageTagDefinition, None))

def constraint48aMapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:languageTagCardinalityEquals ?input .
           }""")

    for row in constraints:
        inputs = row.input.split(",")
        targetLen = len(inputs)
        message = "Values of the constraint \'language tag cardinality equals\' define exactly how many literals of the given language tag have to be defined."
        if targetLen < 4:
            property = inputs[0].rstrip().lstrip()
            tag = inputs[1].rstrip().lstrip()
            cardinality = inputs[2].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?value) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\t$this %s ?value .\n\t\t\t\t\tFILTER (isLiteral(?value) && langMatches(lang(?value), \'%s\'))\n\t\t\t\t}\n\t\t\t}\n\t\t\tGROUP BY $this\n\t\t\tHAVING (SUM(?count) != %s)\n\t\t\t" % (property, tag, cardinality)
        else:
            properties = []
            for i in range(targetLen-2):
                properties.append(inputs[i])
            targets="{ $this "+properties[0]+" ?value }"
            properties.pop(0)
            for property in properties:
                targets += " UNION { $this "+property+" ?value }"
            tag = inputs[targetLen-2].rstrip().lstrip()
            cardinality = inputs[-1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?value) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\t%s\n\t\t\t\t\tFILTER (isLiteral(?value) && langMatches(lang(?value), \'%s\'))\n\t\t\t\t}\n\t\t\t}\n\t\t\tGROUP BY $this\n\t\t\tHAVING (SUM(?count) != %s)\n\t\t\t" % (targets, tag, cardinality)

        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.languageTagCardinalityEquals, None))

def constraint48bMapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:languageTagCardinalityMin ?input .
           }""")

    for row in constraints:
        inputs = row.input.split(",")
        targetLen = len(inputs)
        message = "Values of the constraint \'language tag cardinality min\' define how many literals of the given language tag have to be defined at least."
        if targetLen < 4:
            property = inputs[0].rstrip().lstrip()
            tag = inputs[1].rstrip().lstrip()
            cardinality = inputs[2].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?value) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\t$this %s ?value .\n\t\t\t\t\tFILTER (isLiteral(?value) && langMatches(lang(?value), \'%s\'))\n\t\t\t\t}\n\t\t\t}\n\t\t\tGROUP BY $this\n\t\t\tHAVING (SUM(?count) < %s)\n\t\t\t" % (property, tag, cardinality)
        else:
            properties = []
            for i in range(targetLen-2):
                properties.append(inputs[i])
            targets="{ $this "+properties[0]+" ?value }"
            properties.pop(0)
            for property in properties:
                targets += " UNION { $this "+property+" ?value }"
            tag = inputs[targetLen-2].rstrip().lstrip()
            cardinality = inputs[-1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?value) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\t%s\n\t\t\t\t\tFILTER (isLiteral(?value) && langMatches(lang(?value), \'%s\'))\n\t\t\t\t}\n\t\t\t}\n\t\t\tGROUP BY $this\n\t\t\tHAVING (SUM(?count) < %s)\n\t\t\t" % (targets, tag, cardinality)

        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.languageTagCardinalityMin, None))

def constraint48cMapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:languageTagCardinalityMax ?input .
           }""")

    for row in constraints:
        inputs = row.input.split(",")
        targetLen = len(inputs)
        message = "Values of the constraint \'language tag cardinality min\' define how many literals of the given language tag are allowed to be defined at most."
        if targetLen < 4:
            property = inputs[0].rstrip().lstrip()
            tag = inputs[1].rstrip().lstrip()
            cardinality = inputs[2].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?value) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\t$this %s ?value .\n\t\t\t\t\tFILTER (isLiteral(?value) && langMatches(lang(?value), \'%s\'))\n\t\t\t\t}\n\t\t\t}\n\t\t\tGROUP BY $this\n\t\t\tHAVING (SUM(?count) > %s)\n\t\t\t" % (property, tag, cardinality)
        else:
            properties = []
            for i in range(targetLen-2):
                properties.append(inputs[i])
            targets="{ $this "+properties[0]+" ?value }"
            properties.pop(0)
            for property in properties:
                targets += " UNION { $this "+property+" ?value }"
            tag = inputs[targetLen-2].rstrip().lstrip()
            cardinality = inputs[-1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?value) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\t%s\n\t\t\t\t\tFILTER (isLiteral(?value) && langMatches(lang(?value), \'%s\'))\n\t\t\t\t}\n\t\t\t}\n\t\t\tGROUP BY $this\n\t\t\tHAVING (SUM(?count) > %s)\n\t\t\t" % (targets, tag, cardinality)

        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.languageTagCardinalityMax, None))


def constraint57Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:functionalProperty ?input .
           }""")

    for row in constraints:
        tag = row.input.rstrip().lstrip()
        message = "Objects of the data property \'functional property\' must be distinct."
        mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?sub) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\t$this %s ?obj .\n\t\t\t\t\t?sub %s ?obj .\n\t\t\t\t}\n\t\t\t}\n\t\t\tGROUP BY $this\n\t\t\tHAVING (SUM(?count)>1)\n\n\t\t\t" % (tag, tag)
        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.functionalProperty, None))

def constraint58Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:inverseFunctionalProperty ?input .
           }""")

    for row in constraints:
        tag = row.input.rstrip().lstrip()
        message = "Subjects of the data property \'inverse functional property\' must be distinct."
        mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?sub) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\t$this %s ?obj .\n\t\t\t\t\t?sub %s ?x .\n\t\t\t\t}\n\t\t\t}\n\t\t\tGROUP BY $this\n\t\t\tHAVING (SUM(?count)>1)\n\n\t\t\t" % (tag, tag)
        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.inverseFunctionalProperty, None))

def constraint61Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:symmetricObjectProperty ?input .
           }""")

    for row in constraints:
        tag = row.input.rstrip().lstrip()
        message = "A property is symmetric if it is equivalent to its own inverse."
        mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\t$this %s ?a .\n\t\t\t\tFILTER (!EXISTS { ?a %s $this } )\n\t\t\t} \n\t\t\t" % (tag, tag)
        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.symmetricObjectProperty, None))

def constraint62Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:aSymmetricObjectProperty ?input .
           }""")

    for row in constraints:
        tag = row.input.rstrip().lstrip()
        message = "A property is asymmetric if it is disjoint from its own inverse."
        mapping = "\n\t\t\tSELECT "+str("$this")+"\n\t\t\tWHERE {\n\t\t\t\t$this %s ?a .\n\t\t\t\tFILTER (EXISTS { ?a %s $this } )\n\t\t\t} \n\t\t\t" % (tag, tag)
        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.aSymmetricObjectProperty, None))

def constraint63Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:transitiveObjectProperty ?input .
           }""")

    for row in constraints:
        tag = row.input.rstrip().lstrip()
        message = "A constraint of the constraint type transitive object properties states that the object property p is transitive."
        mapping = "\n\t\t\tSELECT "+str("$this")+"\n\t\t\tWHERE {\n\t\t\t\t$this %s ?a .\n\t\t\t\t?a %s ?b .\n\t\t\t\tFILTER (!EXISTS { $this %s ?b } )\n\t\t\t} \n\t\t\t" % (tag,tag,tag)
        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.transitiveObjectProperty, None))

def constraint89Mapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:selfRestriction ?input .
           }""")

    for row in constraints:
        tag = row.input.rstrip().lstrip()
        message = "A constraint of the constraint type self restriction consists of an object property p, and it makes sure that all individuals are connected by p to themselves."
        mapping = "\n\t\t\tSELECT "+str("$this")+"\n\t\t\tWHERE {\n\t\t\t\tFILTER (!EXISTS { $this %s $this } )\n\t\t\t} \n\t\t\t" % tag
        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.selfRestriction, None))

def constraint233aMapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:sumEquals ?input .
           }""")

    for row in constraints:
        inputs = row.input.split(",")
        targetLen = len(inputs)
        message = "Values of the constraint \'sum\' define exactly how many occurances of a given property have to exist for each data instance."
        if targetLen < 3:
            property = inputs[0].rstrip().lstrip()
            tag = inputs[1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?subject) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\tSELECT DISTINCT ?subject\n\t\t\t\t\tWHERE {\n\t\t\t\t\t\t?subject %s ?object .\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t\tHAVING (SUM(?count) != %s)\n\n\t\t\t" % (property, tag)
        else:
            properties = []
            for i in range(len(inputs) - 1):
                properties.append(inputs[i])
            targets = "{ ?subject " + properties[0] + " ?object }"
            properties.pop(0)
            for property in properties:
                targets += " UNION { ?subject " + property + " ?object }"
            tag = inputs[-1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?subject) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\tSELECT DISTINCT ?subject\n\t\t\t\t\tWHERE {\n\t\t\t\t\t\t%s\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t\tHAVING (SUM(?count) != %s)\n\n\t\t\t" % (
            targets, tag)

        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.sumEquals, None))

def constraint233bMapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:sumMin ?input .
           }""")

    for row in constraints:
        inputs = row.input.split(",")
        targetLen = len(inputs)
        message = "Values of the constraint \'sum\' define exactly how many occurances of a given property have to exist for each data instance."
        if targetLen < 3:
            property = inputs[0].rstrip().lstrip()
            tag = inputs[1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?subject) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\tSELECT DISTINCT ?subject\n\t\t\t\t\tWHERE {\n\t\t\t\t\t\t?subject %s ?object .\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t\tHAVING (SUM(?count) < %s)\n\n\t\t\t" % (property, tag)
        else:
            properties = []
            for i in range(len(inputs) - 1):
                properties.append(inputs[i])
            targets = "{ ?subject " + properties[0] + " ?object }"
            properties.pop(0)
            for property in properties:
                targets += " UNION { ?subject " + property + " ?object }"
            tag = inputs[-1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?subject) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\tSELECT DISTINCT ?subject\n\t\t\t\t\tWHERE {\n\t\t\t\t\t\t%s\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t\tHAVING (SUM(?count) < %s)\n\n\t\t\t" % (
            targets, tag)

        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.sumMin, None))

def constraint233cMapping(shaclGraph):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:sumMax ?input .
           }""")

    for row in constraints:
        inputs = row.input.split(",")
        targetLen = len(inputs)
        message = "Values of the constraint \'sum\' define exactly how many occurances of a given property have to exist for each data instance."
        if targetLen < 3:
            property = inputs[0].rstrip().lstrip()
            tag = inputs[1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?subject) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\tSELECT DISTINCT ?subject\n\t\t\t\t\tWHERE {\n\t\t\t\t\t\t?subject %s ?object .\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t\tHAVING (SUM(?count) > %s)\n\n\t\t\t" % (property, tag)
        else:
            properties = []
            for i in range(len(inputs) - 1):
                properties.append(inputs[i])
            targets = "{ ?subject " + properties[0] + " ?object }"
            properties.pop(0)
            for property in properties:
                targets += " UNION { ?subject " + property + " ?object }"
            tag = inputs[-1].rstrip().lstrip()
            mapping = "\n\t\t\tSELECT $this\n\t\t\tWHERE {\n\t\t\t\tSELECT (COUNT(?subject) as ?count)\n\t\t\t\tWHERE {\n\t\t\t\t\tSELECT DISTINCT ?subject\n\t\t\t\t\tWHERE {\n\t\t\t\t\t\t%s\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t\tHAVING (SUM(?count) > %s)\n\n\t\t\t" % (
            targets, tag)

        addQueryNodes(shaclGraph, row.nodeShape, message, mapping)

    shaclGraph.remove((None, sst.sumMax, None))


if __name__ == '__main__':

    shaclGraph = Graph()
    shaclGraph.parse(sys.argv[1], format="turtle")

    namespaces = dict(shaclGraph.namespace_manager.namespaces())

    sst = Namespace(namespaces["sst"])
    shaclGraph.bind('sst', sst)

    constraint3Mapping(shaclGraph)
    constraint7Mapping(shaclGraph)
    constraint32Mapping(shaclGraph)
    constraint47Mapping(shaclGraph)
    constraint48aMapping(shaclGraph)
    constraint48bMapping(shaclGraph)
    constraint48cMapping(shaclGraph)
    constraint57Mapping(shaclGraph)
    constraint58Mapping(shaclGraph)
    constraint61Mapping(shaclGraph)
    constraint62Mapping(shaclGraph)
    constraint63Mapping(shaclGraph)
    constraint89Mapping(shaclGraph)
    constraint233aMapping(shaclGraph)
    constraint233bMapping(shaclGraph)
    constraint233cMapping(shaclGraph)

    shaclGraph.serialize(destination=sys.argv[2], format="turtle")
