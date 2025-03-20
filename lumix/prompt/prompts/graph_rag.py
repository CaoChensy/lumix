from lumix.prompt.template import PromptTemplate


__all__ = [
    "entities_prompt",
    "relations_prompt",
]


template_entities = """Given a text document that is potentially relevant to this activity and a list of entity types.
Identify all entities. For each identified entity, extract the following information:
- entity: Name of the entity, capitalized
- type: One of the following types: {types}
- description: Comprehensive description of the entity's attributes and activities
Format each entity as List[Tuple]
```python
[(<entity>, <type>, <description>), ...]
```
If no entity is extracted, an empty list is output.

Entity Types: ```\n{types}```
Document: ```\n{content}```
Output:
"""

entities_prompt = PromptTemplate(
    input_variables=["types", "content"],
    template=template_entities,
)

template_relations = """Given your text, entity type, and extracted entities, 
you need to identify all pairs of (source, target) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
    - source: name of the source entity
    - target: name of the target entity
    - relationship: name of the relationship between the source entity and target entity
    - description: explanation as to why you think the source entity and the target entity are related to each other
    - strength: a numeric score indicating strength of the relationship between the source entity and target entity
Format each relationship as List[Tuple]:
```python
[(<source>, <target>, <relationship>, <description>, <strength>), ...]
```
If no relations is extracted, an empty list is output.

Content: ```\n{content}```
Entity Types: ```\n{types}```
Entities: ```\n{entities}```
Output:
"""

relations_prompt = PromptTemplate(
    input_variables=["content", "types", "entities"],
    template=template_relations,
)
