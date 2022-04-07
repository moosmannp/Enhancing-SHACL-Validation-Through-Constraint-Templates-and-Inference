import numpy as np
from rdflib import RDF, BNode, Literal, URIRef, Namespace, Graph, collection
import networkx as nx


def getAbbreviations(ontologyGraph, shaclGraph):
    dictAbbr = {}

    properties = ontologyGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?a ?property ?b
           WHERE {
               ?a ?property ?b .
           }""")
    for row in properties:
        dictAbbr[row.property.n3(shaclGraph.namespace_manager)]=row.property.n3().replace('<','').replace('>','')
        dictAbbr[row.a.n3(shaclGraph.namespace_manager)]=row.a.n3().replace('<','').replace('>','')
        dictAbbr[row.b.n3(shaclGraph.namespace_manager)]=row.b.n3().replace('<','').replace('>','')

    return dictAbbr




def getParentRelations(graph, relationType):
    if relationType == "subclass":
        relations = graph.query(
            """PREFIX owl:<http://www.w3.org/2002/07/owl#>
               SELECT DISTINCT ?parent ?child
               WHERE {
                   ?child rdfs:subClassOf ?parent .
               }""")

    elif relationType == "subproperty":
        relations = graph.query(
            """PREFIX owl:<http://www.w3.org/2002/07/owl#>
               SELECT DISTINCT ?parent ?child
               WHERE {
                   ?child rdfs:subPropertyOf ?parent .
               }""")

    result_class = []
    for row in relations:
        result_class.append(
            (row.parent.n3().replace('<', '').replace('>', ''), row.child.n3().replace('<', '').replace('>', '')))
    result_class_Array = np.asarray(result_class)
    return result_class_Array


def getParentRelationsGraph(parentRelations):
    nodes = []
    nodeValues = {}
    G = nx.DiGraph()
    for relation in parentRelations:
        for node in relation:
            if not (nodes.__contains__(node)):
                nodes.append(node)

    c = 1
    for node in nodes:
        G.add_node(c, name=node)
        nodeValues[node] = c
        c = c + 1

    for relation in parentRelations:
        G.add_edge(nodeValues.get(relation[0]), nodeValues.get(relation[1]))

    return G, nodeValues


def getSuccessors(G, nodeValues, root):
    successors = nx.nodes(nx.dfs_tree(G, nodeValues.get(root)))

    successorsNames = []

    for entry in successors:
        for key, value in nodeValues.items():
            if entry == value:
                successorsNames.append(key)
    return successorsNames


def subClassInference(shaclGraph, G, nodeValues):
    sh = Namespace('http://www.w3.org/ns/shacl#')
    shaclGraph.bind('sh', sh)

    # Subclass Inference for sh:targetClass
    targetClasses = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?shape ?target
           WHERE {
               ?shape sh:targetClass ?target .
           }""")

    for row in targetClasses:
        if (nodeValues.keys().__contains__(row.target.n3().replace("<", "").replace(">", ""))):
            successors = getSuccessors(G, nodeValues, row.target)
            for successor in successors:
                shaclGraph.add((row.shape, sh.targetClass, URIRef(successor)))

    # Subclass Inference for sh:class
    shClasses = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?propertyNode ?propertyClass
           WHERE {
               ?propertyNode sh:class ?propertyClass .
           }""")

    for row in shClasses:
        if (nodeValues.keys().__contains__(row.propertyClass.n3().replace("<", "").replace(">", ""))):
            shaclGraph.remove(
                (row.propertyNode, URIRef('http://www.w3.org/ns/shacl#class'), row.propertyClass.n3()))
            successors = getSuccessors(G, nodeValues, row.propertyClass)
            successorsNumber = len(successors)
            blankNodes = []
            for i in range(successorsNumber * 2):
                blankNodes.append(BNode())
            shaclGraph.add((row.propertyNode, URIRef('http://www.w3.org/ns/shacl#or'), blankNodes[0]))
            count = 0
            for i in range(successorsNumber):
                if i != successorsNumber - 1:
                    shaclGraph.add((blankNodes[count], RDF.first, blankNodes[count + 1]))
                    shaclGraph.add((blankNodes[count + 1], URIRef('http://www.w3.org/ns/shacl#class'),
                                    URIRef(successors[i])))
                    shaclGraph.add((blankNodes[count], RDF.rest, blankNodes[count + 2]))
                else:
                    shaclGraph.add((blankNodes[count], RDF.first, blankNodes[count + 1]))
                    shaclGraph.add((blankNodes[count + 1], URIRef('http://www.w3.org/ns/shacl#class'),
                                    URIRef(successors[i])))
                    shaclGraph.add((blankNodes[count], RDF.rest, RDF.nil))
                count += 2


def subPropertyInference(shaclGraph, G, nodeValues):
    sh = Namespace('http://www.w3.org/ns/shacl#')
    shaclGraph.bind('sh', sh)

    # Subproperty Inference for sh:path
    paths = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?propertyNode ?property
           WHERE {
               ?propertyNode sh:path ?property .
           }""")

    for row in paths:
        if (nodeValues.keys().__contains__(row.property.n3().replace("<", "").replace(">", ""))):
            successors = getSuccessors(G, nodeValues, row.property)
            successorsNumber = len(successors)
            shaclGraph.remove((row.propertyNode, sh.path, row.property))
            blankNodes = []
            for i in range(successorsNumber + 1):
                blankNodes.append(BNode())
            shaclGraph.add((row.propertyNode, sh.path, blankNodes[0]))
            shaclGraph.add((blankNodes[0], sh.alternativePath, blankNodes[1]))
            for i in range(successorsNumber):
                if i != successorsNumber - 1:
                    shaclGraph.add((blankNodes[i + 1], RDF.first, URIRef(successors[i])))
                    shaclGraph.add((blankNodes[i + 1], RDF.rest, blankNodes[i + 2]))
                else:
                    shaclGraph.add((blankNodes[i + 1], RDF.first, URIRef(successors[i])))
                    shaclGraph.add((blankNodes[i + 1], RDF.rest, RDF.nil))

    # Subproperty Inference for sh:alternativePath
    altPaths = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?propertyNode ?blankNode
           WHERE {
               ?propertyNode sh:alternativePath ?blankNode .
           }""")

    for row in altPaths:
        c = collection.Collection(shaclGraph, row.blankNode)
        for term in c:
            if (nodeValues.keys().__contains__(term.n3().replace("<", "").replace(">", ""))):
                successors = getSuccessors(G, nodeValues, term)
                if len(successors)>1:
                    for successor in successors:
                        if not URIRef(successor) in c:
                            c.append(URIRef(successor))

    # Subproperty Inference for sh:targetSubjectsOf
    targetSubjects = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?shapeNode ?property
           WHERE {
               ?propertyNode sh:targetSubjectsOf ?blankNode .
           }""")

    for row in targetSubjects:
        if (nodeValues.keys().__contains__(row.property.n3().replace("<", "").replace(">", ""))):
            successors = getSuccessors(G, nodeValues, row.property)
            for successor in successors:
                shaclGraph.add(row.shapeNode, sh.targetSubjectsOf, row.property)


    # Subproperty Inference for sh:targetObjectsOf
    targetObjects = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?shapeNode ?property
           WHERE {
               ?propertyNode sh:targetObjectsOf ?blankNode .
           }""")

    for row in targetObjects:
        if (nodeValues.keys().__contains__(row.property.n3().replace("<", "").replace(">", ""))):
            successors = getSuccessors(G, nodeValues, row.property)
            for successor in successors:
                shaclGraph.add(row.shapeNode, sh.targetObjectsOf, row.property)

def sstSubClassInference(shaclGraph, G, nodeValues, sst, abbreviations):
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:equivalentClass ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        if str(row.input) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[row.input])
            successorsList = []
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                shaclGraph.add((row.nodeShape, URIRef(sst+"equivalentClass"), Literal(successor)))

    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:disjointClass ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        if str(row.input) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[row.input])
            successorsList = []
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                shaclGraph.add((row.nodeShape, URIRef(sst + "disjointClass"), Literal(successor)))

def sstSubPropertyInference(shaclGraph, G, nodeValues, sst, abbreviations):

    # Symmetric Object Property
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:symmetricObjectProperty ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        if str(row.input) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[row.input])
            successorsList = []
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                shaclGraph.add((row.nodeShape, URIRef(sst+"symmetricObjectProperty"), Literal(successor)))

    # Asymmetric Object Property
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:aSymmetricObjectProperty ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        if str(row.input) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[row.input])
            successorsList = []
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                shaclGraph.add((row.nodeShape, URIRef(sst+"aSymmetricObjectProperty"), Literal(successor)))

    # Transitive Object Property
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:transitiveObjectProperty ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        if str(row.input) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[row.input])
            successorsList = []
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                shaclGraph.add((row.nodeShape, URIRef(sst+"transitiveObjectProperty"), Literal(successor)))

    # Functional Property
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:functionalProperty ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        if str(row.input) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[row.input])
            successorsList = []
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                shaclGraph.add((row.nodeShape, URIRef(sst+"functionalProperty"), Literal(successor)))

    # Inverse Functional Property
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:inverseFunctionalProperty ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        if str(row.input) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[row.input])
            successorsList = []
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                shaclGraph.add((row.nodeShape, URIRef(sst+"inverseFunctionalProperty"), Literal(successor)))

    # Self Restriction
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:selfRestriction ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        if str(row.input) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[row.input])
            successorsList = []
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                shaclGraph.add(
                    (row.nodeShape, URIRef(sst + "selfRestriction"), Literal(successor)))

    # In Controlled Vocabulary
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:inControlledVocabulary ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        input = row.input.replace('"', '').replace(' ', '').split(",")
        if str(input[0]) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[input[0]])
            successorsList = []
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                shaclGraph.add(
                    (row.nodeShape, URIRef(sst + "inControlledVocabulary"), Literal(successor+", "+input[-1])))

    # Language Tag Definition
    constraints = shaclGraph.query(
        """PREFIX owl:<http://www.w3.org/2002/07/owl#>
           SELECT DISTINCT ?nodeShape ?input
           WHERE {
               ?nodeShape sst:languageTagDefinition ?input .
           }""")

    for row in constraints:
        nodeValuesList = []
        for value in nodeValues:
            nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
        input = row.input.replace('"','').replace(' ','').split(",")
        if str(input[0]) in nodeValuesList:
            successors = getSuccessors(G, nodeValues, abbreviations[input[0]])
            successorsList = []
            newTarget = ""
            for value in successors:
                successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            for successor in successorsList:
                newTarget += successor+", "
            newTarget += input[-1]
            shaclGraph.remove((row.nodeShape, URIRef(sst + "languageTagDefinition"), row.input))
            shaclGraph.add((row.nodeShape, URIRef(sst + "languageTagDefinition"), Literal(newTarget)))

        # Language Tag Cardinality Equals
        constraints = shaclGraph.query(
            """PREFIX owl:<http://www.w3.org/2002/07/owl#>
               SELECT DISTINCT ?nodeShape ?input
               WHERE {
                   ?nodeShape sst:languageTagCardinalityEquals ?input .
               }""")

        for row in constraints:
            nodeValuesList = []
            for value in nodeValues:
                nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            input = row.input.n3(shaclGraph.namespace_manager).replace('"', '').replace(' ', '').split(",")
            if str(input[0]) in nodeValuesList:
                successors = getSuccessors(G, nodeValues, abbreviations[input[0]])
                successorsList = []
                newTarget = ""
                for value in successors:
                    successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
                for successor in successorsList:
                    newTarget += successor + ", "
                newTarget += input[-2] + ", "+input[-1]
                shaclGraph.remove((row.nodeShape, URIRef(sst + "languageTagCardinalityEquals"), row.input))
                shaclGraph.add((row.nodeShape, URIRef(sst + "languageTagCardinalityEquals"), Literal(newTarget)))

        # Language Tag Cardinality Min
        constraints = shaclGraph.query(
            """PREFIX owl:<http://www.w3.org/2002/07/owl#>
               SELECT DISTINCT ?nodeShape ?input
               WHERE {
                   ?nodeShape sst:languageTagCardinalityMin ?input .
               }""")

        for row in constraints:
            nodeValuesList = []
            for value in nodeValues:
                nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            input = row.input.n3(shaclGraph.namespace_manager).replace('"', '').replace(' ', '').split(",")
            if str(input[0]) in nodeValuesList:
                successors = getSuccessors(G, nodeValues, abbreviations[input[0]])
                successorsList = []
                newTarget = ""
                for value in successors:
                    successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
                for successor in successorsList:
                    newTarget += successor + ", "
                newTarget += input[1] + ", " + input[2]
                shaclGraph.remove(
                    (row.nodeShape, URIRef(sst + "languageTagCardinalityMin"), row.input))
                shaclGraph.add((row.nodeShape, URIRef(sst + "languageTagCardinalityMin"),
                                Literal(newTarget)))

        # Language Tag Cardinality Min
        constraints = shaclGraph.query(
            """PREFIX owl:<http://www.w3.org/2002/07/owl#>
               SELECT DISTINCT ?nodeShape ?input
               WHERE {
                   ?nodeShape sst:languageTagCardinalityMax ?input .
               }""")
        for row in constraints:
            nodeValuesList = []
            for value in nodeValues:
                nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            input = row.input.n3(shaclGraph.namespace_manager).replace('"', '').replace(' ', '').split(",")
            if str(input[0]) in nodeValuesList:
                successors = getSuccessors(G, nodeValues, abbreviations[input[0]])
                successorsList = []
                newTarget = ""
                for value in successors:
                    successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
                for successor in successorsList:
                    newTarget += successor + ", "
                newTarget += input[1] + ", " + input[2]
                shaclGraph.remove(
                    (row.nodeShape, URIRef(sst + "languageTagCardinalityMax"), row.input))
                shaclGraph.add((row.nodeShape, URIRef(sst + "languageTagCardinalityMax"),
                                Literal(newTarget)))

        # Sum Equals
        constraints = shaclGraph.query(
            """PREFIX owl:<http://www.w3.org/2002/07/owl#>
               SELECT DISTINCT ?nodeShape ?input
               WHERE {
                   ?nodeShape sst:sumEquals ?input .
               }""")

        for row in constraints:
            nodeValuesList = []
            for value in nodeValues:
                nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            input = row.input.n3(shaclGraph.namespace_manager).replace('"', '').replace(' ', '').split(",")
            if str(input[0]) in nodeValuesList:
                successors = getSuccessors(G, nodeValues, abbreviations[input[0]])
                successorsList = []
                newTarget = ""
                for value in successors:
                    successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
                for successor in successorsList:
                    newTarget += successor + ", "
                newTarget += input[-2] + ", "+input[-1]
                shaclGraph.remove((row.nodeShape, URIRef(sst + "sumEquals"), row.input))
                shaclGraph.add((row.nodeShape, URIRef(sst + "sumEquals"), Literal(newTarget)))

        # Sum Min
        constraints = shaclGraph.query(
            """PREFIX owl:<http://www.w3.org/2002/07/owl#>
               SELECT DISTINCT ?nodeShape ?input
               WHERE {
                   ?nodeShape sst:sumMin ?input .
               }""")

        for row in constraints:
            nodeValuesList = []
            for value in nodeValues:
                nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            input = row.input.n3(shaclGraph.namespace_manager).replace('"', '').replace(' ', '').split(",")
            if str(input[0]) in nodeValuesList:
                successors = getSuccessors(G, nodeValues, abbreviations[input[0]])
                successorsList = []
                newTarget = ""
                for value in successors:
                    successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
                for successor in successorsList:
                    newTarget += successor + ", "
                newTarget += input[-2] + ", "+input[-1]
                shaclGraph.remove((row.nodeShape, URIRef(sst + "sumMin"), row.input))
                shaclGraph.add((row.nodeShape, URIRef(sst + "sumMin"), Literal(newTarget)))

        # Sum Max
        constraints = shaclGraph.query(
            """PREFIX owl:<http://www.w3.org/2002/07/owl#>
               SELECT DISTINCT ?nodeShape ?input
               WHERE {
                   ?nodeShape sst:sumMax ?input .
               }""")

        for row in constraints:
            nodeValuesList = []
            for value in nodeValues:
                nodeValuesList.append(URIRef(value).n3(shaclGraph.namespace_manager))
            input = row.input.n3(shaclGraph.namespace_manager).replace('"', '').replace(' ', '').split(",")
            if str(input[0]) in nodeValuesList:
                successors = getSuccessors(G, nodeValues, abbreviations[input[0]])
                successorsList = []
                newTarget = ""
                for value in successors:
                    successorsList.append(URIRef(value).n3(shaclGraph.namespace_manager))
                for successor in successorsList:
                    newTarget += successor + ", "
                newTarget += input[-2] + ", "+input[-1]
                shaclGraph.remove((row.nodeShape, URIRef(sst + "sumMax"), row.input))
                shaclGraph.add((row.nodeShape, URIRef(sst + "sumMax"), Literal(newTarget)))


if __name__ == '__main__':
    ontologyFile = 'ExampleOntology.ttl'
    shaclFile = 'runningExampleMapped.ttl'
    output = 'newShacl.ttl'

    shaclGraph = Graph()
    shaclGraph.parse(shaclFile, format="turtle")

    graphOntology = Graph().parse(ontologyFile, format='turtle')
    subClasses = getParentRelations(graphOntology, "subclass")
    subProperties = getParentRelations(graphOntology, "subproperty")

    subClassGraph, subClassValues = getParentRelationsGraph(subClasses)
    subPropertyGraph, subPropertyValues = getParentRelationsGraph(subProperties)

    subClassInference(shaclGraph, subClassGraph, subClassValues)
    subPropertyInference(shaclGraph, subPropertyGraph, subPropertyValues)

    namespaces = dict(shaclGraph.namespace_manager.namespaces())
    sstNamespace = namespaces["sst"]
    if namespaces.keys().__contains__("sst"):
        abbreviations = getAbbreviations(graphOntology, shaclGraph)
        sstSubClassInference(shaclGraph, subClassGraph, subClassValues, sstNamespace, abbreviations)
        sstSubPropertyInference(shaclGraph, subPropertyGraph, subPropertyValues, sstNamespace, abbreviations)



    shaclGraph.serialize(destination=output, format="ttl")