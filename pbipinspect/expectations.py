
from pbipinspect.pbip import Pbip
from pbipinspect.utils import (
    check_lines_max_length,
    smart_join
)
from textwrap import dedent
from typing import Callable, Literal

ExpectState = Literal['Warning', 'Error', 'Info']
ExpectMessage = dict[str, str]
ColTypes = Literal[
    'double',
    'percentage', # not supported
    'duration',   # not supported
    'decimal',
    'int64',
    'int32',
    'int16',
    'int8',

    'string',

    'dateTime',
    'time'       # not supported

    'boolean',

    'binary',    # not supported
    'list',      # not supported
    'record'     # not supported
]


def expect_col_starts_with(
    pattern: str, 
    col_type: list[ColTypes] | ColTypes | None,
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if columns in a Pbip object start
    with the specified pattern and have a supported data type.

    Parameters
    ----------
    pattern : str
        The pattern to match against the column name.
    col_type : list[ColTypes] | ColTypes | None
        The data type(s) to check for.
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if columns in a Pbip object start
        with the specified pattern and have a supported data type.
    """
    not_supported = ['binary', 'list', 'record', 'time', 'percentage', 'duration'] 
    
    if col_type and not isinstance(col_type, list):
        col_type = [col_type]

    if col_type:
        for col in col_type:
            if col in not_supported:
                Warning(f"Col type '{col}' is not supported. I'll ignore this type.")
        col_type = [x for x in col_type if x not in not_supported]

    def function(pbip: Pbip) -> list[ExpectMessage]:
        """
        Checks if columns in each table of the Pbip object start with a specified pattern
        and match any of the specified data types.

        Args:
            pbip (Pbip): The Pbip object containing tables and columns to check.

        Returns:
            list[ExpectMessage]: A list of messages detailing any columns that do not meet the criteria.
        """
        tables = pbip.tables
        checks = []
        for table in tables:
            table_name = table['name']
            cols = pbip.get_table_field(table_name, 'columns')
            if not cols:
                continue
            for col in cols:
                col_name = col['name']
                check_type = col_type is None or col['dataType'] in col_type
                if check_type and not col_name.startswith(pattern):
                    checks.append({
                        'expect': 'expect_col_starts_with',
                        'state': state,
                        'message': f"Column '{col_name}' in table '{table_name}' must start with '{pattern}'"
                    })
        return checks

    return function

def expect_measure_starts_with(
    pattern: str, 
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if measures in a Pbip object start
    with the specified pattern.

    Parameters
    ----------
    pattern : str
        The pattern to match against the measure name.
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if measures in a Pbip object start
        with the specified pattern.
    """
    
    def function(pbip: Pbip) -> list[ExpectMessage]:
        tables = pbip.tables
        checks = []
        for table in tables:
            table_name = table['name']
            measures = pbip.get_table_field(table_name, 'measures')
            if not measures:
                continue
            for measure in measures:
                measure_name = measure['name']
                if not measure_name.startswith(pattern):
                    checks.append({
                        'expect': 'expect_measure_starts_with',
                        'state': state,
                        'message': f"Measure '{measure_name}' in table '{table_name}' must start with '{pattern}'",
                    })
        return checks
    return function

def expect_table_starts_with(
    pattern: str, 
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if table names in a Pbip object start
    with the specified pattern.

    Parameters
    ----------
    pattern : str
        The pattern to match against the table name.
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if table names in a Pbip object start
        with the specified pattern.
    """
    def function(pbip: Pbip) -> list[ExpectMessage]:
        tables = pbip.tables
        checks = []
        for table in tables:
            table_name = table['name']
            if not table_name.startswith(pattern):
                checks.append({
                    'expect': 'expect_table_starts_with',
                    'state': state,
                    'message': f"Table '{table_name}' must start with '{pattern}'",
                })
        return checks
    return function

def expect_cols_in_relationship_has_same_type(
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if columns in relationships of a Pbip object have the same type.

    Parameters
    ----------
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if columns in relationships of a Pbip object have the same type.
    """
    def function(pbip: Pbip) -> list[ExpectMessage]:
        checks = []
        relationships = pbip.relationships
        for relationship in relationships:
            from_column = relationship['fromColumn']
            from_table = relationship['fromTable']
            to_column = relationship['toColumn']
            to_table = relationship['toTable']

            from_table_column = pbip.get_table_column(from_table, from_column)
            to_table_column = pbip.get_table_column(to_table, to_column)

            if from_table_column and to_table_column:
                from_column_type = from_table_column['dataType']
                to_column_type = to_table_column['dataType']

                if from_column_type != to_column_type:
                    checks.append({
                        'expect': 'expect_cols_in_relationship_has_same_type',
                        'state': state,
                        'message': dedent(f"""
                            Column '{from_column}' in table '{from_table}' and '{to_column}' in table '{to_table}' must have the same type.
                            But I found '{from_column}' with '{from_column_type}' type and '{to_column}' with '{to_column_type}' type.
                        """).strip()
                    })
        return checks
    return function

def expect_table_name_no_spaces(
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if table names in a Pbip object do not contain spaces.

    Parameters
    ----------
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if table names in a Pbip object do not contain spaces.
    """
    
    def function(pbip: Pbip) -> list[ExpectMessage]:
        tables = pbip.tables
        checks = []
        for table in tables:
            table_name = table['name']
            if ' ' in table_name:
                checks.append({
                    'expect': 'expect_table_name_no_spaces',
                    'state': state,
                    'message': f"Table '{table_name}' must not contain spaces",
                })
        return checks
    return function

def expect_dax_lines_length(
    max_length: int,
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if DAX measures in a Pbip object do not exceed the specified maximum length.

    Parameters
    ----------
    max_length : int
        The maximum length of a DAX measure.
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if DAX measures in a Pbip object do not exceed the specified maximum length.
    """
    def function(pbip: Pbip) -> list[ExpectMessage]:
        tables = pbip.tables
        checks = []
        for table in tables:
            table_name = table['name']
            measures = pbip.get_table_field(table_name, 'measures')
            if not measures:
                continue
            for measure in measures:
                measure_name = measure['name']
                expression = measure['expression']
                lines = check_lines_max_length(expression, max_length)
                text = smart_join([x[0] for x in lines])
                if any([x[1] for x in lines]):
                    checks.append({
                        'expect': 'expect_dax_lines_length',
                        'state': state,
                        'message': f"Measure '{measure_name}' in table '{table_name}' has line(s) {text} longer than {max_length} characters",
                    })
        return checks
    return function

def expect_m_lines_length(
    max_length: int,
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if M language expressions in the partitions
    of tables within a Pbip object do not exceed the specified maximum length.

    Parameters
    ----------
    max_length : int
        The maximum length of a line in an M language expression.
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if M language expressions in the partitions
        of tables within a Pbip object do not exceed the specified maximum length.
    """
    def function(pbip: Pbip) -> list[ExpectMessage]:
        tables = pbip.tables
        checks = []
        for table in tables:
            table_name = table['name']
            partitions = pbip.get_table_field(table_name, 'partitions')
            if not partitions:
                continue
            for partition in partitions:
                expression = partition['expression']
                lines = check_lines_max_length(expression, max_length)
                text = text = smart_join([x[0] for x in lines])
                if any([x[1] for x in lines]):
                    checks.append({
                        'expect': 'expect_m_lines_length',
                        'state': state,
                        'message': f"Source code of table '{table_name}' has line(s) {text} longer than {max_length} characters",
                    })
        return checks
    return function

def expect_measures_in_specific_table(
    table_name: str,
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if measures in a Pbip object are in a specific table.

    Parameters
    ----------
    table_name : str
        The name of the table where measures should be.
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if measures in a Pbip object are in a specific table.
    """
    def function(pbip: Pbip) -> list[ExpectMessage]:
        tables = pbip.tables
        checks = []
        tables_with_measures = []
        for table in tables:
            measures = pbip.get_table_field(table['name'], 'measures')
            if measures:
                tables_with_measures.append(table['name'])
        invalid_tables = [
            table
            for table in tables_with_measures
            if table != table_name
        ]
        if invalid_tables:
            checks.append({
                'expect': 'expect_measures_in_specific_table',
                'state': state,
                'message': f"Measures must be in table '{table_name}' but found in table(s) {smart_join(invalid_tables)}",
            })
        return checks
    return function

def expect_no_calculated_columns(
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if calculated columns are not present in any table of a Pbip object.

    Parameters
    ----------
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if calculated columns are not present in any table of a Pbip object.
    """
    def function(pbip: Pbip) -> list[ExpectMessage]:
        tables = pbip.tables
        checks = []
        for table in tables:
            columns = []
            table_name = table['name']
            table_columns = pbip.get_table_field(table_name, 'columns')
            if table_columns is None:
                continue
            for column in table_columns:
                if column['calculated']:
                    columns.append(column['name'])
            if columns:
                checks.append({
                    'expect': 'expect_no_calculated_columns',
                    'state': state,
                    'message': f"Table '{table_name}' has calculated columns: {smart_join(columns)}",
                })
        return checks
    return function

def expect_all_relationships_active(
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if all relationships in a Pbip object are active.

    Parameters
    ----------
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if all relationships in a Pbip object are active.
    """

    def function(pbip: Pbip) -> list[ExpectMessage]:
        relationships = pbip.relationships
        if not relationships:
            return []
        checks = []
        for relationship in relationships:
            from_table = relationship['fromTable']
            to_table = relationship['toTable']
            from_column = relationship['fromColumn']
            to_column = relationship['toColumn']
            if not relationship['isActive']:
                checks.append({
                    'expect': 'expect_all_relationships_active',
                    'state': state,
                    'message': (f"Relationship between '{from_table}.{from_column}' and '{to_table}.{to_column}' must be active."),
                })
        return checks
    return function

def expect_no_calculated_tables(
    state: ExpectState = 'Warning'
) -> Callable:
    """
    Returns a function that checks if calculated tables are not present in a Pbip object.

    Parameters
    ----------
    state : ExpectState, optional
        The state of the expectation, defaults to 'Warning'.

    Returns
    -------
    Callable
        A function that checks if calculated tables are not present in a Pbip object.
    """
    def function(pbip: Pbip) -> list[ExpectMessage]:
        tables = pbip.tables
        checks = []
        for table in tables:
            if table['partitions'][0]['type'] == 'calculated':
                checks.append({
                    'expect': 'expect_no_calculated_tables',
                    'state': state,
                    'message': f"Table '{table['name']}' is calculated",
                })
        return checks
    return function
