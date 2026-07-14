"""
test_contract_service.py

Tests for the contract service layer.
"""

from decimal import Decimal

import pytest

from src.models.client import Client
from src.models.contract import Contract

from src.services.client_service import create_client
from src.services.contract_service import (
    create_contract,
    list_all_contracts,
    list_unpaid_contracts,
    list_unsigned_contracts,
    update_contract,
)


def test_create_contract_success(
    management_user,
    client,
):
    """
    Happy Path

    A management collaborator creates a contract associated with the
    selected client and that client's commercial contact.
    """

    contract = create_contract(
        client_id=client.id,
        total_amount="12500.50",
        amount_due="4000.25",
        is_signed=False,
        current_user=management_user,
    )

    stored_contract = Contract.get_by_id(
        contract.id
    )

    assert stored_contract.client_id == client.id
    assert stored_contract.sales_contact_id == client.sales_contact_id
    assert stored_contract.total_amount == Decimal("12500.50")
    assert stored_contract.amount_due == Decimal("4000.25")
    assert stored_contract.is_signed is False
    assert stored_contract.created_at is not None
    assert Contract.select().count() == 1


def test_create_contract_without_management_permission(
    commercial_user,
    support_user,
    client,
):
    """
    Sad Path

    Commercial and support collaborators cannot create contracts.
    """

    for current_user in (
        commercial_user,
        support_user,
    ):
        with pytest.raises(
            PermissionError,
            match="Permission denied.",
        ):
            create_contract(
                client_id=client.id,
                total_amount="10000.00",
                amount_due="10000.00",
                is_signed=False,
                current_user=current_user,
            )


def test_create_contract_with_inactive_management_user(
    management_user,
    client,
):
    """
    Sad Path

    An inactive management collaborator cannot create a contract.
    """

    management_user.is_active = False
    management_user.save()

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        create_contract(
            client_id=client.id,
            total_amount="10000.00",
            amount_due="10000.00",
            is_signed=False,
            current_user=management_user,
        )


