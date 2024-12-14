
import json
from pathlib import Path
from pbipinspect.expectations import ExpectMessage
from pbipinspect.pbip import (
    is_pbip_file, 
    find_pbip_file,
    get_pbip_name, 
    get_semantic_model_path,
    get_report_path,
    MultiplePbipFilesError,
    Pbip,
    PbipNotFoundError,
    SemanticModelFolderNotFoundError
)
from pbipinspect.tmdl import (
    get_tmdl_relationship,
    get_tmdl_relationship_file,
    get_tmdl_table,
    get_tmdl_table_files,
    has_table_folder
)
from pbipinspect.tmsl import (
    build_tmsl_path,
    clean_tmsl,
    is_TMSL
)
from typing import Callable

class PbipInspect:
    """
    A class for inspecting .pbip files and their associated TMDL and TMSL models.
    """
    def __init__(
        self, 
        name: str | Path,
        semantic_folder: str | Path,
        report_folder: str | Path
    ) -> None:
        """
        Initialize the PbipInspect object with a given name, semantic folder and report folder.

        Parameters
        ----------
        name : str | Path
            The name of the .pbip file.
        semantic_folder : str | Path
            The path of the semantic model folder.
        report_folder : str | Path
            The path of the report folder.

        Returns
        -------
        None
        """
        self.name = name
        self.semantic_folder = semantic_folder
        self.report_folder = report_folder
        self._model = self.parse_pbip()
        self.steps: list[Callable] = []
        self.expects: list[ExpectMessage] = []

    def __repr__(self) -> str:
        return f"PbipInspect(name='{self.name}', semantic_folder='{self.semantic_folder}', report_folder='{self.report_folder}')"

    @property
    def model(self) -> Pbip:
        return self._model

    def parse_tmdl_tables(self) -> list[dict] | None:
        """
        Parse all .tmdl files in the 'definition/tables' folder.

        Returns
        -------
        list[dict] | None
            If the 'definition/tables' folder does not exists, return None.
            Otherwise, return a list of dictionaries, each one representing a table.
        """
        folder = self.semantic_folder
        check = has_table_folder(folder)
        if not check:
            return None
        tables = get_tmdl_table_files(folder)
        parsed_tables = []
        for table in tables:
            content = table.read_text()
            tmdl_parsed = get_tmdl_table(content)
            parsed_tables.append(tmdl_parsed)
        return parsed_tables

    def parse_tmdl_relationships(self) -> list[dict] | None:
        """
        Parse the relationships from the 'relationships.tmdl' file.

        Returns
        -------
        list[dict] | None
            If the 'definition/tables' folder does not exist, return None.
            Otherwise, return a list of dictionaries with relationship details.
        """
        folder = self.semantic_folder
        check = has_table_folder(folder)
        if not check:
            return None
        relationship = get_tmdl_relationship_file(folder)
        content = relationship.read_text()
        parsed_relationship = get_tmdl_relationship(content)
        return parsed_relationship

    #TODO: need to create a real tmdl parser
    def parse_tmdl(self) -> dict:
        """
        Parse the TMDL model from the semantic folder.

        Returns
        -------
        dict
            A dictionary representing the model, containing lists of tables and relationships.
        """
        final_model: dict = {
            'model': {
                'tables': [],
                'relationships': []
            }
        }
        final_model['model']['tables'] = self.parse_tmdl_tables()
        final_model['model']['relationships'] = self.parse_tmdl_relationships()
        return final_model

    def parse_tmsl(self) -> dict:
        """
        Parse the TMSL model from the semantic folder.

        Returns
        -------
        dict
            A dictionary representing the model, containing lists of tables and relationships.
        """
        model_bim = build_tmsl_path(self.semantic_folder)
        with open(model_bim, 'r') as f:
            tmsl = json.load(f)
        final_model = clean_tmsl(tmsl)
        return final_model

    def parse_pbip(self) -> Pbip:
        """
        Parse the PBIP model from the semantic folder.

        Returns
        -------
        Pbip
            An object representing the parsed model, containing the model and a method to run expectations.
        """
        tmsl_check = is_TMSL(self.semantic_folder)
        parse = self.parse_tmsl if tmsl_check else self.parse_tmdl
        final_model = parse()
        return Pbip(final_model)

    def expectations(self, steps: list[Callable]):
        """
        Register a list of expectation functions to run against the model.

        Parameters
        ----------
        steps : list[Callable]
            A list of functions that take a Pbip object as an argument and return a list of ExpectMessage.
        """
        self.steps = steps
    
    def run_expectations(self):
        """
        Executes all registered expectation functions against the model.

        The method iterates over the list of expectation functions stored in `self.steps` 
        and applies each function to the model. It collects the results, which are lists 
        of `ExpectMessage` dictionaries, and flattens them into a single list stored in 
        `self.expects`.

        Returns
        -------
        None
        """
        results = []
        for expect in self.steps:
            results.append(expect(self.model))
        self.expects = [x for y in results for x in y]


def create_inspect(path: str | Path) -> PbipInspect:
    """
    Create a PbipInspect object from a given path, which can be a .pbip file or a directory 
    containing .pbip files. Validates the presence and uniqueness of .pbip files, and verifies 
    the existence of required folders.

    Parameters
    ----------
    path : str | Path
        The path to a specific .pbip file or a directory that may contain .pbip files.

    Returns
    -------
    PbipInspect
        An instance of PbipInspect initialized with the .pbip file's name, semantic folder, 
        and report folder.

    Raises
    ------
    PbipNotFoundError
        If no .pbip file is found in the specified directory.
    MultiplePbipFilesError
        If more than one .pbip file is found in the specified directory.
    SemanticModelFolderNotFoundError
        If the semantic folder does not exist.
    """
    check_pbip = is_pbip_file(path)
    pbips = [Path(path)] if check_pbip else find_pbip_file(path)
    
    if not pbips:
        raise PbipNotFoundError(path)
    
    if len(pbips) > 1:
        raise MultiplePbipFilesError(path, pbips)
    
    pbip = pbips[0]
    pbip_name = get_pbip_name(pbip)
    semantic_folder = get_semantic_model_path(pbip)

    if not semantic_folder.is_dir():
        raise SemanticModelFolderNotFoundError(semantic_folder)

    report_folder = get_report_path(pbip)
    inspect = PbipInspect(pbip_name, semantic_folder, report_folder)
    return inspect
