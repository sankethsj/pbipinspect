
from pbipinspect.inspect import PbipInspect

def test_parse_relationships_to_mermaid_empty_relationships():
    content = {'relationships': []}
    result = PbipInspect.parse_relationships_to_mermaid(content)
    assert result == 'flowchart LR'

def test_parse_relationships_to_mermaid_single_relationship():
    content = {
        'relationships': [
            {
                'fromTable': 'Table1',
                'fromColumn': 'Column1',
                'toTable': 'Table2',
                'toColumn': 'Column2',
                'crossFilteringBehavior': 'singleDirection',
                'filteringSymbol': '<',
                'fromCardinalitySymbol': '*',
                'toCardinalitySymbol': '1'
            }
        ]
    }
    result = PbipInspect.parse_relationships_to_mermaid(content)
    mermaid = """flowchart LR
subgraph s1["Table1"]
n1["Column1"]
end
subgraph s2["Table2"]
n2["Column2"]
end
n1 -- \\* < 1 --- n2"""
    assert result == mermaid

def test_parse_relationships_to_mermaid_multiple_relationships():
    content = {
        'relationships': [
            {
                'fromTable': 'Table1',
                'fromColumn': 'Column1',
                'toTable': 'Table2',
                'toColumn': 'Column2',
                'crossFilteringBehavior': 'singleDirection',
                'filteringSymbol': '<',
                'fromCardinalitySymbol': '*',
                'toCardinalitySymbol': '1'
            },
            {
                'fromTable': 'Table3',
                'fromColumn': 'Column3',
                'toTable': 'Table4',
                'toColumn': 'Column4',
                'crossFilteringBehavior': 'singleDirection',
                'filteringSymbol': '<',
                'fromCardinalitySymbol': '*',
                'toCardinalitySymbol': '1'
            }
        ]
    }
    result = PbipInspect.parse_relationships_to_mermaid(content)
    mermaid = """flowchart LR
subgraph s1["Table1"]
n1["Column1"]
end
subgraph s2["Table2"]
n2["Column2"]
end
subgraph s3["Table3"]
n3["Column3"]
end
subgraph s4["Table4"]
n4["Column4"]
end
n1 -- \\* < 1 --- n2
n3 -- \\* < 1 --- n4"""
    assert result == mermaid

def test_parse_relationships_to_mermaid_multiple_relationships_same_table():
    content = {
        'relationships': [
            {
                'fromTable': 'Table1',
                'fromColumn': 'Column1',
                'toTable': 'Table2',
                'toColumn': 'Column2',
                'crossFilteringBehavior': 'singleDirection',
                'filteringSymbol': '<',
                'fromCardinalitySymbol': '*',
                'toCardinalitySymbol': '1'
            },
            {
                'fromTable': 'Table3',
                'fromColumn': 'Column3',
                'toTable': 'Table1',
                'toColumn': 'Column2',
                'crossFilteringBehavior': 'singleDirection',
                'filteringSymbol': '<',
                'fromCardinalitySymbol': '*',
                'toCardinalitySymbol': '1'
            }
        ]
    }
    result = PbipInspect.parse_relationships_to_mermaid(content)
    mermaid = """flowchart LR
subgraph s1["Table1"]
n1["Column1"]
n2["Column2"]
end
subgraph s2["Table2"]
n3["Column2"]
end
subgraph s3["Table3"]
n4["Column3"]
end
n1 -- \\* < 1 --- n3
n4 -- \\* < 1 --- n2"""
    assert result == mermaid

def test_parse_relationships_to_mermaid_multiple_relationships_both_directions():
    content = {
        'relationships': [
            {
                'fromTable': 'Table1',
                'fromColumn': 'Column1',
                'toTable': 'Table2',
                'toColumn': 'Column2',
                'crossFilteringBehavior': 'bothDirections',
                'filteringSymbol': '<>',
                'fromCardinalitySymbol': '*',
                'toCardinalitySymbol': '1'
            }
        ]
    }
    result = PbipInspect.parse_relationships_to_mermaid(content)
    mermaid = """flowchart LR
subgraph s1["Table1"]
n1["Column1"]
end
subgraph s2["Table2"]
n2["Column2"]
end
n1 -- \\* <> 1 --- n2"""
    assert result == mermaid