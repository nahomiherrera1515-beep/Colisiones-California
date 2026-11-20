"""Crea en la base las vistas de consumo definidas en consumo.py."""

from configuracion import conectar
from consumo import crear_vistas


def main():
    with conectar() as con:
        crear_vistas(con)
    print("Vistas creadas")


if __name__ == "__main__":
    main()
