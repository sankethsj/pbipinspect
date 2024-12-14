
from pbipinspect.expectations import (
    expect_all_relationships_active,
    expect_col_starts_with,
    expect_cols_in_relationship_has_same_type,
    expect_dax_lines_length,
    expect_m_lines_length,
    expect_measure_starts_with,
    expect_measures_in_specific_table,
    expect_no_calculated_columns,
    expect_table_name_no_spaces,
    expect_table_starts_with
)
from pbipinspect.pbip import Pbip

# expect_col_starts_with -----------------------------------------------------
def test_expect_col_starts_with_single_column_type(pbip_expect_col_starts_with):
    func = expect_col_starts_with('Col', 'string')
    result = func(pbip_expect_col_starts_with)
    assert len(result) == 0

def test_expect_col_starts_with_multiple_column_types(pbip_expect_col_starts_with):
    func = expect_col_starts_with('Col', ['string', 'int64'])
    result = func(pbip_expect_col_starts_with)
    assert len(result) == 0

def test_expect_col_starts_with_unsupported_column_types(pbip_expect_col_starts_with):
    func = expect_col_starts_with('Col', ['binary', 'string'])
    result = func(pbip_expect_col_starts_with)
    assert len(result) == 0

def test_expect_col_starts_with_no_column_types(pbip_expect_col_starts_with):
    func = expect_col_starts_with('Col', None)
    result = func(pbip_expect_col_starts_with)
    assert len(result) == 0

def test_expect_col_starts_with_table_no_columns():
    pbip = Pbip({'model': {'tables': [{'name': 'Table1', 'columns': []}]}})
    func = expect_col_starts_with('Col', None)
    result = func(pbip)
    assert len(result) == 0

def test_expect_col_starts_with_not_match(pbip_expect_col_starts_with):
    func = expect_col_starts_with('Foo', 'string')
    result = func(pbip_expect_col_starts_with)
    assert len(result) == 1


# expect_measure_starts_with -------------------------------------------------
def test_expect_measure_starts_with(pbip_expect_measure_starts_with):
    checks = expect_measure_starts_with('Measure')(pbip_expect_measure_starts_with)
    assert len(checks) == 0

def test_expect_measure_starts_with_not_match(pbip_expect_measure_starts_with):
    checks = expect_measure_starts_with('test')(pbip_expect_measure_starts_with)
    assert len(checks) == 2


# expect_table_starts_with ---------------------------------------------------
def test_expect_table_starts_with_match(pbip_expect_table_starts_with):
    checks = expect_table_starts_with('Table')(pbip_expect_table_starts_with)
    assert len(checks) == 0

def test_expect_table_starts_with_not_match(pbip_expect_table_starts_with):
    checks = expect_table_starts_with('Foo')(pbip_expect_table_starts_with)
    assert len(checks) == 2

def test_expect_table_starts_with_empty_tables():
    pbip = Pbip({'model': {'tables': []}})
    checks = expect_table_starts_with('Foo')(pbip)
    assert len(checks) == 0


# expect_cols_in_relationship_has_same_type ----------------------------------
def test_expect_cols_in_relationship_has_same_type_no_relationships():
    pbip = Pbip({'model': {'tables': [], 'relationships': []}})
    func = expect_cols_in_relationship_has_same_type()
    result = func(pbip)
    assert len(result) == 0

def test_expect_cols_in_relationship_has_same_type_same_column_types(
    pbip_expect_cols_in_relationship_has_same_type
):
    pbip = pbip_expect_cols_in_relationship_has_same_type['correct']
    result = expect_cols_in_relationship_has_same_type()(pbip)
    assert len(result) == 0

def test_expect_cols_in_relationship_has_same_type_different_column_types(
    pbip_expect_cols_in_relationship_has_same_type
):
    pbip = pbip_expect_cols_in_relationship_has_same_type['incorrect']
    result = expect_cols_in_relationship_has_same_type()(pbip)
    assert len(result) == 1


# expect_table_name_no_spaces -----------------------------------------------
def test_expect_table_name_no_spaces_valid_tables(pbip_expect_table_name_no_spaces):
    result = expect_table_name_no_spaces()(pbip_expect_table_name_no_spaces)
    assert len(result) == 0

def test_expect_table_name_no_spaces_with_spaces():
    pbip = Pbip({'model': {'tables': [{'name': 'Table 1'}, {'name': 'Table 2'}]}})
    result = expect_table_name_no_spaces()(pbip)
    assert len(result) == 2


# expect_dax_lines_length ----------------------------------------------------
def test_expect_dax_lines_length_no_measures():
    pbip = Pbip({'model': {'tables': [{'name': 'Table1', 'measures': []}]}})
    result = expect_dax_lines_length(16)(pbip)
    assert result == []

def test_expect_dax_lines_length_exceeding_max_length(pbip_expect_dax_lines_length):
    result = expect_dax_lines_length(16)(pbip_expect_dax_lines_length)
    assert len(result) == 1


# expect_m_lines_length ----------------------------------------------------
def test_expect_expect_m_lines_length():
    pbip = Pbip({'model': {'tables': [{'name': 'Table1', 'measures': []}]}})
    result = expect_m_lines_length(16)(pbip)
    assert result == []

def test_expect_expect_m_lines_length_exceeding_max_length(pbip_expect_m_lines_length):
    result = expect_m_lines_length(16)(pbip_expect_m_lines_length)
    assert len(result) == 1


# expect_measures_in_specific_table -------------------------------------------
def test_expect_measures_in_specific_table_no_measures():
    pbip = Pbip({'model': {'tables': [{'name': 'Table1', 'measures': []}]}})
    result = expect_measures_in_specific_table('Table1')(pbip)
    assert result == []

def test_expect_measures_in_specific_table_incorrect_table(
    pbip_expect_measures_in_specific_table
):
    pbip = pbip_expect_measures_in_specific_table['incorrect']
    result = expect_measures_in_specific_table('Table1')(pbip)
    assert len(result) == 1

def test_expect_measures_in_specific_table_correct_table(
    pbip_expect_measures_in_specific_table
):
    pbip = pbip_expect_measures_in_specific_table['correct']
    result = expect_measures_in_specific_table('Table1')(pbip)
    assert len(result) == 0


# expect_no_calculated_columns -----------------------------------------------
def test_expect_no_calculated_columns_no_columns():
    pbip = Pbip({'model': {'tables': [{'name': 'Table1', 'columns': []}]}})
    result = expect_no_calculated_columns()(pbip)
    assert len(result) == 0

def test_expect_no_calculated_columns_with_calculated_columns(pbip_expect_no_calculated_columns):
    result = expect_no_calculated_columns()(pbip_expect_no_calculated_columns)
    assert len(result) == 1


# expect_all_relationships_active --------------------------------------------
def test_expect_all_relationships_active(
    pbip_expect_all_relationships_active
):
    result = expect_all_relationships_active()(pbip_expect_all_relationships_active)
    assert len(result) == 1

def text_expect_all_relationships_active_no_relationships():
    pbip = Pbip({'model': {'tables': [], 'relationships': []}})
    result = expect_all_relationships_active()(pbip)
    assert result == []
