
from pathlib import Path
from pbipinspect.parse.utils import (
    get_measure_references,
    put_column_description,
    get_measure_description,
    get_relationship_filter_cardinality,
    get_table_description,
    remove_doc_comments
)

def build_tmsl_path(semantic_model_path: str | Path) -> Path:
    new_path = Path(semantic_model_path)
    model = Path.joinpath(new_path, 'model.bim')
    return model

def is_TMSL(semantic_model_path: str | Path) -> bool:
    model_bim = build_tmsl_path(semantic_model_path)
    return model_bim.exists()

def clean_tmsl_columns(columns: list[dict]) -> list[dict]:
    """
    Clean columns from the given TMSL model.

    Parameters
    ----------
    columns : list[dict]
        The list of columns to clean

    Returns
    -------
    list[dict]
        A list of cleaned column dictionaries. The dictionaries have the following keys:
        - name: str
        - expression: str | None
        - isHidden: bool
        - isNameInferred: bool
        - dataType: str
        - lineageTag: str
        - summarizeBy: str
        - sourceColumn: str | None
        - annotations: list[str] | None
        - calculated: bool
        - description: str
    """
    cleaned: list[dict] = []
    if not columns:
        return cleaned
    for column in columns:
        cleaned.append({
            'name': column['name'],
            'expression': column.get('expression', ''),
            'isHidden': column.get('isHidden', False),
            'isNameInferred': column.get('isHidden', False),
            'dataType': column['dataType'],
            'lineageTag': column['lineageTag'],
            'summarizeBy': column['summarizeBy'],
            'sourceColumn': column.get('sourceColumn'),
            'annotations': column.get('annotations'),
            'calculated': str(column.get('sourceColumn')).startswith('[') or bool(column.get('expression')),
            'description': column.get('description', '')
        })
    return cleaned

def clean_tmsl_partitions(partitions: list[dict]) -> list[dict]:
    """
    Clean the given list of partition dictionaries.

    Parameters
    ----------
    partitions : list[dict]
        The list of partition dictionaries to clean

    Returns
    -------
    list[dict]
        A list of cleaned partition dictionaries. The dictionaries have the following keys:
        - name: str
        - type: str
        - mode: str
        - raw_expression: str
        - expression: str
        - description: str
    """
    cleaned = []
    for partition in partitions:
        expression = partition['source']['expression']
        if isinstance(expression, str):
            expression = [expression]
        expression = '\n'.join(expression).strip()
        cleaned.append({
            'name': partition['name'],
            'type': partition['source']['type'],
            'mode': partition['mode'],
            'raw_expression': expression,
            'expression': remove_doc_comments(expression),
            'description': get_table_description(expression)
        })
    return cleaned

def clean_tmsl_measures(measures: list[dict]) -> list[dict]:
    """
    Clean measures from the given TMSL model.

    Parameters
    ----------
    measures : list[dict]
        The list of measures to clean.

    Returns
    -------
    list[dict]
        A list of cleaned measure dictionaries. Each dictionary contains the following keys:
        - name: str
        - lineageTag: str
        - annotations: list[str] | None
        - displayFolder: str
        - expression: str
        - formatString: str | None
        - description: str
        - references: list[str]
    """
    cleaned: list[dict] = []
    if not measures:
        return cleaned
    for measure in measures:
        expression = measure['expression']
        if isinstance(expression, str):
            expression = [expression]
        expression = '\n'.join(expression).strip()
        cleaned.append({
            'name': measure['name'],
            'lineageTag': measure['lineageTag'],
            'annotations': measure.get('annotations'),
            'displayFolder': measure.get('displayFolder', ''),
            'expression': remove_doc_comments(expression),
            'formatString': measure.get('formatString'),
            'description': get_measure_description(expression),
            'references': get_measure_references(expression)
        })
    return cleaned

