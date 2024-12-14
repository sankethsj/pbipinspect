
import deepdiff
from pathlib import Path
from pbipinspect.tmsl import (
    build_tmsl_path, 
    clean_tmsl_columns,
    clean_tmsl_measures,
    clean_tmsl_partitions,
    clean_tmsl_relationships,
    clean_tmsl_tables,
    is_TMSL, 
)

def test_build_tmsl_path(tmpdir):
    semantic_model_path = str(tmpdir)
    expected_path = Path(semantic_model_path) / 'model.bim'
    assert build_tmsl_path(semantic_model_path) == expected_path

def test_is_TMSL_false(tmpdir):
    assert is_TMSL(tmpdir) is False

def test_is_TMSL_true(tmpdir):
    Path(str(tmpdir)).joinpath('model.bim').write_text('')
    assert is_TMSL(tmpdir) is True

def test_clean_tmsl_columns_empty():
    assert clean_tmsl_columns([]) == []

def test_clean_tmsl_columns_not_empty():
    columns = [
        {
            "name": "column1",
            "isHidden": True,
            "annotations": [
                {
                "name": "SummarizationSetBy",
                "value": "Automatic"
                }
            ],
            "dataType": "double",
            "isNameInferred": True,
            "lineageTag": "fake_lineage1",
            "sourceColumn": "column1",
            "summarizeBy": "none"
        },
        {
            "name": "column2",
            "expression": "[column1]",
            "annotations": [
                {
                "name": "SummarizationSetBy",
                "value": "Automatic"
                }
            ],
            "dataType": "string",
            "lineageTag": "fake_lineage2",
            "sourceColumn": "[column1]",
            "summarizeBy": "none"
        }
    ]
    expected_result = [
        {
            "name": "column1",
            "expression": "",
            "isHidden": True,
            "annotations": [
                {
                "name": "SummarizationSetBy",
                "value": "Automatic"
                }
            ],
            "dataType": "double",
            "isNameInferred": True,
            "lineageTag": "fake_lineage1",
            "sourceColumn": "column1",
            "summarizeBy": "none",
            "calculated": False
        },
        {
            "name": "column2",
            "expression": "[column1]",
            "isHidden": False,
            "isNameInferred": False,
            "annotations": [
                {
                "name": "SummarizationSetBy",
                "value": "Automatic"
                }
            ],
            "dataType": "string",
            "lineageTag": "fake_lineage2",
            "summarizeBy": "none",
            "sourceColumn": "[column1]",
            "calculated": True
        }
    ]
    result = clean_tmsl_columns(columns)
    assert deepdiff.DeepDiff(result, expected_result, ignore_order=True) == {}

def test_clean_tmsl_partitions():
    partitions = [
        {
            "name": "habitos",
            "mode": "import",
            "source": {
              "expression": [
                  "let ",
                  "a = 1 + 1 ",
                  "in a"
              ],
              "type": "m"
            }
        }
    ]
    expected_result = [
        {
            "name": "habitos",
            "type": "m",
            "mode": "import",
            "expression": "let a = 1 + 1 in a"
        }
    ]
    result = clean_tmsl_partitions(partitions)
    assert deepdiff.DeepDiff(result, expected_result, ignore_order=True) == {}

def test_clean_tmsl_measures_empty():
    assert clean_tmsl_measures([]) == []

def test_clean_tmsl_measures_not_empty():
    measures = [
        {
            "name": "despesa",
            "annotations": [
              {
                "name": "PBI_FormatHint",
                "value": "{\"currencyCulture\":\"pt-BR\"}"
              }
            ],
            "displayFolder": "folder1",
            "expression": "1 + 1",
            "formatString": "\"R$\"\\ #,0.00;-\"R$\"\\ #,0.00;\"R$\"\\ #,0.00",
            "lineageTag": "fake_lineage1"
          },
          {
            "name": "receita",
            "displayFolder": "folder2",
            "expression": "var = 1 + 1\nreturn var",
            "lineageTag": "fake_lineage2"
          }
    ]
    expected_result = [
        {
            "name": "despesa",
            "annotations": [
              {
                "name": "PBI_FormatHint",
                "value": "{\"currencyCulture\":\"pt-BR\"}"
              }
            ],
            "displayFolder": "folder1",
            "expression": "1 + 1",
            "formatString": "\"R$\"\\ #,0.00;-\"R$\"\\ #,0.00;\"R$\"\\ #,0.00",
            "lineageTag": "fake_lineage1"
          },
          {
            "name": "receita",
            "annotations": None,
            "displayFolder": "folder2",
            "expression": "var = 1 + 1\nreturn var",
            "lineageTag": "fake_lineage2",
            "formatString": None
          }
    ]
    result = clean_tmsl_measures(measures)
    assert deepdiff.DeepDiff(result, expected_result, ignore_order=True) == {}

def test_clean_tmsl_tables():
    table = [
        {
            "name": "table1",
            "lineageTag": "fake_lineage1",
            "columns": [
                {
                    "name": "column1",
                    "dataType": "double",
                    "lineageTag": "fake_lineage1",
                    "sourceColumn": "column1",
                    "summarizeBy": "none"
                }
            ],
            "measures": [
                {
                    "name": "measure1",
                    "displayFolder": "folder1",
                    "expression": "1 + 1",
                    "lineageTag": "fake_lineage1"
                }
            ],
            "partitions": [
                {
                    "name": "partition1",
                    "mode": "import",
                    "source": {
                      "expression": "let a = 1 + 1 in a",
                      "type": "m"
                    }
                }
            ]
        }
    ]
    expected_result = [
        {
            "name": "table1",
            "lineageTag": "fake_lineage1",
            "columns": [
                {
                    "name": "column1",
                    "expression": "",
                    "isHidden": False,
                    "annotations": None,
                    "isNameInferred": False,
                    "dataType": "double",
                    "lineageTag": "fake_lineage1",
                    "sourceColumn": "column1",
                    "summarizeBy": "none",
                    "calculated": False
                }
            ],
            "measures": [
                {
                    "name": "measure1",
                    "displayFolder": "folder1",
                    "expression": "1 + 1",
                    "lineageTag": "fake_lineage1",
                    "formatString": None,
                    "annotations": None
                }
            ],
            "partitions": [
                {
                    "name": "partition1",
                    "mode": "import",    
                    "expression": "let a = 1 + 1 in a",
                    "type": "m"
                }
            ],
            "isHidden": False,
            "isPrivate": False
        }
    ]
    result = clean_tmsl_tables(table)
    assert deepdiff.DeepDiff(result, expected_result, ignore_order=True) == {}

def test_clean_tmsl_relationships():
    relationships = [
        {
            "name": "relationship1",
            "fromColumn": "column1",
            "fromTable": "table1",
            "joinOnDateBehavior": "datePartOnly",
            "toColumn": "column2",
            "toTable": "table2"
        }
    ]
    expected_result = [
        {
            "name": "relationship1",
            "fromColumn": "column1",
            "fromTable": "table1",
            "toColumn": "column2",
            "toTable": "table2",
            "crossFilteringBehavior": 'singleDirection',
            "toCardinality": "oneToMany",
            "isActive": True
        }
    ]
    result = clean_tmsl_relationships(relationships)
    assert deepdiff.DeepDiff(result, expected_result, ignore_order=True) == {}