def test_create_contract_for_unknown_client(
    management_user,
):
    """
    Sad Path

    Creating a contract for an unknown client raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Client not found.",
    ):
        create_contract(
            client_id=9999,
            total_amount="10000.00",
            amount_due="10000.00",
            is_signed=False,
            current_user=management_user,
        )


@pytest.mark.parametrize(
    "invalid_total_amount",
    [
        "invalid",
        "NaN",
        "Infinity",
        None,
    ],
)
def test_create_contract_with_invalid_total_amount(
    management_user,
    client,
    invalid_total_amount,
):
    """
    Sad Path

    Invalid or non-finite total amounts are rejected.
    """

    with pytest.raises(
        ValueError,
        match="Total amount must be a valid number.",
    ):
        create_contract(
            client_id=client.id,
            total_amount=invalid_total_amount,
            amount_due="0.00",
            is_signed=False,
            current_user=management_user,
        )


@pytest.mark.parametrize(
    "invalid_total_amount",
    [
        "0",
        "-1",
    ],
)
def test_create_contract_with_non_positive_total_amount(
    management_user,
    client,
    invalid_total_amount,
):
    """
    Sad Path

    The total contract amount must be greater than zero.
    """

    with pytest.raises(
        ValueError,
        match="Total amount must be greater than zero.",
    ):
        create_contract(
            client_id=client.id,
            total_amount=invalid_total_amount,
            amount_due="0.00",
            is_signed=False,
            current_user=management_user,
        )


@pytest.mark.parametrize(
    "invalid_amount_due",
    [
        "invalid",
        "NaN",
        "Infinity",
        None,
    ],
)
def test_create_contract_with_invalid_amount_due(
    management_user,
    client,
    invalid_amount_due,
):
    """
    Sad Path

    Invalid or non-finite remaining amounts are rejected.
    """

    with pytest.raises(
        ValueError,
        match="Amount due must be a valid number.",
    ):
        create_contract(
            client_id=client.id,
            total_amount="10000.00",
            amount_due=invalid_amount_due,
            is_signed=False,
            current_user=management_user,
        )


def test_create_contract_with_negative_amount_due(
    management_user,
    client,
):
    """
    Sad Path

    The remaining amount cannot be negative.
    """

    with pytest.raises(
        ValueError,
        match="Amount due cannot be negative.",
    ):
        create_contract(
            client_id=client.id,
            total_amount="10000.00",
            amount_due="-0.01",
            is_signed=False,
            current_user=management_user,
        )


def test_create_contract_with_amount_due_above_total(
    management_user,
    client,
):
    """
    Sad Path

    The remaining amount cannot exceed the total contract amount.
    """

    with pytest.raises(
        ValueError,
        match="Amount due cannot exceed total amount.",
    ):
        create_contract(
            client_id=client.id,
            total_amount="10000.00",
            amount_due="10000.01",
            is_signed=False,
            current_user=management_user,
        )


@pytest.mark.parametrize(
    "invalid_signed_status",
    [
        "false",
        0,
        1,
        None,
    ],
)
def test_create_contract_with_non_boolean_signed_status(
    management_user,
    client,
    invalid_signed_status,
):
    """
    Sad Path

    The signature status must be a Boolean value.
    """

    with pytest.raises(
        ValueError,
        match="Signed status must be a Boolean.",
    ):
        create_contract(
            client_id=client.id,
            total_amount="10000.00",
            amount_due="10000.00",
            is_signed=invalid_signed_status,
            current_user=management_user,
        )


def test_list_all_contracts_returns_empty_list(
    commercial_user,
):
    """
    Happy Path

    Contract consultation returns an empty list when no contract exists.
    """

    contracts = list_all_contracts(
        current_user=commercial_user,
    )

    assert contracts == []


def test_list_all_contracts_is_available_to_every_department(
    management_user,
    commercial_user,
    support_user,
    client,
):
    """
    Happy Path

    Commercial, management and support collaborators can consult every
    contract in read-only mode.
    """

    first_contract = create_contract(
        client_id=client.id,
        total_amount="10000.00",
        amount_due="5000.00",
        is_signed=False,
        current_user=management_user,
    )

    second_contract = create_contract(
        client_id=client.id,
        total_amount="20000.00",
        amount_due="0.00",
        is_signed=True,
        current_user=management_user,
    )

    expected_ids = [
        first_contract.id,
        second_contract.id,
    ]

    for current_user in (
        commercial_user,
        management_user,
        support_user,
    ):
        contracts = list_all_contracts(
            current_user=current_user,
        )

        assert [
            stored_contract.id
            for stored_contract in contracts
        ] == expected_ids


def test_list_all_contracts_without_authenticated_user(
    test_database,
):
    """
    Sad Path

    An unauthenticated user cannot consult contracts.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        list_all_contracts(
            current_user=None,
        )


def test_list_all_contracts_with_inactive_user(
    support_user,
):
    """
    Sad Path

    An inactive collaborator cannot consult contracts.
    """

    support_user.is_active = False
    support_user.save()

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        list_all_contracts(
            current_user=support_user,
        )


def test_list_unsigned_contracts_returns_all_unsigned_contracts(
    management_user,
    commercial_user,
    client,
):
    """
    Happy Path

    The commercial filter returns every unsigned contract and excludes
    signed contracts.
    """

    first_unsigned_contract = create_contract(
        client_id=client.id,
        total_amount="10000.00",
        amount_due="10000.00",
        is_signed=False,
        current_user=management_user,
    )

    create_contract(
        client_id=client.id,
        total_amount="20000.00",
        amount_due="0.00",
        is_signed=True,
        current_user=management_user,
    )

    second_unsigned_contract = create_contract(
        client_id=client.id,
        total_amount="30000.00",
        amount_due="15000.00",
        is_signed=False,
        current_user=management_user,
    )

    contracts = list_unsigned_contracts(
        current_user=commercial_user,
    )

    assert [
        stored_contract.id
        for stored_contract in contracts
    ] == [
        first_unsigned_contract.id,
        second_unsigned_contract.id,
    ]


