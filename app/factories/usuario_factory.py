from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from app.models.usuario import Usuario


@dataclass(frozen=True)
class DatosCreacionUsuario:
    nombre: str
    email: str
    password_hash: str


class UsuarioFactory:
    """Factory Method para crear usuarios por rol en el dominio inmobiliario."""

    _creadores: Dict[str, Callable[[DatosCreacionUsuario], Usuario]] = {
        "Cliente": lambda datos: Usuario(
            nombre=datos.nombre,
            email=datos.email,
            password_hash=datos.password_hash,
            rol="Cliente",
        ),
        "Agente": lambda datos: Usuario(
            nombre=datos.nombre,
            email=datos.email,
            password_hash=datos.password_hash,
            rol="Agente",
        ),
        "Admin": lambda datos: Usuario(
            nombre=datos.nombre,
            email=datos.email,
            password_hash=datos.password_hash,
            rol="Admin",
        ),
    }

    @classmethod
    def crear_usuario(
        cls,
        rol: str,
        *,
        nombre: str,
        email: str,
        password_hash: str,
    ) -> Usuario:
        # Por seguridad y alineación arquitectónica, si el rol no es válido, se asigna 'Cliente' por defecto.
        creador = cls._creadores.get(rol, cls._creadores["Cliente"])

        return creador(
            DatosCreacionUsuario(
                nombre=nombre,
                email=email,
                password_hash=password_hash,
            )
        )