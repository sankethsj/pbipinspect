
from copy import deepcopy
import re

def remove_doc_comments(x: str) -> str:
    """Removes Power BI style doc comments from a string.

    The function removes all occurrences of /* @doc */ comments from a given string.

    Parameters
    ----------
    x : str
        The string to remove the doc comments from.

    Returns
    -------
    str
        The string with the doc comments removed.
    """
    pattern = r'/\*\s?@doc.*?\*/'
    return re.sub(pattern, '', x, flags=re.DOTALL).strip()

def get_measure_references_table_column(expression: str) -> list[str]:
    """
    Returns all table column references in a given measure expression.

    The function returns all table column references found in a given measure expression.
    The table column references are returned as a list of strings, where each string
    represents a table column reference in the following format: table_name[column_name].

    Parameters
    ----------
    expression : str
        The measure expression to find the table column references in.

    Returns
    -------
    list[str]
        The list of table column references found in the measure expression.
    """
    pattern = r"(?:\b[a-zA-Z_][a-zA-Z0-9_]*\[[^\]]+\])|(?:\'[^\']+\'\[[^\]]+\])"
    matches = re.findall(pattern, expression)
    unique_matches = list(set(matches))
    return unique_matches

def get_measure_references_measure(expression: str) -> list[str]:
    """
    Returns all measure references in a given measure expression.

    The function returns all measure references found in a given measure expression.
    The measure references are returned as a list of strings, where each string
    represents a measure reference in the following format: measure_name.

    Parameters
    ----------
    expression : str
        The measure expression to find the measure references in.

    Returns
    -------
    list[str]
        The list of measure references found in the measure expression.
    """
    pattern = r'(?<![\w\'])\[[^\]]+\](?!\[\w)'
    matches = re.findall(pattern, expression)
    unique_matches = list(set([m.replace('[', '').replace(']', '') for m in matches]))
    return unique_matches

def get_measure_references(expression: str) -> list[dict]:
    """
    Extracts table column and measure references from a given expression.

    This function analyzes a measure expression to identify references to
    table columns and other measures. It returns a list of dictionaries
    where each dictionary describes a reference, specifying whether it is
    a 'table' or a 'measure', along with the respective name and column
    information for table references.

    Parameters
    ----------
    expression : str
        The measure expression to analyze for references.

    Returns
    -------
    list[dict]
        A list of dictionaries representing the references found in the
        expression. Each dictionary contains:
        - 'type': 'table' or 'measure'
        - 'name': Name of the table or measure
        - 'column': Name of the column (only for table references)
    """
    table_column = get_measure_references_table_column(expression)
    measures = get_measure_references_measure(expression)

    references = []
    for tc in table_column:
        table, column, _ = re.split('\\[|\\]', tc)
        references.append({
            'type': 'table',
            'name': table,
            'column': column
        })

    for m in measures:
        references.append({
            'type': 'measure',
            'name': m
        })
    return references

def get_table_description(x: str, pattern = r'@doc\s+(.*?)(?=@col|$)') -> str:
    """
    Extracts the table description from a given string.

    This function takes a string and returns the table description, if present.
    The table description is the text that follows the '@doc' tag until the
    '@col' tag or the end of the string.

    Parameters
    ----------
    x : str
        The string to extract the table description from.
    pattern : str, optional
        The regular expression pattern to match the table description.
    
    Returns
    -------
    str
        The extracted table description, or an empty string if no description is present.
    """
    description = re.search(pattern, x, flags=re.DOTALL)
    if description is None:
        return ''
    return description.group(1).replace('\t', '').strip()

def get_measure_description(x: str) -> str:
    """
    Extracts the measure description from a given string.

    This function takes a string and returns the measure description, if present.

    Parameters
    ----------
    x : str
        The string to extract the measure description from.

    Returns
    -------
    str
        The extracted measure description, or an empty string if no description is present.
    """
    pattern = r'/\* @doc(.*?)\*/'
    description = re.search(pattern, x, flags=re.DOTALL)
    if description is None:
        return ''
    return description.group(1).replace('\t', '').strip()

def get_table_column_description(x: str) -> dict[str, str]:
    """
    Extracts the column descriptions from a given string.

    This function takes a string and returns a dictionary with the column names as
    keys and their descriptions as values. The descriptions are the text that follows
    the '@col' tag until the '@col' or '*/' tag or the end of the string.

    Parameters
    ----------
    x : str
        The string to extract the column descriptions from.

    Returns
    -------
    dict[str, str]
        A dictionary with the column names as keys and their descriptions as values.
    """
    pattern = r'@col\s+(\w+):\s+(.*?)(?=@col|\*\/)'
    matches = re.findall(pattern, x, re.DOTALL)
    result = {match[0]: match[1].strip() for match in matches}
    return result

