"""Paso 9: servicios externos simulados con Mock (sin llamadas reales).

El PMS no llama a un proveedor de pagos, pero SI depende de puertos hacia sistemas externos:
  - IAutorizacionGerencialService : valida credenciales gerenciales (en produccion, un proveedor de identidad).
  - IHotelAliadoCatalogo          : catalogo de hoteles aliados (en produccion, una API/base externa).
Aqui el Mock sustituye al puerto, de modo que se prueba la logica de la capa de aplicacion sin red ni credenciales.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock

import pytest

from aplicacion.abstracciones import AutorizacionInvalidaException, IAutorizacionGerencialService
from aplicacion.comandos import (AplicarAjusteFolioCommand, ConfirmarReservacionCommand, DatosHuespedDto,
                                 GarantiaPagoDto, ConsultarFolioQuery, RegistrarCargoCommand,
                                 RegistrarCheckInCommand)
from dominio.comun import DominioException
from dominio.enumeraciones import CanalVenta, TipoCliente, TipoGarantia, TipoHabitacion
from dominio.value_objects import AutorizacionGerencial
from infraestructura.composicion import PMSComposition
from infraestructura.persistencia import PMSDatabase
from infraestructura.servicios import RelojFijo

AHORA = datetime(2026, 10, 13, 10, 0)


def estancia_con_cargo(autorizaciones):
    """Arrange: PMS con el servicio de autorizacion inyectado, reserva con check-in y un cargo de 200 USD."""
    pms = PMSComposition(PMSDatabase.con_datos_iniciales(), RelojFijo(AHORA), autorizaciones)
    entrada = AHORA.date()
    reserva = pms.reservaciones.confirmar_reservacion(ConfirmarReservacionCommand(
        DatosHuespedDto("Ana Lopez"), entrada, entrada + timedelta(days=2), TipoHabitacion.DOBLE,
        CanalVenta.DIRECTO, TipoCliente.INDIVIDUAL, GarantiaPagoDto(TipoGarantia.TARJETA_CREDITO, "VISA-4242")))
    check_in = pms.recepcion.registrar_check_in(RegistrarCheckInCommand(reserva.reserva_id, "INE-1", "Mexicana"))
    pms.recepcion.registrar_cargo(RegistrarCargoCommand(
        check_in.folio_id, "Cena", "V-1", Decimal("200"), "Restaurante", "Ana Lopez"))
    return pms, check_in.folio_id


def test_cp19_mock_aprueba_credenciales_y_se_aplica_el_ajuste():                  # EXITO
    servicio = Mock(spec=IAutorizacionGerencialService)
    servicio.validar.return_value = AutorizacionGerencial("gerente", AHORA)
    pms, folio_id = estancia_con_cargo(servicio)

    folio = pms.recepcion.aplicar_ajuste(
        AplicarAjusteFolioCommand(folio_id, Decimal("-80"), "Cortesia", "gerente", "1234"))

    assert folio.saldo == Decimal("120.00")
    servicio.validar.assert_called_once_with("gerente", "1234", AHORA)            # se consulto una vez


def test_cp20_mock_rechaza_credenciales_y_el_folio_no_cambia():                  # ERROR
    servicio = Mock(spec=IAutorizacionGerencialService)
    servicio.validar.side_effect = AutorizacionInvalidaException()
    pms, folio_id = estancia_con_cargo(servicio)

    with pytest.raises(AutorizacionInvalidaException):
        pms.recepcion.aplicar_ajuste(
            AplicarAjusteFolioCommand(folio_id, Decimal("-80"), "Cortesia", "gerente", "mal"))

    assert pms.recepcion.consultar_folio(ConsultarFolioQuery(folio_id)).saldo == Decimal("200.00")


def test_cp21_ajuste_dentro_del_limite_sin_credenciales_no_consulta_al_servicio():  # LIMITE
    servicio = Mock(spec=IAutorizacionGerencialService)
    pms, folio_id = estancia_con_cargo(servicio)

    folio = pms.recepcion.aplicar_ajuste(AplicarAjusteFolioCommand(folio_id, Decimal("-50"), "Cortesia menor"))

    assert folio.saldo == Decimal("150.00")
    servicio.validar.assert_not_called()                                          # no hubo llamada externa


def test_cp22_ajuste_mayor_a_50_sin_credenciales_se_rechaza_sin_llamar_al_servicio():  # ERROR
    servicio = Mock(spec=IAutorizacionGerencialService)
    pms, folio_id = estancia_con_cargo(servicio)

    with pytest.raises(DominioException, match="RN-10"):
        pms.recepcion.aplicar_ajuste(AplicarAjusteFolioCommand(folio_id, Decimal("-51"), "Descuento"))

    servicio.validar.assert_not_called()


def test_cp23_servicio_externo_con_timeout_se_propaga_y_no_se_modifica_el_folio():  # ERROR (falla externa)
    servicio = Mock(spec=IAutorizacionGerencialService)
    servicio.validar.side_effect = TimeoutError("proveedor de identidad no responde")
    pms, folio_id = estancia_con_cargo(servicio)

    with pytest.raises(TimeoutError):
        pms.recepcion.aplicar_ajuste(
            AplicarAjusteFolioCommand(folio_id, Decimal("-80"), "Cortesia", "gerente", "1234"))

    assert pms.database.folios[folio_id].ajustes == []
