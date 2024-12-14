
from pathlib import Path
from pbipinspect.utils import get_regex_group
import re
from typing import Optional

def build_relationship_path(semantic_model_path: str | Path) -> Path:
    new_path = Path(semantic_model_path)
    table_folder = Path.joinpath(new_path, 'definition', 'relationships.tmdl')
    return table_folder

def has_relationship_file(semantic_model_path: str | Path) -> bool:
    new_path = Path(semantic_model_path)
    relationship_file = build_relationship_path(new_path)
    if relationship_file.exists():
        return True
    return False

def get_tmdl_relationship_file(semantic_model_path: str | Path) -> Path:
    new_path = Path(semantic_model_path)
    relationship_file = build_relationship_path(new_path)
    return relationship_file

def get_lineage_tag(x: str) -> Optional[str]:
    pattern = r'lineageTag:\s?([0-9a-zA-Z-]+)'
    tag = get_regex_group(x=x, pattern=pattern)
    return tag

def get_relationship_name(x: str) -> str:
    name = x.split('\n')[0]
    return name

def get_relationship_from_to(
    x: str, 
    pattern: str | re.Pattern[str]
) -> tuple[Optional[str], Optional[str]]:
    from_column = re.search(pattern, x)
    if from_column is None:
        return (None, None)
    else: 
        content = from_column.group(1).split('.')
        table = content[0]
        column = content[1]
        return (table, column)

def get_relationship_from_column(x: str) -> tuple[Optional[str], Optional[str]]:
    return get_relationship_from_to(x, r'fromColumn:\s?(.*)')
    
def get_relationship_to_column(x: str) -> tuple[Optional[str], Optional[str]]:
    return get_relationship_from_to(x, r'toColumn:\s?(.*)')

def get_relationship_cardinality(x: str) -> str:
    pattern = r'toCardinality:\s?(\w+)'
    cardinality = get_regex_group(x=x, pattern=pattern, if_none='oneToMany')
    return cardinality

def get_relationship_cross_filtering_behavior(x: str) -> Optional[str]:
    if 'crossFilteringBehavior' in x:
        pattern = r'crossFilteringBehavior:\s?(\w+)'
        behavior = get_regex_group(x=x, pattern=pattern)
        return behavior
    return 'singleDirection'

def get_relationship_is_active(x: str) -> Optional[str]:
    pattern = r'isActive\:\s?(\w+)'
    is_active = get_regex_group(x=x, pattern=pattern, if_none=True)
    return is_active

def get_tmdl_relationship(tmdl: str) -> list[dict]:
    """
    Parse the relationships from a given TMDL content.

    Parameters
    ----------
    tmdl : str
        The content of a TMDL file.

    Returns
    -------
    list[dict]
        A list of dictionaries, each one representing a relationship.
        Each dictionary has the following keys:
            'name': str
                The name of the relationship.
            'fromTable': str
                The name of the table from which the relationship starts.
            'fromColumn': str
                The name of the column from which the relationship starts.
            'toTable': str
                The name of the table to which the relationship ends.
            'toColumn': str
                The name of the column to which the relationship ends.
            'crossFilteringBehavior': str
                The cross filtering behavior of the relationship.
                Can be 'oneDirection' or 'bothDirections'.
            'toCardinality': str
                The cardinality of the relationship.
                Can be 'oneToOne', 'oneToMany' or 'manyToMany'.
            'isActive': bool
                Whether the relationship is active or not.
    """

    splited = tmdl.split('relationship')[1:]
    relationships = []
    for x in splited:
        name = get_relationship_name(x)
        from_table, from_column = get_relationship_from_column(x)
        to_table, to_column = get_relationship_to_column(x)
        cross_filtering_behavior = get_relationship_cross_filtering_behavior(x)
        to_cardinality = get_relationship_cardinality(x)
        is_active = get_relationship_is_active(x)
        relationships.append({
            'name': name,
            'fromTable': from_table,
            'fromColumn': from_column,
            'toTable': to_table,
            'toColumn': to_column,
            'crossFilteringBehavior': cross_filtering_behavior,
            'toCardinality': to_cardinality,
            'isActive': is_active
        })
    return relationships

def build_table_path(semantic_model_path: str | Path) -> Path:
    new_path = Path(semantic_model_path)
    table_folder = Path.joinpath(new_path, 'definition', 'tables')
    return table_folder

def has_table_folder(semantic_model_path: str | Path) -> bool:
    new_path = Path(semantic_model_path)
    table_folder = build_table_path(new_path)
    if table_folder.exists():
        return True
    return False

