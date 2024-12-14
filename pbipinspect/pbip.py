
from pathlib import Path
from textwrap import dedent

def is_pbip_file(path: str | Path) -> bool:
    new_path = Path(path)
    check = new_path.suffix == '.pbip'
    return check

def find_pbip_file(path: str | Path) -> list[Path]:
    new_path = Path(path)
    pbip_files = list(new_path.glob('*.pbip'))
    return pbip_files

def get_pbip_name(path: str | Path) -> str:
    new_path = Path(path)
    return '.'.join(new_path.name.split('.')[0:-1])

def get_component_path(path: str | Path, component: str) -> Path:
    new_path = Path(path)
    pbip_name = get_pbip_name(new_path)
    component_path = Path.joinpath(
        new_path.parent, 
        f'{pbip_name}.{component}'
    )
    return component_path

def get_semantic_model_path(path: str | Path) -> Path:
    return get_component_path(path, 'SemanticModel')

def get_report_path(path: str | Path) -> Path:
    return get_component_path(path, 'Report')

class PbipNotFoundError(Exception):
    def __init__(self, directory: str | Path):
        self.directory = directory
        message = dedent(f"""
            I'm trying to find a file with '.pbip' extension in the directory '{directory}', but I can't find one.
            Please, check if the directory is correct.
        """)
        super().__init__(message)

class MultiplePbipFilesError(Exception):
    def __init__(self, directory: str | Path, pbips: list[Path]):
        self.directory = directory
        message = dedent(f"""
            I find more than one '.pbip' file in the directory '{directory}'. But I expected only one. 
            The files I found are: {[x.name for x in pbips]}.
            Some alternatives could be:
                - Use only one .pbip file in the directory.
                - Pass .pbip path as an argument. 
                  For example: {Path.joinpath(Path(directory), pbips[0].name)}
        """)
        super().__init__(message)

class SemanticModelFolderNotFoundError(Exception):
    def __init__(self, path: Path):
        self.path = path
        message = dedent(f"""
            There isn't the folder {path}'.
        """)
        super().__init__(message)

class Pbip:
    """
    A class that represents pbip model.
    """
    def __init__(self, model: dict) -> None:
        """
        Initialize the Pbip object with a given model.

        Parameters
        ----------
        model : dict
            The model dictionary containing the data structure.
        """
        self._model = model

    @property
    def model(self) -> dict:
        return self._model
    
    def __getitem__(self, key):
        return self._model[key]

    @property
    def tables(self) -> list[dict]:
        return self.model['model']['tables']
    
    @property
    def relationships(self) -> list[dict]:
        return self.model['model']['relationships']

    @relationships.setter
    def relationships(self, value: list[dict]):
        self.model['model']['relationships'] = value

    def get_table_field(self, table: str, field: str) -> list | None:
        """
        Get a field of a table.

        Parameters
        ----------
        table : str
            The name of the table.
        field : str
            The name of the field.

        Returns
        -------
        list | None
            The field of the table, or None if the table or field does not exist.
        """
        if table not in [x['name'] for x in self.tables]:
            return None
        for t in self.tables:
            if t['name'] == table and field in t:
                return t[field]
        return None

    def get_table_column(self, table: str, column: str) -> dict | None:
        """
        Get a column of a table.

        Parameters
        ----------
        table : str
            The name of the table.
        column : str
            The name of the column.

        Returns
        -------
        dict | None
            The column of the table, or None if the table or column does not exist.
        """
        if table not in [x['name'] for x in self.tables]:
            return None
        for t in self.tables:
            column_names = [x['name'] for x in t['columns']]
            if t['name'] == table and column in column_names:
                return t['columns'][column_names.index(column)]
        return None
    
    def get_table_measure(self, table: str, measure: str) -> dict | None:
        """
        Retrieve a specific measure from a table.

        Parameters
        ----------
        table : str
            The name of the table.
        measure : str
            The name of the measure.

        Returns
        -------
        dict | None
            The measure from the table, or None if the table or measure does not exist.
        """
        if table not in [x['name'] for x in self.tables]:
            return None
        for t in self.tables:
            measure_names = [x['name'] for x in t['measures']]
            if t['name'] == table and measure in measure_names:
                return t['measures'][measure_names.index(measure)]
        return None
