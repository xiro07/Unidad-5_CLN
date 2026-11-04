"""Paso 9 (PIA Hotel Costa Azul): casos de exito, error y limite para tres reglas de negocio.

  RN-04  Cancelar con menos de 48 h de anticipacion cobra la primera noche.
  RN-07  Reserva grupal (>= 10 habitaciones) exige deposito minimo del 30 %.
  RN-10  Ajuste de folio mayor a USD 50 exige autorizacion gerencial.

Cada prueba lleva su ID (CP-xx) para trazarla con la matriz matriz_casos_pia.csv.
Las pruebas de dominio NO usan base de datos ni servicios externos.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from dominio.comun import DominioException
from dominio.entidades import Folio, Huesped, Reserva
from dominio.enumeraciones import (CanalVenta, EstadoReserva, TipoCliente, TipoGarantia,
                                   TipoHabitacion)
from dominio.value_objects import (AutorizacionGerencial, DetalleConsumo, GarantiaPago, MonedaMonto,
                                   RangoDeFechas)

AHORA = datetime(2026, 10, 13, 10, 0)
TARJETA = GarantiaPago(TipoGarantia.TARJETA_CREDITO, "VISA-4242")
GERENTE = AutorizacionGerencial("gerente", AHORA)


# ---------- helpers (Arrange reutilizable) ----------
def reserva_confirmada(entrada: datetime, noches: int = 2, total: int = 200) -> Reserva:
    """Reserva individual confirmada cuya llegada es a las 00:00 de `entrada`."""
    r = Reserva.nueva(TipoHabitacion.DOBLE, CanalVenta.DIRECTO, TipoCliente.INDIVIDUAL)
    rango = RangoDeFechas(entrada.date(), (entrada + timedelta(days=noches)).date())
    r.confirmar(Huesped("Ana Lopez"), rango, TARJETA, MonedaMonto.usd(total), datetime(2026, 10, 1))
    return r


def reserva_grupal(habitaciones: int) -> Reserva:
    return Reserva.nueva(TipoHabitacion.DOBLE, CanalVenta.AGENCIA, TipoCliente.GRUPO, habitaciones)


RANGO_GRUPO = RangoDeFechas(date(2026, 11, 10), date(2026, 11, 12))


def folio_con_saldo(saldo: int = 200) -> Folio:
    folio = Folio.abrir(uuid4(), uuid4(), "101", uuid4(), MonedaMonto.usd(100), AHORA)
    vale = DetalleConsumo("Cena", "V-1", MonedaMonto.usd(saldo), AHORA, "Restaurante", "101", "Ana Lopez")
    folio.agregar_cargo(vale, AHORA)
    return folio


# ================= RN-04: cancelacion y penalizacion =================
def test_cp01_cancelar_con_5_dias_no_cobra_penalizacion():                       # EXITO
    reserva = reserva_confirmada(datetime(2026, 10, 18))
    assert reserva.cancelar(AHORA).es_cero
    assert reserva.estado == EstadoReserva.CANCELADA


def test_cp02_cancelar_con_menos_de_48h_cobra_primera_noche():                   # EXITO (penalizacion)
    reserva = reserva_confirmada(datetime(2026, 10, 14), noches=2, total=200)  # llegada en 14 h
    assert reserva.cancelar(AHORA).monto == Decimal("100.00")                    # 200 / 2 noches


def test_cp03_no_se_puede_cancelar_una_reserva_ya_cancelada():                  # ERROR
    reserva = reserva_confirmada(datetime(2026, 10, 18))
    reserva.cancelar(AHORA)
    with pytest.raises(DominioException, match="No se puede cancelar"):
        reserva.cancelar(AHORA)


def test_cp04_exactamente_48h_antes_no_cobra_penalizacion():                     # LIMITE
    reserva = reserva_confirmada(datetime(2026, 10, 15))                         # llegada 15/10 00:00
    exactamente_48h = datetime(2026, 10, 13, 0, 0)
    assert reserva.cancelar(exactamente_48h).es_cero


def test_cp05_47h59m_antes_si_cobra_penalizacion():                              # LIMITE
    reserva = reserva_confirmada(datetime(2026, 10, 15), noches=2, total=200)
    un_minuto_despues = datetime(2026, 10, 13, 0, 1)                             # faltan 47 h 59 min
    assert reserva.cancelar(un_minuto_despues).monto == Decimal("100.00")


# ================= RN-07: reserva grupal y deposito del 30 % =================
def test_cp06_grupo_de_10_con_deposito_30_se_confirma():                         # EXITO
    reserva = reserva_grupal(10)
    reserva.confirmar(Huesped("Grupo ABC"), RANGO_GRUPO, TARJETA, MonedaMonto.usd(1000), AHORA,
                      MonedaMonto.usd(300))
    assert reserva.estado == EstadoReserva.CONFIRMADA
    assert any(type(e).__name__ == "ReservaGrupalConfirmada" for e in reserva.eventos_de_dominio)


def test_cp07_grupo_de_10_sin_deposito_se_rechaza():                             # ERROR
    reserva = reserva_grupal(10)
    with pytest.raises(DominioException, match="RN-07"):
        reserva.confirmar(Huesped("Grupo ABC"), RANGO_GRUPO, TARJETA, MonedaMonto.usd(1000), AHORA, None)
    assert reserva.estado == EstadoReserva.PENDIENTE                             # no cambio de estado


def test_cp08_grupo_de_9_habitaciones_no_exige_deposito():                       # LIMITE
    reserva = reserva_grupal(9)                                                  # 9 < 10: no es grupal
    reserva.confirmar(Huesped("Grupo ABC"), RANGO_GRUPO, TARJETA, MonedaMonto.usd(1000), AHORA)
    assert reserva.estado == EstadoReserva.CONFIRMADA


def test_cp09_deposito_de_299_99_sobre_1000_se_rechaza():                        # LIMITE
    reserva = reserva_grupal(10)
    with pytest.raises(DominioException, match="RN-07"):
        reserva.confirmar(Huesped("Grupo ABC"), RANGO_GRUPO, TARJETA, MonedaMonto.usd(1000), AHORA,
                          MonedaMonto.usd("299.99"))


# ================= RN-10: ajustes mayores a USD 50 =================
def test_cp10_ajuste_de_30_usd_sin_autorizacion_se_aplica():                     # EXITO
    folio = folio_con_saldo(200)
    folio.aplicar_ajuste(MonedaMonto.usd(-30), "Cortesia menor", None, AHORA)
    assert folio.saldo.monto == Decimal("170.00")
    assert folio.ajustes[0].autorizado_por is None


def test_cp11_ajuste_de_50_01_usd_sin_autorizacion_se_rechaza():                 # ERROR
    folio = folio_con_saldo(200)
    with pytest.raises(DominioException, match="RN-10"):
        folio.aplicar_ajuste(MonedaMonto.usd("-50.01"), "Descuento", None, AHORA)
    assert folio.saldo.monto == Decimal("200.00")                                # el saldo no cambio
    assert folio.ajustes == []


def test_cp12_ajuste_de_exactamente_50_usd_sin_autorizacion_se_permite():        # LIMITE
    folio = folio_con_saldo(200)
    folio.aplicar_ajuste(MonedaMonto.usd(-50), "Limite exacto", None, AHORA)
    assert folio.saldo.monto == Decimal("150.00")


def test_cp13_ajuste_de_80_usd_con_autorizacion_registra_al_gerente():           # EXITO
    folio = folio_con_saldo(200)
    folio.aplicar_ajuste(MonedaMonto.usd(-80), "Cortesia gerencial", GERENTE, AHORA)
    assert folio.saldo.monto == Decimal("120.00")
    assert folio.ajustes[0].autorizado_por == "gerente"                          # trazabilidad
