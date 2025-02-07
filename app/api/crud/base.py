from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from api.schemas.base import (
    FilteredColumn, OrderOption, OrderedColumn, AggregationOption, GroupedColumn,
)


def check_connection(session: Session) -> dict:
    try:
        session.execute(text("SELECT 1"))
        return {
            "Status": "Success",
            "Detail": "Connection to database is successful",
            "Host": session.bind.url.host,
            "Database": session.bind.url.database,
            "Query": session.bind.url.query,
        }
    except Exception as e:
        return {
            "Status": "Failed",
            "Detail": str(e),
        }


def add_filter(statement, filtered_columns: Optional[List[FilteredColumn]]):
    if filtered_columns is not None:
        statement = statement.filter_by(
            **{filtering_column.column: filtering_column.value for filtering_column in filtered_columns}
        )
    return statement


def add_order(statement, ordered_columns: Optional[List[OrderedColumn]]):
    if ordered_columns is not None:
        orders = []
        for ordering_column in ordered_columns:
            if ordering_column.option == OrderOption.ascending:
                orders.append(ordering_column)
            else:
                orders.append(ordering_column.desc())
        statement = statement.order_by(*orders)
    return statement


def add_group(statement, grouped_columns: Optional[List[GroupedColumn]], Model):
    if grouped_columns is not None:
        aggr_funcs = []
        for column in grouped_columns:
            if column.aggr == AggregationOption.count:
                aggr_funcs.append(
                    func.count(getattr(Model, column.column).label(column.column))
                )
            elif column.aggr == AggregationOption.avg:
                aggr_funcs.append(
                    func.avg(getattr(Model, column.column).label(column.column))
                )
            elif column.aggr == AggregationOption.var:
                aggr_funcs.append(
                    func.var(getattr(Model, column.column).label(column.column))
                )
            elif column.aggr == AggregationOption.stddev:
                aggr_funcs.append(
                    func.stddev(getattr(Model, column.column).label(column.column))
                )
            elif column.aggr == AggregationOption.sum:
                aggr_funcs.append(
                    func.sum(getattr(Model, column.column).label(column.column))
                )
            elif column.aggr == AggregationOption.max:
                aggr_funcs.append(
                    func.max(getattr(Model, column.column).label(column.column))
                )
            elif column.aggr == AggregationOption.min:
                aggr_funcs.append(
                    func.min(getattr(Model, column.column).label(column.column))
                )
            elif column.aggr == AggregationOption.median:
                aggr_funcs.append(
                    func.median(getattr(Model, column.column).label(column.column))
                )
            elif column.aggr == AggregationOption.mode:
                aggr_funcs.append(
                    func.mode(getattr(Model, column.column).label(column.column))
                )
        statement = statement.group_by(*aggr_funcs)  #TODO: 要確認
    return statement


def get_primary_key_columns(model) -> List[str]:
    return [
        column.name for column in model.__table__.primary_key.columns
    ]


def get_foreign_key_columns(model) -> List[str]:
    return [
        fk.column.name for fk in model.__table__.foreign_keys
    ]


def get_all_model_classes(tables):
    return [
        table_classes["model"] for table_classes in tables.values()
    ]


def get_reference_model_class(foreign_key_column, tables):
    Models = get_all_model_classes(tables)
    for Model in Models:
        primary_key_columns = get_primary_key_columns(Model)
        if foreign_key_column in primary_key_columns:
            return Model
    raise ValueError(
        f"ModelClass having {foreign_key_column} as the primary key was not found in {Models}."
    )


def get_verbose_dict(session: Session, model, tables):
    foreign_key_columns = get_foreign_key_columns(model)
    verbose_dict = {}
    for column in model.__table__.columns:
        if column in foreign_key_columns:
            ReferenceModel = get_reference_model_class(column, tables)
            reference_model_table_name = ReferenceModel.__table__.name
            reference_model_id = getattr(model, column.name)
            filtering_column = FilteredColumn(
                column=getattr(tables[reference_model_table_name], column), value=reference_model_id
            )
            reference_model = retrieve_model(
                session, tables, reference_model_table_name, filtering_columns=[filtering_column]
            )
            delattr(model, column.name)
            setattr(
                model, reference_model_table_name, get_verbose_dict(session, reference_model, tables)
            )
        else:
            verbose_dict[column] = getattr(model, column.name)
    return verbose_dict


