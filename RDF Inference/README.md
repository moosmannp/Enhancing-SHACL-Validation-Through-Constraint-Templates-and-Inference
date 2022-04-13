# Documentation
This documentation gives an short example of how input and output of the ApplyInference.py tool look like, and how the tool is executed from the command line. 
ApplyInference.py takes three parameters as input

1. Path to the SHACL shape file
2. Path to the ontology file
3. Output path were the SHACL file containing the inferred information is stored

Command line execution:
    
    python .\ApplyInference.py /path/to/shaclGraph.ttl /path/to/ontologyGraph.ttl path/to/output.ttl

This tool supports transitive inference on the properties 'rdfs:subClassOf' and 'rdfs:subPropertyOf'. It considers the following connection types:

- Class-based Targets
- Subject-of Targets
- Objects-of Targets
- Predicate Paths
- Alternative Paths

    
###Example
####Input
    
#####Shape Graph
    ex:PersonShape
	a sh:NodeShape ;
	sh:targetClass ex:Person ;
	sh:property [
		sh:path ex:hasName ;
		sh:minCount 1 ;
	] .
	
#####Ontology Graph
    
    ex:Person
        a   owl:Class .
    
    ex:Student
        a   owl:Class ;
        rdfs:subClassOf ex:Person .

####Output
    ex:PersonShape
	a sh:NodeShape ;
	sh:targetClass ex:Person, ex:Student ;
	sh:property [
		sh:path ex:hasName ;
		sh:minCount 1 ;
	] .