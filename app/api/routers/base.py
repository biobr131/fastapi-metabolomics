from fastapi import APIRouter, Body, Depends, Path, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.crud.base import (
    check_connection,
    create_model, retrieve_schemas, retrieve_schema, update_model, delete_model
)
from api.schemas.base import RetrieveModelsQuery, RetrieveModelQuery
from api.dependencies import get_session_dev, get_session_prod

TABLES = {}

HEALTH_CHECK_ROUTE = "health-check"

router = APIRouter()


@router.get(f"/{HEALTH_CHECK_ROUTE}", response_model=dict)
async def check_health(session: Session = Depends(get_session_prod)):
    return check_connection(session)


router_dev = APIRouter()


@router_dev.get(f"/{HEALTH_CHECK_ROUTE}", response_model=dict)
async def check_health_dev(session: Session = Depends(get_session_dev)):
    return check_connection(session)


@router_dev.post("/{table}")
async def create_model_dev(
    session: Session = Depends(get_session_dev), table: str = Path(), created_model_body: BaseModel = Body()
):
    return create_model(session, TABLES, table, created_model_body)


@router_dev.get("/{table}/list")
async def get_models_dev(
    session: Session = Depends(get_session_dev), table: str = Path(),
    retrieve_models_query: RetrieveModelsQuery = Query()
):
    retrieved_columns = retrieve_models_query.get_retrieved_columns(
        TABLES[table]["column"]
    )
    filtering_columns = retrieve_models_query.get_filtering_columns(
        TABLES[table]["column"]
    )
    ordering_columns = retrieve_models_query.get_ordering_columns(
        TABLES[table]["column"]
    )
    grouping_columns = retrieve_models_query.get_grouping_columns(
        TABLES[table]["column"]
    )
    return retrieve_schemas(
        session, TABLES, table, retrieved_columns,
        retrieve_models_query.offset, retrieve_models_query.limit,
        filtering_columns, ordering_columns, grouping_columns
    )


@router_dev.get("/{table}/{index}")
async def get_model_dev(
    session: Session = Depends(get_session_dev), table: str = Path(), index: str = Path(),
    retrieve_model_query: RetrieveModelQuery = Query(),
):
    retrieved_columns = retrieve_model_query.get_retrieved_columns(
        TABLES[table]["column"]
    )
    filtering_columns = retrieve_model_query.get_filtering_columns(
        TABLES[table]["column"]
    )
    return retrieve_schema(
        session, TABLES, table, index, retrieve_model_query.column,
        retrieved_columns, filtering_columns
    )


@router_dev.put("/{table}/{index}")
async def update_model_dev(
    session: Session = Depends(get_session_dev), table: str = Path(), index: str = Path(),
    updated_model_body = Body()
):
    return update_model(session, TABLES, table, index, updated_model_body)


@router_dev.delete("/{table}/{index}")
async def delete_model_dev(
    session: Session = Depends(get_session_dev), table: str = Path(), index: str = Path()
):
    return delete_model(session, TABLES, table, index)

