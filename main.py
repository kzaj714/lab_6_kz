import sys

from src.manager import Manager
from src.models import Parameters


def print_section_header(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_subsection_header(title: str):
    """Print a formatted subsection header"""
    print(f"\n  {title}")
    print(f"  {'-' * 40}")


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"{amount:,.2f} PLN"


def display_apartments(manager):
    """Display all apartments with their rooms and bills"""
    print_section_header("APARTMENTS")

    for apartment in manager.apartments.values():
        print(f"\n{apartment.name} ({apartment.key})")
        print(f"   Location: {apartment.location}")
        print(f"   Total Area: {apartment.area_m2} m2")

        print_subsection_header("Rooms")
        for room in apartment.rooms.values():
            print(f"      - {room.name:<25} {room.area_m2:>6} m2")

        # Find bills for this apartment
        apartment_bills = [bill for bill in manager.bills if bill.apartment == apartment.key]
        if apartment_bills:
            print_subsection_header("Bills")
            for bill in apartment_bills:
                month_year = f"{bill.settlement_month}/{bill.settlement_year}" if bill.settlement_month and bill.settlement_year else "N/A"
                print(f"      - {bill.type:<15} {format_currency(bill.amount_pln):>15}  Due: {bill.date_due}  Period: {month_year}")


def display_tenants(manager):
    """Display all tenants with their details and transfers"""
    print_section_header("TENANTS")

    for tenant_key, tenant in manager.tenants.items():
        print(f"\n{tenant.name}")
        print(f"   Apartment: {tenant.apartment}")
        print(f"   Room: {tenant.room}")
        print(f"   Rent: {format_currency(tenant.rent_pln)}/month")
        print(f"   Deposit: {format_currency(tenant.deposit_pln)}")
        print(f"   Agreement: {tenant.date_agreement_from} to {tenant.date_agreement_to}")

        # Find transfers for this tenant
        tenant_transfers = [transfer for transfer in manager.transfers if transfer.tenant == tenant_key]
        if tenant_transfers:
            print_subsection_header("Transfers")
            for transfer in tenant_transfers:
                month_year = f"{transfer.settlement_month}/{transfer.settlement_year}" if transfer.settlement_month and transfer.settlement_year else "N/A"
                print(f"      - {format_currency(transfer.amount_pln):>15}  Date: {transfer.date}  Period: {month_year}")


def display_specific_settlement(manager, apartment_key: str, year: int, month: int):
    apartment_settlement = manager.get_settlement(apartment_key, year, month)

    print_section_header(f"ROZLICZENIE: {apartment_key} ({month}/{year})")

    if apartment_settlement is None:
        print(f"Brak mieszkania o kluczu: {apartment_key}")
        return

    tenants_settlements = manager.create_tenants_settlements(apartment_settlement)

    print(f"Całkowity koszt mieszkania: {format_currency(apartment_settlement.total_due_pln)}")

    if not tenants_settlements:
        print("Brak lokatorów przypisanych do tego mieszkania.")
        return

    print_subsection_header("Rozliczenie lokatorów")

    for tenant_settlement in tenants_settlements:
        print(f"Lokator: {tenant_settlement.tenant}")
        print(f"  Do zapłaty: {format_currency(tenant_settlement.total_due_pln)}")
        print(f"  Wpłacono:   {format_currency(tenant_settlement.total_transfers_pln)}")
        print(f"  Bilans:     {format_currency(tenant_settlement.balance_pln)}")
        print()


if __name__ == "__main__":
    parameters = Parameters()
    manager = Manager(parameters)

    if len(sys.argv) == 4:
        apartment_key = sys.argv[1]

        try:
            year = int(sys.argv[2])
            month = int(sys.argv[3])
            display_specific_settlement(manager, apartment_key, year, month)
        except ValueError:
            print("Błąd: rok i miesiąc muszą być liczbami całkowitymi.")
            print("Poprawne użycie: python main.py <apartment_key> <year> <month>")
            print("Przykład: python main.py apart-polanka 2025 1")
    else:
        print("Poprawne użycie: python main.py <apartment_key> <year> <month>")
        print("Przykład: python main.py apart-polanka 2025 1")
        print()
        display_apartments(manager)
        display_tenants(manager)

    print(f"\n{'=' * 70}\n")