def create_model(
        session: Session, tables: dict, table_name: str,
        created_model_body: BaseModel
    ) -> BaseModel:
    created_model = tables[table_name].Meta.table_schema.model_validate(created_model_body)
    session.add(created_model)
    session.commit()
    session.refresh(created_model)
    return created_model


def retrieve_models(
        session: Session, tables: dict, table_name: str,
        retrieved_columns: Optional[List[str]], offset: int, limit: int,
        filtered_columns: Optional[List[FilteredColumn]],
        ordered_columns: Optional[List[OrderedColumn]],
        grouped_columns: Optional[List[GroupedColumn]]
):
    Model = tables[table_name]
    if retrieved_columns is None:
        statement = select(Model)
        statement = add_filter(statement, filtered_columns)
        statement = add_order(statement, ordered_columns)
        statement = add_group(statement, grouped_columns, Model)
        statement = statement.offset(offset).limit(limit)
        return session.scalars(statement).all()
    else:
        statement = select(*[getattr(Model, column) for column in retrieved_columns])
        statement = add_filter(statement, filtered_columns)
        statement = add_order(statement, ordered_columns)
        statement = add_group(statement, grouped_columns, Model)
        statement = statement.offset(offset).limit(limit)
        return session.execute(statement).all()
    

def retrieve_schemas(
        session: Session, tables: dict, table_name: str,
        retrieved_columns: Optional[List[str]], offset: int, limit: int,
        filtered_columns: Optional[List[FilteredColumn]],
        ordered_columns: Optional[List[OrderedColumn]],
        grouped_columns: Optional[List[GroupedColumn]],
        verbose: bool = False
) -> List[BaseModel]:
    models = retrieve_models(
        session, tables, table_name, retrieved_columns, offset, limit,
        filtered_columns, ordered_columns, grouped_columns
    )
    if verbose:
        return [
            tables[table_name].Meta.verbose_schema.model_validate(get_verbose_dict(session, model, tables)) for model in models
        ]
    else:
        return [
            tables[table_name].Meta.table_schema.model_validate(model) for model in models
        ]
    

def retrieve_model(
        session: Session, tables: dict, table_name: str,
        retrieved_columns: Optional[List[str]],
        filtered_columns: Optional[List[FilteredColumn]]
    ):
    Model = tables[table_name]
    if retrieved_columns is None:
        statement = select(Model)
        statement = add_filter(statement, filtered_columns)
        return session.scalars(statement).one()
    else:
        statement = select(*[getattr(Model, column) for column in retrieved_columns])
        statement = add_filter(statement, filtered_columns)
        return session.execute(statement).one()


def retrieve_schema(
        session: Session, tables: dict, table_name: str,
        retrieved_columns: Optional[List[str]],
        filtered_columns: Optional[List[FilteredColumn]],
        verbose: bool = False
) -> BaseModel:
    model = retrieve_model(
        session, tables, table_name, retrieved_columns, filtered_columns,
    )
    if verbose:
        return tables[table_name].Meta.verbose_schema.model_validate(get_verbose_dict(session, model, tables))
    else:
        return tables[table_name].Meta.table_schema.model_validate(model)


def update_model(
        session: Session, tables: dict, table_name: str,
        updated_model_index: str, updated_model_body: BaseModel
    ) -> BaseModel:
    filtering_column = FilteredColumn(
        column=tables[table_name].Meta.index_column, value=updated_model_index
    )
    updated_model = retrieve_schema(
        session, tables, table_name, filtering_columns=[filtering_column]
    )
    updated_model_data = updated_model_body.model_dump(exclude_unset=True)
    for key, value in updated_model_data.items():
        setattr(updated_model, key, value)
    session.add(updated_model)
    session.commit()
    session.refresh(updated_model)
    return updated_model


def delete_model(
        session: Session, tables: dict, table_name: str,
        deleted_model_index: str
    ) -> BaseModel:
    filtering_column = FilteredColumn(
        column=tables[table_name].Meta.index_column, value=deleted_model_index
    )
    deleted_model = retrieve_schema(
        session, tables, table_name, filtering_columns=[filtering_column]
    )
    session.delete(deleted_model)
    session.commit()
    return deleted_model
