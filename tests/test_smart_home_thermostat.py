"""Define tests for Thermostat module."""
import json

import pytest

import smart_home.Thermostat as th


def test_HomeData(homeData):
    assert homeData.default_home == "MYHOME"
    assert len(homeData.rooms[homeData.default_home]) == 2

    assert len(homeData.modules[homeData.default_home]) == 3

    expected = {
        "12:34:56:00:fa:d0": {
            "id": "12:34:56:00:fa:d0",
            "type": "NAPlug",
            "name": "Thermostat",
            "setup_date": 1494963356,
            "modules_bridged": ["12:34:56:00:01:ae"],
        },
        "12:34:56:00:01:ae": {
            "id": "12:34:56:00:01:ae",
            "type": "NATherm1",
            "name": "Livingroom",
            "setup_date": 1494963356,
            "room_id": "2746182631",
            "bridge": "12:34:56:00:fa:d0",
        },
        "12:34:56:00:f1:62": {
            "id": "12:34:56:00:f1:62",
            "type": "NACamera",
            "name": "Hall",
            "setup_date": 1544828430,
            "room_id": "3688132631",
        },
    }
    assert homeData.modules[homeData.default_home] == expected


def test_HomeData_homeById(homeData):
    home_id = "91763b24c43d3e344f424e8b"
    assert homeData.homeById(home_id)["name"] == "MYHOME"


def test_HomeData_homeByName(homeData):
    assert homeData.homeByName()["name"] == "MYHOME"


def test_HomeData_gethomeId(homeData):
    assert homeData.gethomeId() == "91763b24c43d3e344f424e8b"


def test_HomeData_getSelectedschedule(homeData):
    assert homeData.getSelectedschedule()["name"] == "Default"


def test_HomeStatus(homeStatus):
    assert len(homeStatus.rooms) == 1
    assert homeStatus.default_room["id"] == "2746182631"

    expexted = {
        "id": "2746182631",
        "reachable": True,
        "therm_measured_temperature": 19.8,
        "therm_setpoint_temperature": 12,
        "therm_setpoint_mode": "away",
        "therm_setpoint_start_time": 1559229567,
        "therm_setpoint_end_time": 0,
    }
    assert homeStatus.default_room == expexted


def test_HomeStatus_roomById(homeStatus):
    expexted = {
        "id": "2746182631",
        "reachable": True,
        "therm_measured_temperature": 19.8,
        "therm_setpoint_temperature": 12,
        "therm_setpoint_mode": "away",
        "therm_setpoint_start_time": 1559229567,
        "therm_setpoint_end_time": 0,
    }
    assert homeStatus.roomById("2746182631") == expexted


def test_HomeStatus_thermostatById(homeStatus):
    expexted = {
        "id": "12:34:56:00:01:ae",
        "reachable": True,
        "type": "NATherm1",
        "firmware_revision": 65,
        "rf_strength": 58,
        "battery_level": 3793,
        "boiler_valve_comfort_boost": False,
        "boiler_status": False,
        "anticipating": False,
        "bridge": "12:34:56:00:fa:d0",
        "battery_state": "high",
    }
    assert homeStatus.thermostatById("12:34:56:00:01:ae") == expexted


def test_HomeStatus_relayById(homeStatus):
    expexted = {
        "id": "12:34:56:00:fa:d0",
        "type": "NAPlug",
        "firmware_revision": 174,
        "rf_strength": 107,
        "wifi_strength": 42,
    }
    assert homeStatus.relayById("12:34:56:00:fa:d0") == expexted


def test_HomeStatus_setPoint(homeStatus):
    assert homeStatus.setPoint("2746182631") == 12


def test_HomeStatus_setPointmode(homeStatus):
    assert homeStatus.setPointmode("2746182631") == "away"


def test_HomeStatus_getAwaytemp(homeStatus):
    assert homeStatus.getAwaytemp() == 14


def test_HomeStatus_getHgtemp(homeStatus):
    assert homeStatus.getHgtemp() == 7


def test_HomeStatus_measuredTemperature(homeStatus):
    assert homeStatus.measuredTemperature() == 19.8


def test_HomeStatus_boilerStatus(homeStatus):
    assert homeStatus.boilerStatus() == False


def test_HomeStatus_thermostatType(homeStatus, homeData):
    assert homeStatus.thermostatType("MYHOME", "2746182631") == "NATherm1"


def test_ThermostatData(thermostatData):
    assert thermostatData.default_device == "Thermostat"
    assert thermostatData.default_module == "Livingroom"
    assert thermostatData.temp == 19.8


def test_ThermostatData_lastData(thermostatData):
    expected = {
        "Livingroom": {
            "time": 1559297836,
            "temperature": 19.8,
            "setpoint_temp": 12,
            "setpoint_mode": "away",
            "battery_vp": 3798,
            "rf_status": 59,
            "therm_relay_cmd": 0,
            "battery_percent": 53,
        }
    }
    assert thermostatData.lastData() == expected


@pytest.mark.parametrize(
    "test_input,expected", [("station_name", "Thermostat"), ("type", "NAPlug")]
)
def test_ThermostatData_deviceById(thermostatData, test_input, expected):
    assert thermostatData.deviceById("12:34:56:00:fa:d0")[test_input] == expected


@pytest.mark.parametrize(
    "test_input,expected", [("_id", "12:34:56:00:fa:d0"), ("type", "NAPlug")]
)
def test_ThermostatData_deviceByName(thermostatData, test_input, expected):
    assert thermostatData.deviceByName("Thermostat")[test_input] == expected


@pytest.mark.parametrize(
    "test_input,expected", [("module_name", "Livingroom"), ("type", "NATherm1")]
)
def test_ThermostatData_moduleById(thermostatData, test_input, expected):
    assert thermostatData.moduleById("12:34:56:00:01:ae")[test_input] == expected


@pytest.mark.parametrize(
    "test_input,expected", [("_id", "12:34:56:00:01:ae"), ("type", "NATherm1")]
)
def test_ThermostatData_moduleByName(thermostatData, test_input, expected):
    assert thermostatData.moduleByName("Livingroom")[test_input] == expected


@pytest.mark.parametrize(
    "mode, temp, endTimeOffset, expected",
    [
        (
            "manual",
            19,
            3600,
            {"status": "ok", "time_exec": 0.020781993865967, "time_server": 1559162635},
        )
    ],
)
def test_ThermostatData_setthermpoint(
    thermostatData, requests_mock, mode, temp, endTimeOffset, expected
):
    with open("fixtures/status_ok.json") as f:
        json_fixture = json.load(f)
    requests_mock.post(
        th._SETTEMP_REQ, json=json_fixture, headers={"content-type": "application/json"}
    )
    assert thermostatData.setthermpoint(mode, temp, endTimeOffset) == expected
