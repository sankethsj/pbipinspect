
from pathlib import Path
from pbipinspect.pbip import (
    is_pbip_file,
    find_pbip_file,
    get_pbip_name,
    get_component_path,
    Pbip
)
import pytest

def test_is_pbip_file_with_valid_extension():
    assert is_pbip_file('test.pbip') == True

def test_is_pbip_file_pbip_with_invalid_extension():
    assert is_pbip_file('test.txt') == False

def test_find_pbip_file_single_file(tmp_path):
    pbip_file = tmp_path / 'example.pbip'
    pbip_file.touch()
    assert find_pbip_file(tmp_path) == [pbip_file]

def test_find_pbip_file_multiple_files(tmp_path):
    pbip_file1 = tmp_path / 'example1.pbip'
    pbip_file1.touch()
    pbip_file2 = tmp_path / 'example2.pbip'
    pbip_file2.touch()
    assert find_pbip_file(tmp_path) == [pbip_file1, pbip_file2]

def test_find_pbip_file_no_files(tmp_path):
    assert find_pbip_file(tmp_path) == []

def test_find_pbip_file_non_existent_directory():
    find_pbip_file('/non/existent/directory') == []

def test_get_pbip_name_string_path():
    path = "file.pbip"
    assert get_pbip_name(path) == "file"

def test_get_pbip_name_path_object():
    path = Path("file.pbip")
    assert get_pbip_name(path) == "file"

def test_get_pbip_name_single_dot():
    path = "file.pbip"
    assert get_pbip_name(path) == "file"

def test_get_pbip_name_multiple_dots():
    path = "file.name.pbip"
    assert get_pbip_name(path) == "file.name"

def test_get_component_path_string_path():
    path = "example.pbip"
    component = "Report"
    expected = Path("example.Report")
    assert get_component_path(path, component) == expected

def test_get_component_path_path_object():
    path = Path("example.pbip")
    component = "Report"
    expected = Path("example.Report")
    assert get_component_path(path, component) == expected

def test_get_component_path_multiple_dots():
    path = "example.name.pbip"
    component = "Report"
    expected = Path("example.name.Report")
    assert get_component_path(path, component) == expected

def test_getitem_key_exists():
    model = {'key': 'value'}
    pbip = Pbip(model)
    assert pbip['key'] == 'value'

def test_getitem_key_invalid():
    model = {}
    pbip = Pbip(model)
    with pytest.raises(KeyError):
        pbip[None]

@pytest.fixture
def pbip():
    model = {
        'model': {
            'tables': [
                {
                    'name': 'Table1',
                    'columns': [{'name': 'Column1'}, {'name': 'Column2'}],
                    'measures': [{'name': 'Measure1'}]
                },
                {
                    'name': 'Table2',
                    'columns': [{'name': 'Column1'}, {'name': 'Column2'}],
                    'measures': [{'name': 'Measure1'}]
                }
            ]
        }
    }
    return Pbip(model)

def test_pbip_get_table_field_existing_table_and_field(pbip):
    result = pbip.get_table_field('Table1', 'columns')
    assert result == [{'name': 'Column1'}, {'name': 'Column2'}]

def test_pbip_get_table_field_non_existent_table(pbip):
    result = pbip.get_table_field('Invalid', 'columns')
    assert result is None

def test_pbip_get_table_field_non_existent_field(pbip):
    result = pbip.get_table_field('Table1', 'non_existent_field')
    assert result is None

def test_pbip_get_table_column_column_exists(pbip):
    result = pbip.get_table_column('Table1', 'Column1')
    assert result == {'name': 'Column1'}

def test_pbip_get_table_column_column_does_not_exist(pbip):
    result = pbip.get_table_column('Table1', 'Column3')
    assert result is None

def test_pbip_get_table_column_table_does_not_exist(pbip):
    result = pbip.get_table_column('Table3', 'Column1')
    assert result is None

def test_pbip_get_table_measure_found_in_table(pbip):
    assert pbip.get_table_measure('Table1', 'Measure1') == {'name': 'Measure1'}

def test_pbip_get_table_measure_not_found_in_table(pbip):
    assert pbip.get_table_measure('Table1', 'Measure2') is None

def test_pbip_get_table_table_not_found(pbip):
    assert pbip.get_table_measure('Table3', 'Measure1') is None
