from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import DeclarativeBase


def register_tables(Models: List[type[DeclarativeBase]]):
    tables = {}
    for Model in Models:
        table_name = Model.__tablename__
        tables[table_name] = Model
    return tables


class FilteredColumn(BaseModel):
    column: str
    value: Any


class OrderOption(str, Enum):
    ascending: str = "ascending"
    descending: str = "descending"


class OrderedColumn(BaseModel):
    column: str
    option: str


class AggregationOption(str, Enum):
    count: str = "count"
    avg: str = "avg"
    var: str = "var"
    stddev: str = "stddev"
    sum: str = "sum"
    max: str = "max"
    min: str = "min"
    median: str = "median"
    mode: str = "mode"


class GroupedColumn(BaseModel):
    column: str
    aggr: str


class RetrieveModelQuery(BaseModel):
    column: Optional[List[str]] = Field(default=None)
    filter_by: Optional[List[str]] = Field(default=None)
    filter_value: Optional[List[str]] = Field(default=None)

    def check_query_pairs(self, key, value, query_name):
        if len(key) != len(value):
            raise ValueError(f"{query_name} query is invalid")
        
    def get_retrieved_columns(self, ModelColumn: type[Enum]) -> List[str]:
        return [
            getattr(ModelColumn, column) for column in self.column
        ]
        
    def get_filtered_columns(self, ModelColun: type[Enum]) -> List[FilteredColumn]:
        if self.filter_by is not None and self.filter_value is not None:
            self.check_query_pairs(self.filter_by, self.filter_value, "Filtering")
            return [
                FilteredColumn(column=getattr(ModelColun, column), value=value) for column, value in zip(self.filter_by, self.filter_value)
            ]
        return None


class RetrieveModelsQuery(RetrieveModelQuery):
    offset: int = Field(default=0, gte=0)
    limit: int = Field(default=10, gt=0, lte=100)
    order_by: Optional[List[str]] = Field(default=None)
    order_ascending: Optional[List[str]] = Field(default=None)
    group_by: Optional[List[str]] = Field(default=None)
    group_aggr: Optional[List[str]] = Field(default=None)

    def get_ordering_columns(self, model_column: Enum) -> List[OrderedColumn]:
        if self.order_by is not None and self.order_ascending is not None:
            self.check_query_numbers(self.order_by, self.order_ascending, "Ordering")
            options = []
            for is_ascending in self.order_ascending:
                if is_ascending.lower() == "true":
                    option = "ascending"
                elif is_ascending.lower() == "false":
                    option = "descending"
                else:
                    raise ValueError("Query order_ascending should be boolean")
                options.append(option)
            return [
                OrderedColumn(column=getattr(model_column, column), option=getattr(OrderOption, option)) for column, option in zip(self.order_by, options)
            ]
        return None


    def get_grouping_columns(self, model_column: Enum) -> List[GroupedColumn]:
        if self.group_by is not None and self.group_aggr is not None:
            self.check_query_numbers(self.group_by, self.group_aggr, "Grouping")
            return [
                GroupedColumn(column=getattr(model_column, column), aggr=getattr(AggregationOption, aggr_option)) for column, aggr_option in zip(self.group_by, self.group_aggr)
            ]
        return None
    

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseTablename(BaseSchema):
    pass


class TablenameTable(BaseTablename):
    pass


class ConciseTablename(BaseTablename):
    pass


class VerboseTablname(BaseTablename):
    pass


# TableModel.Meta.table_schema = TablenameTable
# TableModel.Meta.concise_schema = ConciseTablename
# TableModel.Meta.verbose_schema = VerboseTablename
