from pydantic import BaseModel, Field, create_model
from typing import Dict, Any

def build_response_class(config: Dict[str, Any]) -> type(BaseModel):
    """
    Builds the response class based on the criteria passed into the dictionary.
    """
    fields = {}
    data = config.get("data", {})
    
    # Data is in the format data = {"name": "description"}:
    for data_name, data_description in data.items():
        fields[data_name] = (str, Field(..., description=data_description))
    
    # Add the final output payload structure field
    output_payload_structure = f"""The final response should be structured as a JSON object with the following schema:
                                   {{data: {config.get("data", {})}}}. 
                                   # Requirements
                                   - The output should match this structure exactly. 
                                   - The output does not add any additional fields.
                                   - Assign null if the specified field has no information.
                                   """
    fields["output_payload_structure"] = (str, Field(..., description=output_payload_structure))
    
    # Create the dynamic Pydantic model class:
    ResponseClass = create_model("ResponseClass", **fields)
    return ResponseClass