def put_column_description(
    columns: list[dict],
    table_expression: str
) -> list[dict]:
    """
    Adds column descriptions to a list of columns.

    This function takes a list of columns and a table expression, extracts the column
    descriptions from the table expression, and adds them to the columns.

    Parameters
    ----------
    columns : list[dict]
        The list of columns to add descriptions to.
    table_expression : str
        The table expression to extract the column descriptions from.

    Returns
    -------
    list[dict]
        The list of columns with descriptions added.
    """
    cur_columns = deepcopy(columns)
    columns_description = get_table_column_description(table_expression)
    if columns:
        for column in cur_columns:
            column_name = column['name']
            if column_name in columns_description:
                column['description'] = columns_description[column_name]
            else:
                column['description'] = ''
    return cur_columns

def get_relationship_filter_cardinality(
    filtering: str,
    to_cardinality: str | None,
    from_cardinality: str | None,
) -> tuple[str, str, str]:
    """
    Returns a tuple of 3 strings that represent the filtering direction, and the
    cardinality of the "from" and "to" columns in a relationship.

    Parameters
    ----------
    filtering : str
        The filtering behavior of the relationship. Can be 'singleDirection' or
        'bothDirections'.
    to_cardinality : str | None
        The cardinality of the "to" column in the relationship. Can be 'one' or
        'many', or None.
    from_cardinality : str | None
        The cardinality of the "from" column in the relationship. Can be 'one' or
        'many', or None.

    Returns
    -------
    tuple[str, str, str]
        A tuple of 3 strings. The first element is the filtering direction
        symbol, the second element is the "from" column cardinality symbol, and
        the third element is the "to" column cardinality symbol. The filtering
        direction symbol is '<' for single direction and '<>' for both
        directions. The cardinality symbols are '1' for one-to-one and '*' for
        one-to-many or many-to-many.
    """
    filtering_symbol = '<' if filtering == 'singleDirection' else '<>'
    from_cardinality_symbol = '*'
    to_cardinality_symbol = '*'

    if filtering == 'bothDirections':
        if from_cardinality == 'one' or to_cardinality == 'one':
            from_cardinality_symbol = '1'
            to_cardinality_symbol = '1'
        elif not from_cardinality and not to_cardinality:
            to_cardinality_symbol = '1'
        elif to_cardinality == 'oneToMany':
            to_cardinality_symbol = '1'

    elif filtering == 'singleDirection':
        if not to_cardinality:
            to_cardinality_symbol = '1'
        elif to_cardinality == 'many':
            from_cardinality_symbol = '*'
            to_cardinality_symbol = '*'
        elif to_cardinality == 'oneToMany':
            from_cardinality_symbol = '*'
            to_cardinality_symbol = '1'
    
    return (filtering_symbol, from_cardinality_symbol, to_cardinality_symbol)

def get_content_until_next_level(
    content: list[str],
    level_identifier: str='\t'
) -> list[str]:
    """
    Returns the content until the next level of indentation.

    Parameters
    ----------
    content : list[str]
        The content to be processed.
    level_identifier : str, optional
        The string used to identify the level of indentation. Defaults to '\t'.

    Returns
    -------
    list[str]
        The content until the next level of indentation.
    """
    if not content:
        return []
    last = content[-1].split('\n')
    idx_next_level = [
        idx for idx, x in enumerate(last)
        if x.count(level_identifier) == 1
    ]
    if not idx_next_level:
        return content[:-1] + ['\n'.join(last)]
    return content[:-1] + ['\n'.join(last[0:idx_next_level[0]])]

def get_table_property_content(
    tmdl: str, 
    property: str, 
    level_identifier: str='\t'
) -> list[str]:
    """
    Returns the content of a given table property from a TMDL file.

    Parameters
    ----------
    tmdl : str
        The content of the TMDL file.
    property : str
        The name of the property to be extracted. Can be 'column', 'measure', or
        'partition'.
    level_identifier : str, optional
        The string used to identify the level of indentation. Defaults to '\t'.

    Returns
    -------
    list[str]
        The content of the given table property.
    """
    content = tmdl.split(f'{level_identifier}{property} ')[1:]
    valid_content = get_content_until_next_level(content)
    return valid_content
