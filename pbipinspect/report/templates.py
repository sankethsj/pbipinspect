
DEFAULT_TEMPLATE = """
{% if metadata -%}- [Overview](#Overview){% endif %}
- [Expectations](#Expectations)
- [Model](#Model)
    - [Relationships](#Relationships)
    - [Expressions](#Expressions)
    - [Tables](#Tables)
        | Table name | Source code | Columns | Measures |
        | ---------- | ----------- | ------- | -------- |
    {%- for table in tables %}
        | [{{ table.name }}](#{{ sanitize_id(table.name) }}) |[Source code](#source-code-{{ sanitize_id(table.name) }}) | [Columns](#columns-{{ sanitize_id(table.name) }}) | [Measures](#measures-{{ sanitize_id(table.name) }}) |
    {%- endfor %}

----
{% if metadata %}
# <span id="Overview">Overview</span>
{% for md in metadata %}
## {{ md }}
{{ metadata[md] }}
{% endfor %}
----
{% endif -%}

# <span id="Expectations">Expectations</span>
{% if expects %}
| State | Expect | Message |
| ----- | ------ | ------- |
{%- for expect in expects %}
| {{ expect.state }} | {{ expect.expect }} | {{ expect.message }} |
{%- endfor %}
{% endif %}
{% if not expects %}Without warnings or errors{% endif %}

----

# <span id="Model">Model</span>
## <span id="Relationships">Relationships</span>
```mermaid
---
config:
    layout: elk
---
{{ mermaid_relationships }}
```

## <span id="Tables">Tables</span>
{% for table in tables %}
### <span id="{{ sanitize_id(table.name) }}">{{ table.name }} {% if table.isHidden %}(Hidden){% endif %} {% if table.isPrivate %}(Private){% endif %}</span>
{{ table.partitions[0].description }}
#### <span id="source-code-{{ sanitize_id(table.name) }}">Source code</span>
```m
{{ table.partitions[0].expression }}
```
#### <span id="columns-{{ sanitize_id(table.name) }}">Columns</span>
{%- if table.columns %}
| Column | Description | Type | Calculated | Is hidden |
| ------ | ----------- | ---- | ---------- | --------- |
{%- for column in table.columns %}
| {{ column.name }} | {{ column.description }} | {{ column.dataType }} | {{ column.calculated }} | {{ column.isHidden }} |
{%- endfor %}
{% endif %}
{% if not table.columns %}No columns{% endif %}
#### <span id="measures-{{ sanitize_id(table.name) }}">Measures</span>
{% if not table.measures %}No measures{% endif %}
{%- if table.measures %}
{%- for measure in table.measures %}
##### <span id="{{ sanitize_id(table.name) }}-{{ sanitize_id(measure.name) }}">{{ measure.name }}</span>
Description: {{ measure.description }}

Display folder: {{ measure.displayFolder }}

Dependencies:
{% for reference in measure.references -%}
{%- if reference.type == 'table' -%}
- {{ reference.name }}[{{ reference.column }}]
{% endif %}
{%- if reference.type == 'measure' -%}
- [{{ reference.name }}]
{%- endif %}
{% endfor %}

Expression:
```dax
{{ measure.expression }}
```
{% endfor %}
{% endif %}
{% endfor %}

## <span id="Expressions">Expressions</span>
{% if not expressions %}No expressions{% endif %}
{%- if expressions %}
{%- for expression in expressions %}
### <span id="{{ sanitize_id(expression.name) }}">{{ expression.name }}</span>
{{ expression.description }}

Type: {{ expression.type }}
{% if expression.type == 'function' %}
```m
{{ expression.expression }}
```
{% endif %}
{% if expression.type == 'expression' %}
Value: {{ expression.expression }}
{% endif %}
{% endfor %}
{% endif %}
"""
