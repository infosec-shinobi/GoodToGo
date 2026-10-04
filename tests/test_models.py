from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.entities import Household, HouseholdMembership, User, UserPreference


def test_schema_and_household_membership_mapping_work_in_sqlite():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    user = User(email="alex@example.test", display_name="Alex")
    user.preference = UserPreference(theme_mode="dark", color_scheme="forest")
    household = Household(
        name="Example household",
        jurisdiction="US-OH",
        content_pack_version="2026.09",
    )
    household.memberships.append(HouseholdMembership(user=user, role="owner"))

    with Session(engine) as session:
        session.add(household)
        session.commit()
        session.refresh(user)

        assert user.preference.theme_mode == "dark"
        assert user.preference.color_scheme == "forest"
        assert user.memberships[0].household.name == "Example household"

