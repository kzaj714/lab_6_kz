from src.models import Apartment, Bill, Parameters, Tenant, TenantSettlement, Transfer, ApartmentSettlement
from typing import List


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []

        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None) -> float | None:
        if month is not None and (month < 1 or month > 12):
            raise ValueError("Month must be between 1 and 12")

        if apartment_key not in self.apartments:
            return None

        total_cost = 0.0

        for bill in self.bills:
            if (
                bill.apartment == apartment_key
                and (year is None or bill.settlement_year == year)
                and (month is None or bill.settlement_month == month)
            ):
                total_cost += bill.amount_pln

        return total_cost

    def get_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")

        if apartment_key not in self.apartments:
            return None

        total_cost = self.get_apartment_costs(apartment_key, year, month)

        if total_cost is None:
            return None

        return ApartmentSettlement(
            key=f"{apartment_key}-{year}-{month}",
            apartment=apartment_key,
            year=year,
            month=month,
            total_due_pln=total_cost
        )

    def get_tenant_transfers(
        self,
        tenant_key: str,
        year: int = None,
        month: int = None,
        transfer_type: str = None
    ) -> float:
        if month is not None and (month < 1 or month > 12):
            raise ValueError("Month must be between 1 and 12")

        total_transfers = 0.0

        for transfer in self.transfers:
            if (
                transfer.tenant == tenant_key
                and (year is None or transfer.settlement_year == year)
                and (month is None or transfer.settlement_month == month)
                and (transfer_type is None or transfer.type == transfer_type)
            ):
                total_transfers += transfer.amount_pln

        return total_transfers

    def create_tenants_settlements(self, apartment_settlement: ApartmentSettlement) -> List[TenantSettlement] | None:
        if apartment_settlement.month < 1 or apartment_settlement.month > 12:
            raise ValueError("Month must be between 1 and 12")

        if apartment_settlement.apartment not in self.apartments:
            return None

        tenants_in_apartment = [
            (tenant_key, tenant)
            for tenant_key, tenant in self.tenants.items()
            if tenant.apartment == apartment_settlement.apartment
        ]

        if not tenants_in_apartment:
            return []

        tenant_due = apartment_settlement.total_due_pln / len(tenants_in_apartment)

        settlements = []

        for tenant_key, tenant in tenants_in_apartment:
            total_transfers = self.get_tenant_transfers(
                tenant_key,
                apartment_settlement.year,
                apartment_settlement.month,
                "rent"
            )

            settlements.append(
                TenantSettlement(
                    tenant=tenant.name,
                    apartment_settlement=apartment_settlement.key,
                    month=apartment_settlement.month,
                    year=apartment_settlement.year,
                    total_due_pln=tenant_due,
                    total_transfers_pln=total_transfers,
                    balance_pln=total_transfers - tenant_due
                )
            )

        return settlements

    def get_debtors(self, apartment_key: str, month: int, year: int) -> List[Tenant]:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")

        if apartment_key not in self.apartments:
            return []

        debtors = []

        for tenant_key, tenant in self.tenants.items():
            if tenant.apartment == apartment_key:
                total_transfers = self.get_tenant_transfers(
                    tenant_key,
                    year,
                    month,
                    "rent"
                )

                if total_transfers < tenant.rent_pln:
                    debtors.append(tenant)

        return debtors

    def check_deposits(self) -> dict:
        result = {}

        for tenant_key, tenant in self.tenants.items():
            paid_deposit = self.get_tenant_transfers(
                tenant_key,
                transfer_type="deposit"
            )

            result[tenant_key] = {
                "tenant": tenant.name,
                "expected_deposit_pln": tenant.deposit_pln,
                "paid_deposit_pln": paid_deposit,
                "is_correct": paid_deposit == tenant.deposit_pln
            }

        return result