# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-02-16

### Added
- Module `pbipinspect.parse` to parse Power BI models, including TMSL and TMDL
- Several functions to `pbipinspect.parse.utils` to parse TMSL and TMDL
- Module `pbipinspect.report` with templates for report generation
- Expressions (parameters and functions) added to model in `PbipInspect`. A new method `parse_tmdl_expressions` was added due to this
- Method `add_metadata` to the `PbipInspect` class to add metadata to the report. Metadata is used in default report template to provide overview section
- Method `parse_relationships_to_mermaid` to the `PbipInspect` class to parse relationships to mermaid format. The output is used in default report template
- Method `build_report` to the `PbipInspect` class to build a markdown report. This function also gives the possibility to use a custom template and render function
- New utilies functions `sanitize_id` and `fix_duplicate_ids` to `pbipinspect.utils`. These functions are used to create valid ids and fix duplicate ids in the report
- Property `expressions` to the `Pbip` class
- Method `get_fields` to the `Pbip` class to retrieve fields from tables based on the specified key
- `expect_no_calculated_tables` expectation

### Changed
- Property `model` in `PbipInspect` renamed to `pbip`
- TMDL parser now uses a different approach to avoid errors arising from conflicting names
- Method `parse_tmdl` in `PbipInspect` changed to support expressions

### Fixed
- TMDL and TMLS parses in `PbipInspect` now uses utf-8 encoding
- TMLD parser now checks if relationship file exists
- Variables name in measures source code now appear correctly

## [0.1.0] - 2024-12-13

### Added
- Expectations to validate Power BI project
- tmsl and tmdl parser
- `Pbip` and `PbipInspect` class
- `create_inspect` function to create a `PbipInspect`
