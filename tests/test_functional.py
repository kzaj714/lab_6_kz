import pytest

from src.manager import Manager
from src.models import Parameters, Transfer


def test_total_due_for_all_tenants_equals_apartment_costs():
    manager = Manager(Parameters())

    apartment_key = "apart-polanka"
    year = 2025
    month = 1

    apartment_settlement = manager.get_settlement(apartment_key, year, month)
    tenants_settlements = manager.create_tenants_settlements(apartment_settlement)

    tenants_total_due = sum(
        tenant_settlement.total_due_pln
        for tenant_settlement in tenants_settlements
    )

    assert tenants_total_due == pytest.approx(apartment_settlement.total_due_pln)


def test_get_debtors_returns_tenants_whose_transfers_are_lower_than_rent():
    manager = Manager(Parameters())

    manager.transfers = [
        Transfer(
            amount_pln=1500.0,
            date="2025-01-05",
            settlement_year=2025,
            settlement_month=1,
            tenant="tenant-1",
            type="rent"
        ),
        Transfer(
            amount_pln=1000.0,
            date="2025-01-05",
            settlement_year=2025,
            settlement_month=1,
            tenant="tenant-2",
            type="rent"
        ),
        Transfer(
            amount_pln=1300.0,
            date="2025-01-05",
            settlement_year=2025,
            settlement_month=1,
            tenant="tenant-3",
            type="rent"
        )
    ]

    debtors = manager.get_debtors("apart-polanka", 1, 2025)

    debtors_names = [tenant.name for tenant in debtors]

    assert "Jan Nowak" not in debtors_names
    assert "Adam Kowalski" in debtors_names
    assert "Ewa Adamska" not in debtors_names


def test_check_deposits_returns_information_about_correct_and_incorrect_deposits():
    manager = Manager(Parameters())

    manager.transfers = [
        Transfer(
            amount_pln=3000.0,
            date="2024-01-01",
            settlement_year=None,
            settlement_month=None,
            tenant="tenant-1",
            type="deposit"
        ),
        Transfer(
            amount_pln=1000.0,
            date="2024-01-01",
            settlement_year=None,
            settlement_month=None,
            tenant="tenant-2",
            type="deposit"
        ),
        Transfer(
            amount_pln=2800.0,
            date="2024-01-01",
            settlement_year=None,
            settlement_month=None,
            tenant="tenant-3",
            type="deposit"
        )
    ]

    deposits_report = manager.check_deposits()

    assert deposits_report["tenant-1"]["tenant"] == "Jan Nowak"
    assert deposits_report["tenant-1"]["expected_deposit_pln"] == pytest.approx(3000.0)
    assert deposits_report["tenant-1"]["paid_deposit_pln"] == pytest.approx(3000.0)
    assert deposits_report["tenant-1"]["is_correct"] is True

    assert deposits_report["tenant-2"]["tenant"] == "Adam Kowalski"
    assert deposits_report["tenant-2"]["expected_deposit_pln"] == pytest.approx(2900.0)
    assert deposits_report["tenant-2"]["paid_deposit_pln"] == pytest.approx(1000.0)
    assert deposits_report["tenant-2"]["is_correct"] is False

    assert deposits_report["tenant-3"]["tenant"] == "Ewa Adamska"
    assert deposits_report["tenant-3"]["expected_deposit_pln"] == pytest.approx(2800.0)
    assert deposits_report["tenant-3"]["paid_deposit_pln"] == pytest.approx(2800.0)
    assert deposits_report["tenant-3"]["is_correct"] is True