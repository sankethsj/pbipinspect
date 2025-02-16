
from pathlib import Path
from pbipinspect.utils import get_regex_group
from pbipinspect.parse.utils import (
    get_measure_references,
    put_column_description,
    get_measure_description,
    get_relationship_filter_cardinality,
    get_table_description,
    get_table_property_content,
    remove_doc_comments,
)
import re
from typing import Optional

def build_component_path(semantic_model_path: str | Path, component: str) -> Path:
    new_path = Path(semantic_model_path)
    table_folder = Path.joinpath(new_path, 'definition', component)
    return table_folder

def build_relationship_path(semantic_model_path: str | Path) -> Path:
    return build_component_path(semantic_model_path, 'relationships.tmdl')

def build_expression_path(semantic_model_path: str | Path) -> Path:
    return build_component_path(semantic_model_path, 'expressions.tmdl')

def has_relationship_file(semantic_model_path: str | Path) -> bool:
    new_path = Path(semantic_model_path)
    relationship_file = build_relationship_path(new_path)
    if relationship_file.exists():
        return True
    return False

def has_expression_file(semantic_model_path: str | Path) -> bool:
    new_path = Path(semantic_model_path)
    expression_file = build_expression_path(new_path)
    if expression_file.exists():
        return True
    return False

def get_tmdl_relationship_file(semantic_model_path: str | Path) -> Path:
    new_path = Path(semantic_model_path)
    relationship_file = build_relationship_path(new_path)
    return relationship_file

def get_tmdl_expression_file(semantic_model_path: str | Path) -> Path:
    new_path = Path(semantic_model_path)
    expression_file = build_expression_path(new_path)
    return expression_file

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

def get_relationship_to_cardinality(x: str) -> str:
    pattern = r'toCardinality:\s?(\w+)'
    cardinality = get_regex_group(x=x, pattern=pattern, if_none='oneToMany')
    return cardinality

def get_relationship_from_cardinality(x: str) -> str:
    pattern = r'fromCardinality:\s?(\w+)'
    cardinality = get_regex_group(x=x, pattern=pattern, if_none='oneToMany')
    return cardinality

