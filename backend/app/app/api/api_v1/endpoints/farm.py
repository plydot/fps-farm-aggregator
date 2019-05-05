from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from starlette.requests import Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud
from app.api.utils.db import get_db
from app.db_models.farm import Farm as DBFarm
from app.models.farm import Farm, FarmCreate, FarmUpdate, FarmInDB

from farmOS import farmOS

router = APIRouter()

# /farms/ endpoints for farmOS instances

@router.get("/", tags=["farms"], response_model=List[Farm])
def read_farms(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve farms
    """
    farms = crud.farm.get_multi(db, skip=skip, limit=limit)
    return farms

@router.get("/{farm_id}", tags=["farms"], response_model=Farm)
def read_farm_by_id(
    farm_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific farm by id
    """
    farm = crud.farm.get_by_id(db, farm_id=farm_id)
    return farm

@router.post("/", tags=["farms"], response_model=Farm)
async def create_farm(
    *,
    db: Session = Depends(get_db),
    farm_in: FarmCreate
):
    """
    Create new farm
    """
    # Check to see if farm authenticates
    #farm_test = farmOS(farm_in.url, farm_in.username, farm_in.password)
    #farm_in.is_authenticated = farm_test.authenticate()

    farm = crud.farm.create(db, farm_in=farm_in)

    return farm

@router.put("/{farm_id}", tags=["farms"], response_model=Farm)
async def update_farm(
    *,
    db: Session = Depends(get_db),
    farm_id: int,
    farm_in: FarmUpdate,
):
    """
    Update farm
    """
    farm = crud.farm.get_by_id(db, farm_id=farm_id)
    if not farm:
        raise HTTPException(
            status_code=404,
            detail="The farm with this ID does not exist in the system",
        )
    farm = crud.farm.update(db, farm=farm, farm_in=farm_in)
    return farm

@router.delete("/{farm_id}", tags=["farms"], response_model=Farm)
async def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete farm
    """
    farm = crud.farm.delete(db, farm_id=farm_id)
    return farm

# /farms/info/ endpoint for accessing farmOS info

@router.get("/info/", tags=["farm info"])
def get_all_farm_info(
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = {}
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id]['info'] = f.info()

    return data

# /farms/logs/ endpoint for accessing farmOS logs

class Log(BaseModel):
    class Config:
        extra = 'allow'

    name: str
    type: str

class LogUpdate(BaseModel):
    class Config:
        extra = 'allow'

    id: int

@router.get("/logs/", tags=["farm log"])
def get_all_farm_logs(
    request: Request,
    db: Session = Depends(get_db),
    farms: List[int] = Query(None),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)
    query_params = {**request.query_params}
    query_params.pop('farms')

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id] = data[farm.id] + f.log.get(filters=query_params)
    return data

@router.post("/logs/", tags=["farm log"])
def create_farm_logs(
    log: Log,
    farms: List[int] = Query(None),
    #filters: Dict = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.log.send(payload=log.dict()))

    return data

@router.put("/logs/", tags=["farm log"])
def update_farm_logs(
    log: LogUpdate,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.log.send(payload=log.dict()))

    return data

@router.delete("/logs/", tags=["farm log"])
def delete_farm_logs(
    id: int,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.log.delete(id=id))

    return data

# /farms/assets/ endpoint for accessing farmOS assets

class Asset(BaseModel):
    class Config:
        extra = 'allow'

    name: str
    type: str

class AssetUpdate(BaseModel):
    class Config:
        extra = 'allow'

    id: int

@router.get("/assets/", tags=["farm asset"])
def get_all_farm_assets(
    request: Request,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)
    query_params = {**request.query_params}
    query_params.pop('farms')

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id] = data[farm.id] + f.asset.get(filters=query_params)

    return data

@router.post("/assets/", tags=["farm asset"])
def create_farm_assets(
    asset: Asset,
    farms: List[int] = Query(None),
    #filters: Dict = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.asset.send(payload=asset.dict()))


    return data

@router.put("/assets/", tags=["farm asset"])
def update_farm_assets(
    asset: AssetUpdate,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.asset.send(payload=asset.dict()))

    return data

@router.delete("/assets/", tags=["farm asset"])
def delete_farm_assets(
    id: int,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.asset.delete(id=id))

    return data

# /farms/terms/ endpoint for accessing farmOS terms

class Term(BaseModel):
    class Config:
        extra = 'allow'

    name: str
    vocabulary: int

class TermUpdate(BaseModel):
    class Config:
        extra = 'allow'

    id: int

@router.get("/terms/", tags=["farm term"])
def get_all_farm_terms(
    request: Request,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)
    query_params = {**request.query_params}
    query_params.pop('farms')

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id] = data[farm.id] + f.term.get(filters=query_params)

    return data

@router.post("/terms/", tags=["farm term"])
def create_farm_term(
    term: Term,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.term.send(payload=term.dict()))

    return data

@router.put("/terms/", tags=["farm term"])
def update_farm_terms(
    term: TermUpdate,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.term.send(payload=term.dict()))

    return data

@router.delete("/terms/", tags=["farm term"])
def delete_farm_term(
    tid: int,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.term.delete(id=tid))

    return data

# /farms/areas/ endpoint for accessing farmOS areas

class Area(Term):
    class Config:
        extra = 'allow'

    name: str
    area_type: str

class AreaUpdate(BaseModel):
    class Config:
        extra = 'allow'

    id: int

@router.get("/areas/", tags=["farm area"])
def get_all_farm_areas(
    request: Request,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)
    query_params = {**request.query_params}
    query_params.pop('farms')

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id] = data[farm.id] + f.area.get(filters=query_params)

    return data

@router.post("/areas/", tags=["farm area"])
def create_farm_area(
    area: Area,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.area.send(payload=area.dict()))

    return data

@router.put("/areas/", tags=["farm area"])
def update_farm_area(
    area: AreaUpdate,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.area.send(payload=area.dict()))

    return data

@router.delete("/areas/", tags=["farm area"])
def delete_farm_area(
    id: int,
    farms: List[int] = Query(None),
    db: Session = Depends(get_db),
):
    if farms:
        farm_list = crud.farm.get_by_multi_id(db, farm_id_list=farms)
    else:
        farm_list = crud.farm.get_multi(db)

    data = {}
    for farm in farm_list:
        data[farm.id] = []
        f = farmOS(farm.url, farm.username, farm.password)
        if f.authenticate() :
            data[farm.id].append(f.area.delete(id=id))

    return data
