import hashlib
import uuid


def create_uuid_from_string(val: str):
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)


def row_to_uuid(row):
    row_string = ','.join(row.astype(str))  # Convert each element of the row to string and join them with commas
    return create_uuid_from_string(row_string)


def flatten_list(nested_list) -> list:
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))  # Recursively flatten
        elif isinstance(item, str):
            # Strip whitespace and convert to lowercase
            flat_list.append(item.strip().lower().replace('"', ''))
        else:
            flat_list.append(item)
    return flat_list
