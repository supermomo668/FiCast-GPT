from pydantic import BaseModel
from typing import List, Dict, Any

from thought_agents.ontology.parser.dialogue import Person

def get_all_participants(participant_data: Dict[str, str]) -> List[Person]:
    """
    Flattens a nested participants dictionary into a single list of Person objects..
    """
    flattened_participants = participant_data["hosts"] + participant_data["guests"]
    return [Person(**participant) for participant in flattened_participants]

def update_existing_character(existing_persons: List[Person], new_persons: List[Person], target_attribute) -> List[Person]:
    """
    Updates existing persons with information from new persons.
    Args:
        existing_persons: List of persons to be updated
        target_attribute: Attribute to be updated
    """
    name_to_person = {person.name: person for person in new_persons}
    existing_persons = existing_persons.copy()
    for person in existing_persons:
        if person.name in name_to_person:
            new_person = name_to_person[person.name]
            # Update fields if they are None
            if person.__getattribute__(target_attribute) is None:
              person.__setattr__(
                target_attribute, new_person.__getattribute__(target_attribute))
    return existing_persons