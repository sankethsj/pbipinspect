# pbipinspect

Parse, validate and document your Power BI Project

## Installation

```
pip install pbipinspect
```

## Usage

This library transforms your Power BI project into a structured and validated state. It provides a set of tools to analyze, validate, and document your project.

First, you need to create an inspect object. The `create_inspect` function takes a path to your project and returns a `PbipInspect` object. You can also instantiate the object directly using the PbipInspect class, but using `create_inspect` is recommended.

```python
>>> from pbipinspect import create_inspect
>>> inspect = create_inspect('your-project.pbip')
```

Inspect parse you Power BI Project and gives you the ability to validate and document it. ou can view the model generated from your project by accessing the `pbip.model` attribute.
```python
>>> print(inspect.pbip.model)
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
    'relationships': [{...}],
    'expressions': [{...}]
}}
```

### Expectations

Now, it's possible to validate your project. pbipinspect already comes with some expects that you can use to validate your project.

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

### Building documentation

Additionally, you can generate documentation for your project using the `build_report` method.
```python
>>> report = inspect.build_report()
```

By default, this approach will create a report using the default template. However, you can change the template and the variables by specifying the `report_template` and `render` parameters.

You can also use the `add_metadata` method to include metadata in your report. This metadata will be displayed at the top of the report in the "Overview" section. Therefore, metadata should be used to provide information about your project, such as its name, description, author, etc.

```python
>>> inspect.add_metadata({
...     'name': 'Project name',
...     'description': 'Project description',
...     'author': 'Author'
... })
>>> report = inspect.build_report()
```

### Tables, columns and measures descriptions

pbipinspect introduces a method for generating descriptions for tables, columns, and measures. In your Power BI project, you can add a comment in the source code of a table following this pattern:

```m
/* @doc 
Table description

@col column1:
column1 description

@col column2:
column2 description
*/
let
    Source = Table.FromRecords({
        [column1 = 1, column2 = 2]
    }),
    #"Changed Type" = Table.TransformColumnTypes(
      Source,
      {{"col1", number}, {"col2", number}}
    )
in
    #"Changed Type"
```

The same pattern can be used for measures:
```dax
/* @doc 
Measure description
*/
var = 1
return var + 1
```

These descriptions are added to the "description" field of each corresponding property in the parsed model.

## The model

The `pbip.model` field of the `PbipInspect` object contains the parsed model of your Power BI Project.
Currently, the model contains the following fields:

```json
{
  "type": "object",
  "properties": {
    "model": {
      "type": "object",
      "properties": {
        "tables": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "lineageTag": { "type": "string" },
              "isHidden": { "type": "boolean" },
              "isPrivate": { "type": "boolean" },
              "columns": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "name": { "type": "string" },
                    "expression": { "type": "string" },
                    "isHidden": { "type": "boolean" },
                    "isNameInferred": { "type": "boolean" },
                    "dataType": { "type": "string" },
                    "lineageTag": { "type": "string" },
                    "summarizeBy": { "type": "string" },
                    "sourceColumn": { "type": "string" },
                    "annotations": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "name": { "type": "string" },
                          "value": { "type": "string" }
                        }
                      }
                    },
                    "calculated": { "type": "boolean" },
                    "description": { "type": "string" }
                  }
                }
              },
              "measures": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "name": { "type": "string" },
                    "lineageTag": { "type": "string" },
                    "annotations": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "name": { "type": "string" },
                          "value": { "type": "string" }
                        }
                      }
                    },
                    "displayFolder": { "type": "string" },
                    "expression": { "type": "string" },
                    "formatString": { "type": "string" },
                    "description": { "type": "string" },
                    "references": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "type": { "type": "string" },
                          "name": { "type": "string" },
                          "column": { "type": "string" }
                        }
                      }
                    }
                  }
                }
              },
              "partitions": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "name": { "type": "string" },
                    "type": { "type": "string" },
                    "mode": { "type": "string" },
                    "raw_expression": { "type": "string" },
                    "expression": { "type": "string" },
                    "description": { "type": "string" }
                  }
                }
              }
            }
          }
        },
        "relationships": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "fromTable": { "type": "string" },
              "fromColumn": { "type": "string" },
              "toTable": { "type": "string" },
              "toColumn": { "type": "string" },
              "crossFilteringBehavior": { "type": "string" },
              "filteringSymbol": { "type": "string" },
              "fromCardinalitySymbol": { "type": "string" },
              "toCardinalitySymbol": { "type": "string" },
              "isActive": { "type": "boolean" }
            }
          }
        },
        "expressions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "lineageTag": { "type": "string" },
              "type": { "type": "string" },
              "expression": { "type": "string" },
              "description": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

## Getting help

If you encounter a clear bug, please file an issue with a minimal reproducible example on GitHub.