def test_list_unsigned_contracts_requires_commercial_permission(
    management_user,
    support_user,
    client,
):
    """
    Sad Path

    The unsigned-contract filter is restricted to commercial users.
    """

    create_contract(
        client_id=client.id,
        total_amount="10000.00",
        amount_due="10000.00",
        is_signed=False,
        current_user=management_user,
    )

    for current_user in (
        management_user,
        support_user,
    ):
        with pytest.raises(
            PermissionError,
            match="Permission denied.",
        ):
            list_unsigned_contracts(
                current_user=current_user,
            )


def test_list_unpaid_contracts_returns_contracts_with_amount_due(
    management_user,
    commercial_user,
    client,
):
    """
    Happy Path

    The commercial filter returns contracts with an amount still due
    and excludes fully paid contracts.
    """

    first_unpaid_contract = create_contract(
        client_id=client.id,
        total_amount="10000.00",
        amount_due="10000.00",
        is_signed=False,
        current_user=management_user,
    )

    create_contract(
        client_id=client.id,
        total_amount="20000.00",
        amount_due="0.00",
        is_signed=True,
        current_user=management_user,
    )

    second_unpaid_contract = create_contract(
        client_id=client.id,
        total_amount="30000.00",
        amount_due="0.01",
        is_signed=True,
        current_user=management_user,
    )

    contracts = list_unpaid_contracts(
        current_user=commercial_user,
    )

    assert [
        stored_contract.id
        for stored_contract in contracts
    ] == [
        first_unpaid_contract.id,
        second_unpaid_contract.id,
    ]


def test_list_unpaid_contracts_requires_commercial_permission(
    management_user,
    support_user,
    client,
):
    """
    Sad Path

    The unpaid-contract filter is restricted to commercial users.
    """

    create_contract(
        client_id=client.id,
        total_amount="10000.00",
        amount_due="10000.00",
        is_signed=False,
        current_user=management_user,
    )

    for current_user in (
        management_user,
        support_user,
    ):
        with pytest.raises(
            PermissionError,
            match="Permission denied.",
        ):
            list_unpaid_contracts(
                current_user=current_user,
            )


def test_update_contract_by_management_success(
    management_user,
    contract,
):
    """
    Happy Path

    A management collaborator can update every contract.
    """

    original_client_id = contract.client_id
    original_created_at = contract.created_at

    updated_contract = update_contract(
        contract_id=contract.id,
        total_amount="15000.00",
        amount_due="0.00",
        is_signed=True,
        current_user=management_user,
    )

    stored_contract = Contract.get_by_id(
        contract.id
    )

    assert updated_contract.id == contract.id
    assert stored_contract.client_id == original_client_id
    assert stored_contract.total_amount == Decimal("15000.00")
    assert stored_contract.amount_due == Decimal("0.00")
    assert stored_contract.is_signed is True
    assert stored_contract.created_at == original_created_at


def test_update_own_contract_by_commercial_success(
    commercial_user,
    contract,
):
    """
    Happy Path

    A commercial collaborator updates a contract belonging to one of
    their clients.
    """

    updated_contract = update_contract(
        contract_id=contract.id,
        total_amount="12000.00",
        amount_due="3000.00",
        is_signed=True,
        current_user=commercial_user,
    )

    assert updated_contract.total_amount == Decimal("12000.00")
    assert updated_contract.amount_due == Decimal("3000.00")
    assert updated_contract.is_signed is True
    assert updated_contract.sales_contact_id == commercial_user.id


def test_commercial_cannot_update_another_commercial_contract(
    management_user,
    second_commercial_user,
    contract,
):
    """
    Sad Path

    A commercial collaborator cannot update a contract belonging to
    another commercial collaborator's client.
    """

    with pytest.raises(
        PermissionError,
        match="You can only update contracts for your own clients.",
    ):
        update_contract(
            contract_id=contract.id,
            total_amount=contract.total_amount,
            amount_due=contract.amount_due,
            is_signed=contract.is_signed,
            current_user=second_commercial_user,
        )