def get_tmdl_table_files(semantic_model_path: str | Path) -> list[Path]:
    new_path = Path(semantic_model_path)
    table_folder = build_table_path(new_path)
    tables = list(table_folder.glob('*.tmdl'))
    return tables

def get_table_name(tmdl: str) -> Optional[str]:
    pattern = r'(?<=table\s)([A-Za-z0-9_-]+)'
    name = get_regex_group(x=tmdl, pattern=pattern)
    return name

def get_table_content(tmdl: str) -> str:
    content = re.split(r'column|measure|partition|annotation|hierarchy', tmdl)[0]
    return content

def get_table_lineage_tag(tmdl: str) -> Optional[str]:
    table_content = get_table_content(tmdl)
    lineage_tag = get_lineage_tag(table_content)
    return lineage_tag

def check_table_property(tmdl: str, property: str) -> bool:
    table_content = get_table_content(tmdl)
    check = property in table_content
    return check

def get_annotations(x: str) -> Optional[list[dict]]:
    annotations = re.findall(r'annotation\s(\w+)\s?\=\s?(.*)', x)
    column_annotation = []
    if annotations == []:
        return None
    for x in annotations:
        column_annotation.append({'name': x[0], 'value': x[1]})
    return column_annotation

def get_table_columns_content(tmdl: str) -> list[str]:
    content = tmdl.split('column')[1:]
    valid_content = [x for x in content if not x.startswith(':')]#[0]
    return valid_content

def get_table_column_name_expression(x: str) -> tuple[Optional[str], Optional[str]]:
    pattern = r'(\w+)\s?\=?\s?(.*)$'
    x_splited = x.split('\n')[0]
    name = get_regex_group(x=x_splited, pattern=pattern, group=1)
    expression = get_regex_group(x=x_splited, pattern=pattern, group=2)
    return (name, expression)

def get_table_column_data_type(x: str) -> Optional[str]:
    pattern = r'dataType:\s?(\w+)'
    data_type = get_regex_group(x=x, pattern=pattern)
    return data_type

def get_table_summarize_by(x: str) -> Optional[str]:
    pattern = r'summarizeBy:\s?(\w+)'
    summarize_by = get_regex_group(x=x, pattern=pattern)
    return summarize_by

def get_table_source_column(x: str) -> Optional[str]:
    pattern = r'sourceColumn:\s?(\[?\w+\]?)'
    source_column = get_regex_group(x=x, pattern=pattern)
    return source_column

def get_table_column_type(x: str) -> Optional[str]:
    pattern = r'type:\s?(\w+)'
    type = get_regex_group(x=x, pattern=pattern)
    return type

def get_table_columns(tmdl: str) -> list[dict]:
    """
    Parse columns from the given tmdl string.

    Parameters
    ----------
    tmdl : str
        TMDL string

    Returns
    -------
    list[dict]
        A list of dictionaries containing column information. Each dictionary has the following keys:
        - name: str
        - expression: str
        - isHidden: bool
        - isNameInferred: bool
        - dataType: str | None
        - lineageTag: str | None
        - summarizeBy: str | None
        - sourceColumn: str | None
        - annotations: list[dict] | None
        - calculated: bool
    """
    content = get_table_columns_content(tmdl)
    columns = []
    for x in content:
        cur_value = re.split(r'measure|partition|hierarchy', x)[0]
        name, expression = get_table_column_name_expression(cur_value)
        data_type = get_table_column_data_type(cur_value)
        is_hidden = 'isHidden' in cur_value
        is_name_inferred = 'isNameInferred' in cur_value
        lineage_tag = get_lineage_tag(cur_value)
        summarize_by = get_table_summarize_by(cur_value)
        source_column = get_table_source_column(cur_value)
        annotations = get_annotations(cur_value)
        columns.append({
            'name': name,
            'expression': expression,
            'isHidden': is_hidden,
            'isNameInferred': is_name_inferred,
            'dataType': data_type,
            'lineageTag': lineage_tag,
            'summarizeBy': summarize_by,
            'sourceColumn': source_column,
            'annotations': annotations,
            'calculated': str(source_column).startswith('[') or expression
        })
    return columns

def get_table_partition_name_type(x: str) -> tuple[Optional[str], Optional[str]]:
    pattern = r'(.*)\s?\=\s?(\w+)'
    x_splited = x.split('\n')[0]
    name = get_regex_group(x=x_splited, pattern=pattern, group=1)
    type = get_regex_group(x=x_splited, pattern=pattern, group=2)
    if name and type:
        return (name.strip(), type.strip())
    return (None, None)

