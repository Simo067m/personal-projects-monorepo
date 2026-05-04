import pytest

from memberships.app.db import (
    add_membership,
    get_all_memberships,
    get_membership_by_id,
    get_paid_memberships,
    get_free_memberships,
    get_total_monthly_cost,
    update_membership,
    delete_membership_by_id,
)


# --- Helpers ---

def _add_paid(app, organization="Spotify", price=99.0, frequency="monthly", currency="DKK"):
    """Convenience wrapper for adding a paid membership in tests."""
    with app.app_context():
        add_membership(
            organization=organization,
            description="Music streaming",
            membership_type="Premium",
            member_since="2023-01-01",
            is_paid=True,
            payment_frequency=frequency,
            price_per_period=price,
            currency=currency,
        )


def _add_free(app, organization="Local Library"):
    """Convenience wrapper for adding a free membership in tests."""
    with app.app_context():
        add_membership(
            organization=organization,
            description="Free public library card",
            membership_type="Standard",
            member_since="2022-06-01",
            is_paid=False,
        )


# --- Add & Retrieve ---

def test_add_and_retrieve_paid_membership(app):
    _add_paid(app)
    with app.app_context():
        results = get_all_memberships()
        assert len(results) == 1
        assert results[0]["organization"] == "Spotify"
        assert results[0]["is_paid"] == 1


def test_add_and_retrieve_free_membership(app):
    _add_free(app)
    with app.app_context():
        results = get_all_memberships()
        assert len(results) == 1
        assert results[0]["organization"] == "Local Library"
        assert results[0]["is_paid"] == 0


def test_get_membership_by_id_returns_correct_row(app):
    _add_paid(app)
    with app.app_context():
        all_memberships = get_all_memberships()
        membership_id = all_memberships[0]["id"]

        result = get_membership_by_id(membership_id)
        assert result is not None
        assert result["organization"] == "Spotify"


def test_get_membership_by_id_returns_none_for_unknown(app):
    with app.app_context():
        result = get_membership_by_id(999)
        assert result is None


# --- Filtering ---

def test_get_paid_memberships_excludes_free(app):
    _add_paid(app)
    _add_free(app)
    with app.app_context():
        paid = get_paid_memberships()
        assert len(paid) == 1
        assert paid[0]["organization"] == "Spotify"


def test_get_free_memberships_excludes_paid(app):
    _add_paid(app)
    _add_free(app)
    with app.app_context():
        free = get_free_memberships()
        assert len(free) == 1
        assert free[0]["organization"] == "Local Library"


def test_get_all_memberships_ordered_paid_first(app):
    """Paid memberships should come before free ones regardless of insert order."""
    _add_free(app)
    _add_paid(app)
    with app.app_context():
        results = get_all_memberships()
        assert results[0]["is_paid"] == 1
        assert results[1]["is_paid"] == 0


# --- Monthly Cost ---

def test_total_monthly_cost_for_monthly_frequency(app):
    _add_paid(app, price=99.0, frequency="monthly", currency="DKK")
    with app.app_context():
        totals = get_total_monthly_cost()
        assert "DKK" in totals
        assert totals["DKK"] == pytest.approx(99.0)


def test_total_monthly_cost_for_yearly_frequency(app):
    """A yearly price of 1200 DKK should normalise to 100 DKK/month."""
    _add_paid(app, price=1200.0, frequency="yearly", currency="DKK")
    with app.app_context():
        totals = get_total_monthly_cost()
        assert totals["DKK"] == pytest.approx(100.0)


def test_total_monthly_cost_for_quarterly_frequency(app):
    """A quarterly price of 300 DKK should normalise to 100 DKK/month."""
    _add_paid(app, price=300.0, frequency="quarterly", currency="DKK")
    with app.app_context():
        totals = get_total_monthly_cost()
        assert totals["DKK"] == pytest.approx(100.0)


def test_total_monthly_cost_accumulates_multiple(app):
    """Two paid memberships in the same currency should sum correctly."""
    _add_paid(app, organization="Spotify", price=99.0, frequency="monthly", currency="DKK")
    _add_paid(app, organization="Netflix", price=149.0, frequency="monthly", currency="DKK")
    with app.app_context():
        totals = get_total_monthly_cost()
        assert totals["DKK"] == pytest.approx(248.0)


def test_total_monthly_cost_separates_currencies(app):
    """Memberships in different currencies should not be merged."""
    _add_paid(app, organization="Spotify", price=99.0, frequency="monthly", currency="DKK")
    _add_paid(app, organization="NYT", price=9.99, frequency="monthly", currency="USD")
    with app.app_context():
        totals = get_total_monthly_cost()
        assert "DKK" in totals
        assert "USD" in totals
        assert totals["DKK"] == pytest.approx(99.0)
        assert totals["USD"] == pytest.approx(9.99)


def test_total_monthly_cost_excludes_free_memberships(app):
    _add_free(app)
    with app.app_context():
        totals = get_total_monthly_cost()
        assert totals == {}


# --- Update ---

def test_update_membership_persists_changes(app):
    _add_paid(app)
    with app.app_context():
        membership_id = get_all_memberships()[0]["id"]

        update_membership(
            membership_id=membership_id,
            organization="Spotify",
            description="Updated description",
            membership_type="Family",
            member_since="2023-01-01",
            is_paid=True,
            payment_frequency="monthly",
            price_per_period=149.0,
            currency="DKK",
        )

        updated = get_membership_by_id(membership_id)
        assert updated["membership_type"] == "Family"
        assert updated["price_per_period"] == 149.0
        assert updated["description"] == "Updated description"


def test_update_membership_can_switch_to_free(app):
    """A paid membership should be updatable to free, clearing payment fields."""
    _add_paid(app)
    with app.app_context():
        membership_id = get_all_memberships()[0]["id"]

        update_membership(
            membership_id=membership_id,
            organization="Spotify",
            description="Now free via student deal",
            membership_type="Student",
            member_since="2023-01-01",
            is_paid=False,
        )

        updated = get_membership_by_id(membership_id)
        assert updated["is_paid"] == 0
        assert updated["price_per_period"] is None


# --- Delete ---

def test_delete_membership_removes_record(app):
    _add_paid(app)
    with app.app_context():
        membership_id = get_all_memberships()[0]["id"]
        delete_membership_by_id(membership_id)

        assert get_membership_by_id(membership_id) is None
        assert get_all_memberships() == []