def clean_tmsl_tables(tables: list[dict]) -> list[dict]:
    """
    Clean tables from the given TMSL model.

    Parameters
    ----------
    tables : list[dict]
        The list of tables to clean.

    Returns
    -------
    list[dict]
        A list of cleaned table dictionaries. Each dictionary contains the following keys:
        - name: str
        - lineageTag: str
        - isHidden: bool
        - isPrivate: bool
        - columns: list[dict]
        - measures: list[dict]
        - partitions: list[dict]
    """
    cleaned = []
    for table in tables:
        expression = table['partitions'][0]['source']['expression']
        if isinstance(expression, str):
            expression = [expression]
        expression = '\n'.join(expression).strip()
        columns = table.get('columns', [])
        columns_with_descriptions = put_column_description(columns, expression)
        
        cleaned.append({
            'name': table['name'],
            'lineageTag': table['lineageTag'],
            'isHidden': table.get('isHidden', False),
            'isPrivate': table.get('isPrivate', False),
            'columns': clean_tmsl_columns(columns_with_descriptions),
            'measures': clean_tmsl_measures(table.get('measures', [])),
            'partitions': clean_tmsl_partitions(table['partitions'])
        })
    return cleaned

def clean_tmsl_relationships(relationships: list[dict]) -> list[dict]:
    """
    Clean relationships from the given TMSL model.

    Parameters
    ----------
    relationships : list[dict]
        The list of relationships to clean.

    Returns
    -------
    list[dict]
        A list of cleaned relationship dictionaries. Each dictionary contains the following keys:
        - name: str
        - fromTable: str
        - fromColumn: str
        - toTable: str
        - toColumn: str
        - crossFilteringBehavior: str
        - filteringSymbol: str
        - fromCardinalitySymbol: str
        - toCardinalitySymbol: str
        - isActive: bool
    """
    cleaned = []
    for relationship in relationships:
        filtering_behavior = relationship.get('crossFilteringBehavior', 'singleDirection')
        to_cardinality = relationship.get('toCardinality')
        from_cardinality = relationship.get('fromCardinality')

        filtering_cardinality = get_relationship_filter_cardinality(
            filtering_behavior,
            to_cardinality,
            from_cardinality
        )
        filtering_symbol, from_cardinality_symbol, to_cardinality_symbol = filtering_cardinality

        cleaned.append({
            'name': relationship['name'],
            'fromTable': relationship['fromTable'],
            'fromColumn': relationship['fromColumn'],
            'toTable': relationship['toTable'],
            'toColumn': relationship['toColumn'],
            'crossFilteringBehavior': filtering_behavior,
            'filteringSymbol': filtering_symbol,
            'fromCardinalitySymbol': from_cardinality_symbol,
            'toCardinalitySymbol': to_cardinality_symbol,
            'isActive': relationship.get('isActive', True)
        })
    return cleaned

def clean_tmsl_expressions(expressions: list[dict]) -> list[dict]:
    """
    Clean expressions from the given TMSL model.

    Parameters
    ----------
    expressions : list[dict]
        The list of expressions to clean.

    Returns
    -------
    list[dict]
        A list of cleaned expression dictionaries. Each dictionary contains the following keys:
        - name: str
        - expression: str
        - description: str
    """
    cleaned = []
    for expression in expressions:
        is_function = any([True for x in expression['annotations'] if x['value'] == 'Function'])
        if not is_function:
            expr = expression['expression'].split('meta')[0].strip()
        else:
            expr = '\n'.join(expression['expression']).strip()
        cleaned.append({
            'name': expression['name'],
            'lineageTag': expression['lineageTag'],
            'expression': expr,
            'description': expression.get('description'),
            'type': 'function' if is_function else 'parameter'
        })
    return cleaned

def clean_tmsl(tmsl_model: dict) -> dict:
    """
    Clean the given TMSL model.

    Parameters
    ----------
    tmsl_model : dict
        The TMSL model to clean.

    Returns
    -------
    dict
        A cleaned version of the given TMSL model.
    """
    model = tmsl_model['model']
    tables = model.get('tables', [])
    relationships = model.get('relationships', [])
    expressions = model.get('expressions', [])
    cleaned_tables = clean_tmsl_tables(tables)
    cleaned_relationships = clean_tmsl_relationships(relationships)
    cleaned_expressions = clean_tmsl_expressions(expressions)
    new_model = {
        'model': {
            'tables': cleaned_tables,
            'relationships': cleaned_relationships,
            'expressions': cleaned_expressions
        }
    }
    return new_model
