
from pbipinspect.pbip import Pbip
import pytest


@pytest.fixture
def pbip_expect_col_starts_with():
    return Pbip({
        'model': {
            'tables': [
                {
                    'name': 'Table1', 
                    'columns': [{'name': 'Col1', 'dataType': 'string'}]
                },
                {
                    'name': 'Table2', 
                    'columns': [{'name': 'Col2', 'dataType': 'int64'}]
                }
            ]
        }
    })

@pytest.fixture
def pbip_expect_measure_starts_with():
    return Pbip({
        'model': {
            'tables': [
                {
                    'name': 'Table1', 
                    'measures': [{'name': 'Measure1'}]
                },
                {
                    'name': 'Table2', 
                    'measures': [{'name': 'Measure2'}]
                }
            ]
        }
    })

@pytest.fixture
def pbip_expect_table_starts_with():
    return Pbip({
        'model': {
            'tables': [
                {
                    'name': 'Table1'
                },
                {
                    'name': 'Table2'
                }
            ]
        }
    })

@pytest.fixture
def pbip_expect_cols_in_relationship_has_same_type():
    return {
        'correct': Pbip({
            'model': {
                'tables': [
                    {'name': 'table1', 'columns': [{'name': 'col1', 'dataType': 'string'}]},
                    {'name': 'table2', 'columns': [{'name': 'col2', 'dataType': 'string'}]}
                ],
                'relationships': [
                    {'fromTable': 'table1', 'fromColumn': 'col1', 'toTable': 'table2', 'toColumn': 'col2'}
                ]
            }
        }),
        'incorrect': Pbip({
            'model': {
                'tables': [
                    {'name': 'table1', 'columns': [{'name': 'col1', 'dataType': 'string'}]},
                    {'name': 'table2', 'columns': [{'name': 'col2', 'dataType': 'int64'}]}
                ],
                'relationships': [
                    {'fromTable': 'table1', 'fromColumn': 'col1', 'toTable': 'table2', 'toColumn': 'col2'}
                ]
            }
        })
    }

@pytest.fixture
def pbip_expect_table_name_no_spaces():
    return Pbip({
        'model': {
            'tables': [
                {'name': 'Table1'},
                {'name': 'Table2'}
            ]
        }
    })

@pytest.fixture
def pbip_expect_dax_lines_length():
    return Pbip({
        'model': {
            'tables': [
                {'name': 'Table1', 'measures': [{'name': 'Measure1', 'expression': 'short expression'}]},
                {'name': 'Table2', 'measures': [{'name': 'Measure2', 'expression': 'long expression that exceeds the max length'}]}
            ]
        }
    })

@pytest.fixture
def pbip_expect_m_lines_length():
    return Pbip({
        'model': {
            'tables': [
                {'name': 'Table1', 'partitions': [{'expression': 'short expression'}]},
                {'name': 'Table2', 'partitions': [{'expression': 'long expression that exceeds the max length'}]}
            ]
        }
    })

@pytest.fixture
def pbip_expect_measures_in_specific_table():
    return {
        'correct': Pbip({
            'model': {
                'tables': [
                    {'name': 'Table1', 'measures': [{'name': 'Measure1'}]},
                    {'name': 'Table2', 'measures': []}
                ]
            }
         }),
        'incorrect': Pbip({
            'model': {
                'tables': [
                    {'name': 'Table1', 'measures': [{'name': 'Measure1'}]},
                    {'name': 'Table2', 'measures': [{'name': 'Measure2'}]}
                ]
            }
        })
    }

@pytest.fixture
def pbip_expect_no_calculated_columns():
    return Pbip({
        'model': {
            'tables': [
                {'name': 'Table1', 'columns': [{'name': 'Col1', 'calculated': False}]},
                {'name': 'Table2', 'columns': [{'name': 'Col2', 'calculated': True}]}
            ]
        }
    })

@pytest.fixture
def pbip_expect_all_relationships_active():
    return Pbip({
        'model': {
            'tables': [
                {'name': 'Table1', 'columns': [{'name': 'Col1'}]},
                {'name': 'Table2', 'columns': [{'name': 'Col2'}]}
            ],
            'relationships': [
                {'fromTable': 'Table1', 'fromColumn': 'Col1', 'toTable': 'Table2', 'toColumn': 'Col2', 'isActive': True},
                {'fromTable': 'Table1', 'fromColumn': 'Col1', 'toTable': 'Table2', 'toColumn': 'Col2', 'isActive': False}
            ]
        }
    })