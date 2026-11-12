from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from database import coleccion_menus_diarios, verificar_conexion
from models import PlatoMenu, PlatoMenuCreate, PlatoMenuUpdate

app = FastAPI(
    title="API de Menu Diario - Restaurante",
    description="API RESTful asincrona con FastAPI y MongoDB para gestionar platos del menu diario",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    await verificar_conexion()


@app.get("/", tags=["Raiz"])
async def root():
    return {
        "mensaje": "Bienvenido a la API de Menu Diario del Restaurante",
        "documentacion": "/docs",
    }


@app.post(
    "/menus-diarios",
    response_model=PlatoMenu,
    status_code=status.HTTP_201_CREATED,
    tags=["Menu diario"],
    summary="Crear un plato en el menu diario",
)
async def create_plato_menu(plato_in: PlatoMenuCreate):
    """Guarda un plato en la coleccion 'menus_diarios' de MongoDB."""
    plato_existente = await coleccion_menus_diarios.find_one(
        {"plato": plato_in.plato}
    )
    if plato_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un plato registrado con el nombre '{plato_in.plato}'.",
        )

    nuevo_plato = plato_in.model_dump()
    nuevo_plato["fecha_creacion"] = datetime.now()

    resultado = await coleccion_menus_diarios.insert_one(nuevo_plato)
    plato_creado = await coleccion_menus_diarios.find_one(
        {"_id": resultado.inserted_id}
    )
    return plato_creado


@app.get(
    "/menus-diarios",
    response_model=List[PlatoMenu],
    status_code=status.HTTP_200_OK,
    tags=["Menu diario"],
    summary="Listar todos los platos del menu diario",
)
async def get_platos_menu():
    """Recupera todos los documentos de la coleccion de MongoDB."""
    platos = []
    cursor = coleccion_menus_diarios.find()
    async for documento in cursor:
        platos.append(documento)
    return platos


@app.get(
    "/menus-diarios/{id}",
    response_model=PlatoMenu,
    status_code=status.HTTP_200_OK,
    tags=["Menu diario"],
    summary="Buscar un plato por ObjectId",
)
async def get_plato_menu_por_id(id: str):
    """Busca un plato por su ObjectId de MongoDB."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId valido de MongoDB",
        )

    plato = await coleccion_menus_diarios.find_one({"_id": ObjectId(id)})
    if plato:
        return plato

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"El plato con ID '{id}' no fue encontrado en la base de datos",
    )


@app.put(
    "/menus-diarios/{id}",
    response_model=PlatoMenu,
    status_code=status.HTTP_200_OK,
    tags=["Menu diario"],
    summary="Actualizar campos de un plato",
)
async def update_plato_menu(id: str, plato_update: PlatoMenuUpdate):
    """Actualiza los campos de un documento en MongoDB por su _id."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId valido",
        )

    datos_a_actualizar = plato_update.model_dump(exclude_unset=True)

    if len(datos_a_actualizar) >= 1:
        resultado_actualizacion = await coleccion_menus_diarios.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos_a_actualizar},
        )

        if (
            resultado_actualizacion.modified_count == 1
            or resultado_actualizacion.matched_count == 1
        ):
            plato_modificado = await coleccion_menus_diarios.find_one(
                {"_id": ObjectId(id)}
            )
            return plato_modificado

    plato_existente = await coleccion_menus_diarios.find_one(
        {"_id": ObjectId(id)}
    )
    if plato_existente:
        return plato_existente

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible actualizar. El plato con ID '{id}' no existe",
    )


@app.delete(
    "/menus-diarios/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Menu diario"],
    summary="Eliminar un plato del menu diario",
)
async def delete_plato_menu(id: str):
    """Elimina un documento de MongoDB por su ObjectId."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId valido",
        )

    resultado_eliminacion = await coleccion_menus_diarios.delete_one(
        {"_id": ObjectId(id)}
    )

    if resultado_eliminacion.deleted_count == 1:
        return {
            "mensaje": f"Plato con ID '{id}' eliminado exitosamente de MongoDB"
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible eliminar. El plato con ID '{id}' no existe en la base de datos",
    )