def get_relationship_cross_filtering_behavior(x: str) -> str:
    pattern = r'crossFilteringBehavior:\s?(\w+)'
    behavior = get_regex_group(x=x, pattern=pattern, if_none='singleDirection')
    return behavior

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
            'filteringSymbol': str
                The filtering symbol of the relationship.
                Can be '<' or '<>'.
            'fromCardinalitySymbol': str
                The cardinality symbol of the relationship.
                Can be '1' or '*'.
            'toCardinalitySymbol': str
                The cardinality symbol of the relationship.
                Can be '1' or '*'.
            'isActive': bool
                Whether the relationship is active or not.
    """

    splited = tmdl.split('relationship')[1:]
    relationships = []
    for x in splited:
        filtering_behavior = get_relationship_cross_filtering_behavior(x)
        from_cardinality = get_relationship_from_cardinality(x)
        to_cardinality = get_relationship_to_cardinality(x)

        filtering_cardinality = get_relationship_filter_cardinality(
            filtering_behavior,
            to_cardinality,
            from_cardinality
        )
        filtering_symbol, from_cardinality_symbol, to_cardinality_symbol = filtering_cardinality

        name = get_relationship_name(x)
        from_table, from_column = get_relationship_from_column(x)
        to_table, to_column = get_relationship_to_column(x)
        cross_filtering_behavior = get_relationship_cross_filtering_behavior(x)
        is_active = get_relationship_is_active(x)
        relationships.append({
            'name': name,
            'fromTable': from_table,
            'fromColumn': from_column,
            'toTable': to_table,
            'toColumn': to_column,
            'crossFilteringBehavior': cross_filtering_behavior,
            'filteringSymbol': filtering_symbol,
            'fromCardinalitySymbol': from_cardinality_symbol,
            'toCardinalitySymbol': to_cardinality_symbol,
            'isActive': is_active
        })
    return relationships

def get_expression_name(x: str) -> str:
    pattern = r"expression\s(.*)"
    name = str(get_regex_group(x=x, pattern=pattern)).split(' =')[0]
    return name

def get_expression_parameter_description(x: str, parameter: str) -> str:
    pattern = f'\/\/\/(.*)\nexpression\s({parameter})'
    search = re.search(pattern, x)
    if search is None:
        return ''
    return search.group(1).strip()

def get_expression_function_description(expression: str, pattern: str) -> str:
    return get_table_description(expression, pattern)

def is_expression_function(x: str):
    pattern = r'(annotation PBI_ResultType = Function)'
    return bool(get_regex_group(x=x, pattern=pattern))

def get_tmdl_expressions(tmdl: str) -> list[dict]:
    splited = [x for x in tmdl.split('\n') if x != '']
    no_tabs_idx = [idx 
        for (idx, value) in enumerate(splited)
        if value.count('\t') == 0
    ] + [len(splited)]
    sequences = list(zip(no_tabs_idx[0:-1], no_tabs_idx[1:]))
    expressions = []
    for begin, end in sequences:
        cur_list = splited[begin:end]
        cur = '\n'.join(splited[begin:end])
        expression_name = get_expression_name(cur)
        expression_lineage = get_lineage_tag(cur)
        if expression_name == 'None':
            continue
        is_function = is_expression_function(cur)
        if is_function:
            idx_next_level = [idx
                for (idx, value) in enumerate(cur_list[1:])
                if value.count('\t') == 1
            ][0] + 1
            raw_value = '\n'.join(cur_list[1:idx_next_level]).replace('\t\t', '')
            value = remove_doc_comments(raw_value).replace('```', '')
            description = get_expression_function_description(raw_value, r'@doc(.*?)(?=let)').replace('*/', '').strip()
        else:
            value = splited[begin].split('=')[1].split('meta')[0].strip()
            description = get_expression_parameter_description(x=tmdl, parameter=expression_name)
        expressions.append({
            'name': expression_name,
            'lineageTag': expression_lineage,
            'type': 'function' if is_function else 'expression',
            'expression': value,
            'description': description
        })
    return expressions

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
    pattern = r"table\s+['\"]?([^'\"]+?)['\"]?\s*\n"
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
    return get_table_property_content(tmdl, 'column')

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
    for cur_value in content:
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

def get_table_partition_content(tmdl: str) -> list[str]:
    return get_table_property_content(tmdl, 'partition')

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
        - raw_expression: str
        - expression: str
        - description: str
    """
    content = get_table_partition_content(tmdl)
    partitions = []
    for cur_value in content:
        name, type = get_table_partition_name_type(cur_value)
        mode = get_table_partition_mode(cur_value)
        source = get_table_partition_source(cur_value)
        description = get_table_description(cur_value)
        source_without_docs = remove_doc_comments(source) if source else None
        partitions.append({
            'name': name,
            'type': type,
            'mode': mode,
            'raw_expression': source,
            'expression': source_without_docs,
            'description': description,
        })
    return partitions

def get_table_measure_content(tmdl: str) -> list[str]:
    return get_table_property_content(tmdl, 'measure')

def get_table_measure_name(x: str) -> str:
    name = x.split('=')[0].strip()
    return name

def get_table_measure_format_string(x: str) -> Optional[str]:
    pattern = r'formatString:\s?(.*)\n'
    format_string = get_regex_group(x=x, pattern=pattern)
    return format_string

def get_table_measure_display_folder(x: str) -> str:
    pattern = r'displayFolder:\s?(.*)\n'
    display_folder = get_regex_group(x=x, pattern=pattern, if_none='')
    return display_folder

def get_table_measure_expression(x: str) -> str:
    pattern = r'formatString|displayFolder|lineageTag|annotation'
    without_description = remove_doc_comments(x)
    raw_expression = re.split(pattern, without_description)[0].split('=')[1:]
    expression = '='.join(raw_expression).replace('\t', '').replace('```', '').strip()
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
        - description: str
        - references: list[str]
    """
    content = get_table_measure_content(tmdl)
    measures = []
    for cur_value in content:
        name = get_table_measure_name(cur_value)
        format_string = get_table_measure_format_string(cur_value)
        display_folder = get_table_measure_display_folder(cur_value)
        lineage_tag = get_lineage_tag(cur_value)
        annotations = get_annotations(cur_value)
        expression = get_table_measure_expression(cur_value)
        description = get_measure_description(cur_value)
        references = get_measure_references(expression)
        measures.append({
            'name': name,
            'formatString': format_string,
            'annotations': annotations,
            'displayFolder': display_folder,
            'lineageTag': lineage_tag,
            'expression': expression,
            'description': description,
            'references': references
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

    expression = table_partitions[0]['raw_expression']
    columns_with_descriptions = put_column_description(table_columns, expression)
    return {
        'name': table_name,
        'lineageTag': lineage_tag,
        'isHidden': is_hidden,
        'isPrivate': is_private,
        'columns': columns_with_descriptions,
        'measures': table_measures,
        'partitions': table_partitions
    }
