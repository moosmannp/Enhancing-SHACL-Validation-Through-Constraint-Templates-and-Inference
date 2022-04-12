# Documentation
This documentation lists all supported commands supported by the SHACL-SPARQL Templates (sst) and short examples on how to use them. Note that a target class has to be defines in the SHACL file via the sh:targetClass command.

The mapping from the sst: commands to SHACL-SPARQL is done via the Mapping.py script. It takes parameters as input

1. Path to the SHACL file containing sst: commands
2. Output path were the SHACL file containing the SHACL-SPARQL mappings is stored

Command line: python .\Mapping.py /path/to/shaclGraph.ttl path/to/output.ttl

###sst:equivalentClass
Constraints of the constraint type class equivalence assert that two classes have the same instances.
The sst:equivalentClass command takes a string containing the class equivalent to the target class as input.

Example:

    sh:ExampleShape a sh:NodeShape ;
        sst:equivalentClass "ex:equivalentClass" ;
        sh:targetClass ex:targetClass .

###sst:disjointClass
The constraint type disjoint classes states that no individual can be at the same time an instance of both classes.
The sst:disjointClass command takes a string containing the class disjointed from the target class as input.

Example:

    sh:ExampleShape a sh:NodeShape ;
        sst:disjointClass "ex:disjointClass" ;
        sh:targetClass ex:targetClass .
       

###sst:inControlledVocabulary
Constraints of this type guarantee that individuals of a given class are assigned to the class skos:Concept and are included in a specific controlled vocabulary.
The sst:inControlledVocabulary command takes a string containing the target property and the target vocabulary as input. The inputs have to be separated by ','.

Example:

    sh:ExampleShape a sh:NodeShape ; 
        sst:inControlledVocabulary "ex:targetProperty, ex:targetVocabulary"
        sh:targetClass ex:targetClass .

###sst:languageTagDefinition
Values of the data property \'language tag\' must contain literals with a defined language tag.
The sst:languageTagDefinition command takes a string containing the target property and the language tag that must be present as input. The inputs have to be separated by ','.

Example:

    sh:ExampleShape a sh:NodeShape ; 
        sst:languageTagDefinition "ex:targetProperty, en" ;
        sh:targetClass ex:targetClass .

###sst:languageTagCardinalityEquals
Values of the data property \'language tag cardinality equals\' define the exact number of times a certain language tag has to occur on a given property.
The sst:languageTagCardinality command takes a string containing the target property, the language tag, and the cardinality as input. The inputs have to be separated by ','. 

Example:

    sh:ExampleShape a sh:NodeShape ;
        sst:languageTagCardinalityEquals "ex:targetProperty, en, 1" ;
        sh:targetClass ex:targetClass .

###sst:languageTagCardinalityMin
Values of the data property \'language tag cardinality min\' define the minimum number of times a certain language tag has to occur on a given property.
The sst:languageTagCardinality command takes a string containing the target property, the language tag, and the cardinality as input. The inputs have to be separated by ','. 

Example:

    sh:ExampleShape a sh:NodeShape ;
        sst:languageTagCardinalityMin "ex:targetProperty, en, 1" ;
        sh:targetClass ex:targetClass .
            
###sst:languageTagCardinalityMax
Values of the data property \'language tag cardinality max\' define the maximum number of times a certain language tag is allowed to occur on a given property.
The sst:languageTagCardinality command takes a string containing the target property, the language tag, and the cardinality as input. The inputs have to be separated by ','. 

Example:

    sh:ExampleShape a sh:NodeShape ;
        sst:languageTagCardinalityMax "ex:targetProperty, en, 1" ;
        sh:targetClass ex:targetClass .

###sst:functionalProperty
Objects of the data property \'functional property\' must be distinct.
The sst:functionalProperty command takes takes a string containing the target property as input. 

Example:

    sh:ExampleShape a sh:NodeShape ;
        sst:functionalProperty "ex:targetProperty" ;
        sh:targetClass ex:targetClass .

###sst:inverseFunctionalProperty
Subjects of the data property \'inverse functional property\' must be distinct.
The sst:inverseFunctionalProperty command takes takes a string containing the target property as input. 
Example:

    sh:ExampleShape a sh:NodeShape ;
        sst:inverseFunctionalProperty "ex:targetProperty" ;
        sh:targetClass ex:targetClass .

###sst:symmetricObjectProperty
A property is symmetric if it is equivalent to its own inverse.
The sst:symmetricObjectProperty command takes takes a string containing the target property as input. 

