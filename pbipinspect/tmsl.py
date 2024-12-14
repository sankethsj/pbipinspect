
from pathlib import Path

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
            'calculated': str(column.get('sourceColumn')).startswith('[') or bool(column.get('expression'))
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
        - expression: str
    """
    cleaned = []
    for partition in partitions:
        cleaned.append({
            'name': partition['name'],
            'type': partition['source']['type'],
            'mode': partition['mode'],
            'expression': ''.join(partition['source']['expression'])
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
    """
    cleaned: list[dict] = []
    if not measures:
        return cleaned
    for measure in measures:
        cleaned.append({
            'name': measure['name'],
            'lineageTag': measure['lineageTag'],
            'annotations': measure.get('annotations'),
            'displayFolder': measure['displayFolder'],
            'expression': ''.join(measure['expression']),
            'formatString': measure.get('formatString')
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
        cleaned.append({
            'name': table['name'],
            'lineageTag': table['lineageTag'],
            'isHidden': table.get('isHidden', False),
            'isPrivate': table.get('isPrivate', False),
            'columns': clean_tmsl_columns(table.get('columns', [])),
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
        - toCardinality: str
        - isActive: bool
    """
    cleaned = []
    for relationship in relationships:
        cleaned.append({
            'name': relationship['name'],
            'fromTable': relationship['fromTable'],
            'fromColumn': relationship['fromColumn'],
            'toTable': relationship['toTable'],
            'toColumn': relationship['toColumn'],
            'crossFilteringBehavior': relationship.get('crossFilteringBehavior', 'singleDirection'),
            'toCardinality': relationship.get('toCardinality', 'oneToMany'),
            'isActive': relationship.get('isActive', True)
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
    tables = model['tables']
    relationships = model['relationships']
    cleaned_tables = clean_tmsl_tables(tables)
    cleaned_relationships = clean_tmsl_relationships(relationships)
    new_model = {
        'model': {
            'tables': cleaned_tables,
            'relationships': cleaned_relationships
        }
    }
    return new_model
