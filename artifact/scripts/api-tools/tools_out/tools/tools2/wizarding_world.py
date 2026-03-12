import requests
from runtime import Args
from typings.getPottered.getPottered import Input, Output
from typing import Optional, Dict, Any, Union
import uuid

BASE_URL = "https://wizard-world-api.herokuapp.com"

def get_elixirs(args: Args[Input]) -> Output:
    endpoint = f"{BASE_URL}/Elixirs"
    params = {
        "Name": args.Name if hasattr(args, 'Name') else None,
        "Difficulty": args.Difficulty if hasattr(args, 'Difficulty') else None,
        "Ingredient": args.Ingredient if hasattr(args, 'Ingredient') else None
    }
    return make_request(endpoint, params)

def get_houses() -> Output:
    endpoint = f"{BASE_URL}/Houses"
    return make_request(endpoint)

def get_spells(args: Args[Input]) -> Output:
    endpoint = f"{BASE_URL}/Spells"
    params = {
        "Name": args.Name if hasattr(args, 'Name') else None,
        "Type": args.Type if hasattr(args, 'Type') else None,
        "Incantation": args.Incantation if hasattr(args, 'Incantation') else None
    }
    return make_request(endpoint, params)

def get_wizards(args: Args[Input]) -> Output:
    endpoint = f"{BASE_URL}/Wizards"
    params = {
        "FirstName": args.FirstName if hasattr(args, 'FirstName') else None,
        "LastName": args.LastName if hasattr(args, 'LastName') else None
    }
    return make_request(endpoint, params)

def get_wizard_by_id(wizard_id: str) -> Output:
    if not is_valid_uuid(wizard_id):
        return Output(data=None, error="Invalid wizard ID format")
    endpoint = f"{BASE_URL}/Wizards/{wizard_id}"
    return make_request(endpoint)

def is_valid_uuid(uuid_string: str) -> bool:
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def make_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Output:
    try:
        response = requests.get(endpoint, params={k: v for k, v in params.items() if v is not None} if params else None)
        
        if response.status_code == 200:
            data = response.json()
            return Output(data=data, error=None)
        elif response.status_code == 404:
            return Output(data=None, error="Resource not found")
        elif response.status_code == 429:
            return Output(data=None, error="Rate limit exceeded")
        else:
            return Output(data=None, error=f"Failed to retrieve data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        return Output(data=None, error=f"An error occurred: {str(e)}")

def handler(args: Args[Input]) -> Output:
    endpoint = args.endpoint if hasattr(args, 'endpoint') else 'elixirs'
    
    if endpoint == 'elixirs':
        return get_elixirs(args)
    elif endpoint == 'houses':
        return get_houses()
    elif endpoint == 'spells':
        return get_spells(args)
    elif endpoint == 'wizards':
        return get_wizards(args)
    elif endpoint == 'wizard_by_id':
        wizard_id = args.id if hasattr(args, 'id') else None
        if wizard_id:
            return get_wizard_by_id(wizard_id)
        else:
            return Output(data=None, error="Wizard ID is required for this endpoint")
    else:
        return Output(data=None, error="Invalid endpoint specified")