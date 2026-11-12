"""
Modulo de base de datos (database.py)
Gestiona la conexion asincrona a MongoDB utilizando Motor
"""

from decouple import config
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = config("MONGO_URL", default="mongodb://localhost:27017")
DATABASE_NAME = config("DATABASE_NAME", default="restaurante_db")

client = AsyncIOMotorClient(MONGODB_URL)

database = client[DATABASE_NAME]

coleccion_menus_diarios = database["menus_diarios"]


async def verificar_conexion():
    """Comprueba el estado de la conexion al iniciar la API."""
    try:
        await client.admin.command("ping")
        print(f"Conexion exitosa a MongoDB - Base de Datos: '{DATABASE_NAME}'")
    except Exception as e:
        print(f"Error de conexion a MongoDB: {e}")