Example:

    sh:ExampleShape a sh:NodeShape ;
        sst:symmetricObjectProperty "ex:targetProperty" ;
        sh:targetClass ex:targetClass .

###sst:aSymmetricObjectProperty
A property is asymmetric if it is disjoint from its own inverse.
The sst:aSymmetricObjectProperty command takes takes a string containing the target property as input. 
Example:

    sh:ExampleShape a sh:NodeShape ;
    	sst:aSymmetricObjectProperty "ex:targetProperty" ;
        sh:targetClass ex:targetClass .

###sst:transitiveObjectProperty
A constraint of the constraint type transitive object properties states that the object property p is transitive.
The sst:transitiveObjectProperty command takes takes a string containing the target property as input. 

Example:

    sh:ExampleShape a sh:NodeShape ;
        sst:transitiveObjectProperty "ex:targetProperty" ;
        sh:targetClass ex:targetClass .
       
###sst:selfRestriction
A constraint of the constraint type self restriction consists of an object property p, and it makes sure that all individuals are connected by p to themselves.
The sst:selfRestriction command takes takes a string containing the target property as input. 

Example:

    sh:ExampleShape a sh:NodeShape ;	    
        sst:selfRestriction "ex:targetProperty" ;
        sh:targetClass ex:targetClass .
         
###sst:sumEquals
Values of the constraint \'sumEquals\' define exactly how many occurances of a given property have to exist for each data instance.
The sst:sumEquals command takes a string containing the target property and the cardinality as input. The inputs have to be separated by ','.

Example:

    sh:ExampleShape a sh:NodeShape ;	    
        sst:sumEquals "ex:targetProperty, 1" ;
        sh:targetClass ex:targetClass .

###sst:sumMin
Values of the constraint \'sumMin\' define how many occurances of a given property have to exist at least for each data instance.
The sst:sumMin command takes a string containing the target property and the cardinality as input. The inputs have to be separated by ','.

Example:

    sh:ExampleShape a sh:NodeShape ;	    
        sst:sumMin "ex:targetProperty, 1" ;
        sh:targetClass ex:targetClass .

###sst:sumMax
Values of the constraint \'sumMax\' define how many occurances of a given property have to exist at most for each data instance.
The sst:sumMax command takes a string containing the target property and the cardinality as input. The inputs have to be separated by ','.

Example:

    sh:ExampleShape a sh:NodeShape ;	    
        sst:sumMax "ex:targetProperty, 1" ;
        sh:targetClass ex:targetClass .

###Example
####Input

    sh:ProviderShape a sh:NodeShape ;
        sst:disjointClass "ex:Resource" ;
        sst:transitiveObjectProperty "ex:isSubsidiaryOf" ;
        sst:languageTagCardinalityEquals "rdfs:label, en, 1" ;
        sst:symmetricObjectProperty "ex:hasProjectPartner" ;
        sh:targetClass ex:Provider .
        
####Output

    sh:ProviderShape a sh:NodeShape ;
    sh:sparql [ sh:message "A property is symmetric if it is equivalent to its own inverse." ;
            sh:select """
			SELECT $this
			WHERE {
				$this ex:hasProjectPartner ?a .
				FILTER (!EXISTS { ?a ex:hasProjectPartner $this } )
			} 
			""" ],
        [ sh:message "The constraint type disjoint classes states that no individual can be at the same time an instance of both classes." ;
            sh:select """
			SELECT $this
			WHERE {
				$this a <http://www.example.orgProvider> .
				FILTER (EXISTS { $this a ex:Resource } )
			} 
			""" ],
        [ sh:message "A constraint of the constraint type transitive object properties states that the object property p is transitive." ;
            sh:select """
			SELECT $this
			WHERE {
				$this ex:isSubsidiaryOf ?a .
				?a ex:isSubsidiaryOf ?b .
				FILTER (!EXISTS { $this ex:isSubsidiaryOf ?b } )
			} 
			""" ],
        [ sh:message "Values of the constraint 'language tag cardinality equals' define exactly how many literals of the given language tag have to be defined." ;
            sh:select """
			SELECT $this
			WHERE {
				SELECT (COUNT(?value) as ?count)
				WHERE {
					$this rdfs:label ?value .
					FILTER (isLiteral(?value) && langMatches(lang(?value), 'en'))
				}
			}
			GROUP BY $this
			HAVING (SUM(?count) != 1)
			""" ] ;
    sh:targetClass ex:Provider .
    