def test_contract_update_uses_current_client_owner_and_synchronizes_contact(
    commercial_user,
    second_commercial_user,
    contract,
):
    """
    Happy Path

    Commercial ownership is determined from the related client, and the
    contract commercial contact is synchronized during the update.
    """

    client = contract.client
    client.sales_contact = second_commercial_user
    client.save(
        only=[
            Client.sales_contact,
        ]
    )

    assert contract.sales_contact_id == commercial_user.id

    updated_contract = update_contract(
        contract_id=contract.id,
        total_amount=contract.total_amount,
        amount_due=contract.amount_due,
        is_signed=contract.is_signed,
        current_user=second_commercial_user,
    )

    assert updated_contract.sales_contact_id == second_commercial_user.id


def test_previous_client_owner_cannot_update_after_reassignment(
    commercial_user,
    second_commercial_user,
    contract,
):
    """
    Sad Path

    A commercial collaborator loses update permission after their client
    is reassigned to another commercial collaborator.
    """

    client = contract.client
    client.sales_contact = second_commercial_user
    client.save(
        only=[
            Client.sales_contact,
        ]
    )

    with pytest.raises(
        PermissionError,
        match="You can only update contracts for your own clients.",
    ):
        update_contract(
            contract_id=contract.id,
            total_amount=contract.total_amount,
            amount_due=contract.amount_due,
            is_signed=contract.is_signed,
            current_user=commercial_user,
        )


def test_update_contract_without_authorized_department_hides_existence(
    support_user,
):
    """
    Sad Path

    An unauthorized department is rejected before the contract lookup.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        update_contract(
            contract_id=9999,
            total_amount="10000.00",
            amount_due="10000.00",
            is_signed=False,
            current_user=support_user,
        )


def test_update_contract_with_inactive_commercial_hides_existence(
    commercial_user,
):
    """
    Sad Path

    An inactive commercial collaborator is rejected before lookup.
    """

    commercial_user.is_active = False
    commercial_user.save()

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        update_contract(
            contract_id=9999,
            total_amount="10000.00",
            amount_due="10000.00",
            is_signed=False,
            current_user=commercial_user,
        )


def test_update_unknown_contract_by_authorized_user(
    management_user,
):
    """
    Sad Path

    An authorized collaborator receives an error for an unknown
    contract.
    """

    with pytest.raises(
        ValueError,
        match="Contract not found.",
    ):
        update_contract(
            contract_id=9999,
            total_amount="10000.00",
            amount_due="10000.00",
            is_signed=False,
            current_user=management_user,
        )


@pytest.mark.parametrize(
    (
        "total_amount",
        "amount_due",
        "expected_message",
    ),
    [
        (
            "invalid",
            "0.00",
            "Total amount must be a valid number.",
        ),
        (
            "0",
            "0.00",
            "Total amount must be greater than zero.",
        ),
        (
            "10000.00",
            "-0.01",
            "Amount due cannot be negative.",
        ),
        (
            "10000.00",
            "10000.01",
            "Amount due cannot exceed total amount.",
        ),
    ],
)
def test_update_contract_validates_amounts(
    management_user,
    contract,
    total_amount,
    amount_due,
    expected_message,
):
    """
    Sad Path

    Contract updates apply the same financial validation as creation.
    """

    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        update_contract(
            contract_id=contract.id,
            total_amount=total_amount,
            amount_due=amount_due,
            is_signed=contract.is_signed,
            current_user=management_user,
        )


def test_update_contract_validates_signed_status(
    management_user,
    contract,
):
    """
    Sad Path

    Contract updates reject a non-Boolean signature status.
    """

    with pytest.raises(
        ValueError,
        match="Signed status must be a Boolean.",
    ):
        update_contract(
            contract_id=contract.id,
            total_amount=contract.total_amount,
            amount_due=contract.amount_due,
            is_signed="true",
            current_user=management_user,
        )
