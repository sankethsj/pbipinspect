# pbipinspect

Parse, validate and document your Power BI Project

## Installation

```
pip install pbipinspect
```

## Usage

This library brings your Power BI project to a structured and validated state. It provides a set of tools to analyze, validate, and document your project.

First, you need to create a inspect. The `create_inspect` function takes a path to your project and returns a `PbipInspect` object. You can create directly with `PbipInspect` class, but `create_inspect` is recommended.

```python
>>> from pbipinspect import create_inspect
>>> inspect = create_inspect('your-project.pbip')
```

Inspect parse you Power BI Project and gives you the ability to validate and document it. You can see the model generated from your project acessing the attribute `model`.
```python
>>> print(inspect.model)
{'model': {
    'tables': [{
        'name': 'table',
        'lineageTag': 'id',
        'columns': [{...}],
        'measures': [{...}],
        'partitions': [{...}],
        'isHidden': False,
        'annotations': [{...}]
    }],
    'relationships': [{...}]
}}
```

Now, it's possible to validate your project. This is possible thanks to expects. Pbipinspect already comes with some expects that you can use to validate your project.

```python
>>> from pbipinspect.expectations import *
>>> inspect.expectations(steps=[
...     expect_col_starts_with(col_type='dateTime', pattern='dt_', state='Info'),
...     expect_measure_starts_with(pattern='m_'),
...     expect_table_starts_with(pattern='t_'),
...     expect_table_name_no_spaces(),
...     expect_cols_in_relationship_has_same_type(),
...     expect_dax_lines_length(max_length=60),
...     expect_m_lines_length(max_length=60),
...     expect_measures_in_specific_table('_measures'),
...     expect_no_calculated_columns(state='Error'),
...     expect_all_relationships_active()
>>> ])
>>> inspect.run_expectations()
>>> print(inspect.expects)
[{'expect': 'expect_col_starts_with',
   'state': 'Warning',
   'message': "Column 'Column1' in table 'Table1' must start with 'dt_'"},
 {'expect': 'expect_no_calculated_columns',
  'state': 'Error',
  'message': "Table 'Table1' has calculated columns: 'Column2' and 'Column3'"}
]
```

## Getting help

If you encounter a clear bug, please file an issue with a minimal reproducible example on GitHub.