def get_table_partition_mode(x: str) -> Optional[str]:
    pattern = r'mode:\s?(\w+)'
    mode = get_regex_group(x=x, pattern=pattern)
    return mode

def get_table_partition_source(x: str) -> Optional[str]:
    source_idx = re.search(r'source\s?=', x)
    if source_idx is None:
        return None
    else: 
        idx = source_idx.span()[1]
        source = x[idx:].replace('\t', '').replace('```', '').strip()
        return source

def get_table_partitions(tmdl: str) -> list[dict]:
    """
    Parse partitions from the given tmdl string.

    Parameters
    ----------
    tmdl : str
        TMDL string

    Returns
    -------
    list[dict]
        A list of dictionaries containing partition information. Each dictionary has the following keys:
        - name: str
        - type: str
        - mode: str
        - expression: str
    """
    splited = [x for x in tmdl.split('partition')[1:]]
    partitions = []
    for x in splited:
        cur_value = re.split(r'measure|column|hierarchy|annotation', x)[0]
        name, type = get_table_partition_name_type(cur_value)
        mode = get_table_partition_mode(cur_value)
        source = get_table_partition_source(cur_value)
        partitions.append({
            'name': name,
            'type': type,
            'mode': mode,
            'expression': source
        })
    return partitions

def get_table_measure_name(x: str) -> str:
    name = x.split('=')[0].strip()
    return name

def get_table_measure_format_string(x: str) -> Optional[str]:
    pattern = r'formatString:\s?(.*)\n'
    format_string = get_regex_group(x=x, pattern=pattern)
    return format_string

def get_table_measure_display_folder(x: str) -> Optional[str]:
    pattern = r'displayFolder:\s?(.*)\n'
    display_folder = get_regex_group(x=x, pattern=pattern)
    return display_folder

def get_table_measure_expression(x: str) -> str:
    pattern = r'formatString|displayFolder|lineageTag|annotation'
    raw_expression = re.split(pattern, x)[0].split('=')[1:]
    expression = ''.join(raw_expression).replace('\t', '').replace('```', '').strip()
    return expression

def get_table_measures(tmdl: str) -> list[dict]:
    """
    Parse measures from the given tmdl string.

    Parameters
    ----------
    tmdl : str
        TMDL string

    Returns
    -------
    list[dict]
        A list of dictionaries containing measure information. Each dictionary has the following keys:
        - name: str
        - formatString: str | None
        - annotations: list[str]
        - displayFolder: str | None
        - lineageTag: str | None
        - expression: str
    """
    splited = [x for x in tmdl.split('measure')[1:]]
    measures = []
    for x in splited:
        cur_value = re.split(r'partition|column|hierarchy', x)[0]
        name = get_table_measure_name(cur_value)
        format_string = get_table_measure_format_string(cur_value)
        display_folder = get_table_measure_display_folder(cur_value)
        lineage_tag = get_lineage_tag(cur_value)
        annotations = get_annotations(cur_value)
        expression = get_table_measure_expression(cur_value)
        measures.append({
            'name': name,
            'formatString': format_string,
            'annotations': annotations,
            'displayFolder': display_folder,
            'lineageTag': lineage_tag,
            'expression': expression
        })
    return measures

def get_tmdl_table(tmdl: str) -> dict:
    """
    Reads a .tmdl file and returns a dictionary containing the table information

    Parameters
    ----------
    tmdl : str
        The contents of the .tmdl file

    Returns
    -------
    dict
        A dictionary containing the table information with the following keys:
            - name: The name of the table
            - lineageTag: The lineage tag of the table
            - isHidden: A boolean indicating if the table is hidden
            - isPrivate: A boolean indicating if the table is private
            - columns: A list of dictionaries containing the column information
            - measures: A list of dictionaries containing the measure information
            - partitions: A list of dictionaries containing the partition information
    """
    table_name = get_table_name(tmdl)
    lineage_tag = get_table_lineage_tag(tmdl)
    is_hidden = check_table_property(tmdl, 'isHidden')
    is_private = check_table_property(tmdl, 'isPrivate')
    table_columns = get_table_columns(tmdl)
    table_measures = get_table_measures(tmdl)
    table_partitions = get_table_partitions(tmdl)
    return {
        'name': table_name,
        'lineageTag': lineage_tag,
        'isHidden': is_hidden,
        'isPrivate': is_private,
        'columns': table_columns,
        'measures': table_measures,
        'partitions': table_partitions
    }
