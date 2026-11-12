from datetime import datetime
from typing import Annotated, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import core_schema


class _ObjectIdPydanticAnnotation:
    """Adaptador para validar y serializar ObjectId de MongoDB en Pydantic v2."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate(value):
            if isinstance(value, ObjectId):
                return str(value)
            if isinstance(value, str) and ObjectId.is_valid(value):
                return value
            raise ValueError("ID invalido de MongoDB (ObjectId)")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.to_string_ser_schema(),
        )


PyObjectId = Annotated[str, _ObjectIdPydanticAnnotation]


class PlatoMenuBase(BaseModel):
    plato: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Nombre del plato",
        example="Bandeja paisa",
    )
    categoria_plato: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Categoria gastronomica del plato",
        example="Plato principal",
    )
    precio: float = Field(
        ...,
        gt=0,
        description="Precio del plato",
        example=28000,
    )
    disponible_hoy: bool = Field(
        default=True,
        description="Indica si el plato esta disponible hoy",
    )


class PlatoMenuCreate(PlatoMenuBase):
    """Modelo para recibir solicitudes POST de creacion."""

    pass


class PlatoMenuUpdate(BaseModel):
    """Modelo para solicitudes PUT con campos opcionales para edicion."""

    plato: Optional[str] = Field(None, min_length=3, max_length=150)
    categoria_plato: Optional[str] = Field(None, min_length=2, max_length=100)
    precio: Optional[float] = Field(None, gt=0)
    disponible_hoy: Optional[bool] = None


class PlatoMenu(PlatoMenuBase):
    """Modelo completo de respuesta con el ID y la fecha de registro."""

    id: PyObjectId = Field(
        alias="_id",
        description="Identificador unico de ObjectId de MongoDB",
    )
    fecha_creacion: datetime = Field(
        default_factory=datetime.now,
        description="Fecha de registro",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "654321789abcdef012345678",
                "plato": "Bandeja paisa",
                "categoria_plato": "Plato principal",
                "precio": 28000,
                "disponible_hoy": True,
                "fecha_creacion": "2026-11-05T18:30:00",
            }
        },
    )
