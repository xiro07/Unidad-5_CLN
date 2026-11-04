"""Paso 9: pruebas de persistencia (repositorio + Unit of Work) con la base EN MEMORIA del proyecto.

El PMS no usa SQL todavia: `InMemoryUnitOfWork` aplica las escrituras en commit() y las descarta en rollback().
Cada prueba crea su propia `PMSDatabase`, asi que no comparten datos entre si.
"""
from datetime import date, datetime

import pytest

from aplicacion.abstracciones import transaccion
from dominio.entidades import Huesped, Reserva
from dominio.enumeraciones import CanalVenta, TipoCliente, TipoGarantia, TipoHabitacion
from dominio.value_objects import GarantiaPago, MonedaMonto, RangoDeFechas
from infraestructura.persistencia import InMemoryReservaRepository, InMemoryUnitOfWork, PMSDatabase

AHORA = datetime(2026, 10, 13, 10, 0)


@pytest.fixture
def entorno():
    db = PMSDatabase.con_datos_iniciales()
    uow = InMemoryUnitOfWork(db)
    return db, uow, InMemoryReservaRepository(db, uow)


def una_reserva() -> Reserva:
    r = Reserva.nueva(TipoHabitacion.DOBLE, CanalVenta.DIRECTO, TipoCliente.INDIVIDUAL)
    r.confirmar(Huesped("Ana Lopez"), RangoDeFechas(date(2026, 10, 20), date(2026, 10, 22)),
                GarantiaPago(TipoGarantia.TARJETA_CREDITO, "VISA-4242"), MonedaMonto.usd(300), AHORA)
    return r


def test_cp14_commit_persiste_la_reserva(entorno):                               # EXITO
    db, uow, repo = entorno
    reserva = una_reserva()
    uow.begin()
    repo.save(reserva)
    uow.commit()
    assert repo.find_by_id(reserva.id) is reserva
    assert len(db.reservas) == 1


def test_cp15_rollback_descarta_la_reserva(entorno):                             # ERROR / REVERSION
    db, uow, repo = entorno
    reserva = una_reserva()
    uow.begin()
    repo.save(reserva)
    assert repo.find_by_id(reserva.id) is None       # antes del commit todavia no existe
    uow.rollback()
    assert repo.find_by_id(reserva.id) is None       # tras rollback tampoco
    assert db.reservas == {}


def test_cp16_error_dentro_de_la_transaccion_hace_rollback_automatico(entorno):  # ERROR
    db, uow, repo = entorno
    with pytest.raises(ValueError, match="falla simulada"):
        with transaccion(uow):                       # begin -> bloque -> commit (rollback si falla)
            repo.save(una_reserva())
            raise ValueError("falla simulada")
    assert db.reservas == {}
    assert uow.activa is False                       # la transaccion quedo cerrada


def test_cp17_no_se_puede_iniciar_una_segunda_transaccion_activa(entorno):       # LIMITE
    _, uow, _ = entorno
    uow.begin()
    with pytest.raises(RuntimeError, match="Ya hay una transaccion activa"):
        uow.begin()
    uow.rollback()


def test_cp18_commit_sin_transaccion_activa_falla(entorno):                      # ERROR
    _, uow, _ = entorno
    with pytest.raises(RuntimeError, match="No hay una transaccion activa"):
        uow.commit()
