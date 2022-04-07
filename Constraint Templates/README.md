# Documentation
This documentation lists all supported commands supported by the SHACL-SPARQL Templates (sst) and short examples on how to use them. Note that a target class has to be defines in the SHACL file via the sh:targetClass command.

The mapping from the sst: commands to SHACL-SPARQL is done via the Mapping.py script. It takes parameters as input

1. Path to the SHACL file containing sst: commands
2. Output path were the SHACL file containing the SHACL-SPARQL mappings is stored

Command line: python .\Mapping.py /path/to/shaclGraph.ttl path/to/output.ttl

###sst:equivalentClass
Constraints of the constraint type class equivalence assert that two classes have the same instances.

Example:
TODO

###sst:disjointClass
The constraint type disjoint classes states that no individual can be at the same time an instance of both classes.
The sst:disjointClass command takes a string containing the name of the class disjointed from the target class as input. The sh:path of the property is rdfs:type.

Example:

sh:property
        [ sst:disjointClass "gax-resource:Resource" ;
            sh:path rdfs:type ]
            


###sst:predicatePatternMatching
Constraints of this type enable to check if IRIs of individuals of a given class correspond to a specific pattern.

Example:
TODO

###sst:inControlledVocabulary
Constraints of this type guarantee that individuals of a given class are assigned to the class skos:Concept and are included in at least one of possibly multiple controlled vocabularies.

Example:
TODO

###sst:languageTagDefinition
Values of the data property \'language tag\' must contain literals with a defined language tag.
The sst:languageTagDefinition command takes a string containing the language tag that must be present as input. The sh:path of the property is the desired property that should include a literal of the desired language.
Example:

sh:property
        [ sst:languageTagDefinition "en" ;
            sh:path rdfs:label ]

###sst:languageTagCardinality
Values of the data property \'language tag cardinality\' define the number of times a certain language tag is allowed to occur on a given property.
The sst:languageTagCardinality command takes a string containing the language tag and the cardinality as input. They have to be separated by a whitespace. The sh:path of the property is the desired property that should include exactly the defined number of literals in the desired language.
Example:

sh:property
        [ sst:languageTagCardinality "en 1" ;
            sh:path rdfs:label ]

###sst:functionalProperty
Objects of the data property \'functional property\' must be distinct.
The sst:functionalProperty command takes the targeted property as input. The sh:path is in this case identical to the input for the sst:functionalProperty command.
Example:

sh:property
        [ sst:functionalProperty gax-participant:hasLegallyBindingName ;
            sh:path gax-participant:hasLegallyBindingName ]

###sst:inverseFunctionalProperty
Subjects of the data property \'inverse functional property\' must be distinct.
The sst:inverseFunctionalProperty command takes the targeted property as input. The sh:path is in this case identical to the input for the sst:inverseFunctionalProperty command.

Example:

sh:property
        [ sst:inverseFunctionalProperty gax-participant:hasSalesTaxID ;
            sh:path gax-participant:hasSalesTaxID ]

###sst:symmetricObjectProperty
A property is symmetric if it is equivalent to its own inverse.
The sst:symmetricObjectProperty command takes the targeted property as input. The sh:path is in this case identical to the input for the sst:symmetricObjectProperty command.

Example:
sh:property
        [ sst:symmetricObjectProperty ex:hasProjectPartner ;
            sh:path ex:hasProjectPartner ]

###sst:aSymmetricObjectProperty
A property is asymmetric if it is disjoint from its own inverse.
The sst:aSymmetricObjectProperty command takes the targeted property as input. The sh:path is in this case identical to the input for the sst:aSymmetricObjectProperty command.

Example:

sh:property
	    [ sst:aSymmetricObjectProperty ex:isSubsidiaryOf ;
            sh:path ex:isSubsidiaryOf ]

###sst:transitiveObjectProperty
A constraint of the constraint type transitive object properties states that the object property p is transitive.
The sst:transitiveObjectProperty command takes the targeted property as input. The sh:path is in this case identical to the input for the sst:transitiveObjectProperty command.

Example:

sh:property
        [ sst:transitiveObjectProperty ex:isSubsidiaryOf ;
            sh:path ex:isSubsidiaryOf ] 

###sst:selfRestriction
A constraint of the constraint type self restriction consists of an object property p, and it makes sure that all individuals are connected by p to themselves.
The sst:selfRestriction command takes the targeted property as input. The sh:path is in this case identical to the input for the sst:selfRestriction command.

Example:

sh:property
	    [ sst:selfRestriction ex:trusts ;
            sh:path ex:trusts ]
            
###sst:sum
This constraint requires aggregating multiple values of an object or data property context of a class using the SPARQL aggregation set functions Count and Sum.

Example:
TODO

###Example File


    sh:ProviderShape a sh:NodeShape ;
	    sh:property	  
	        [ sst:disjointClass "gax-resource:Resource" ;	        
                sh:path rdfs:type ],                
            [ sst:transitiveObjectProperty ex:isSubsidiaryOf ;
                sh:path ex:isSubsidiaryOf ],
            [ sst:languageTagCardinality "en 1" ;
                sh:path rdfs:label ],
            [ sst:symmetricObjectProperty ex:hasProjectPartner ;
                sh:path ex:hasProjectPartner ],
        sh:targetClass gax-participant:Provider .
    