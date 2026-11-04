# app/crud/donation.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation


class CRUDDonation(CRUDBase):

    async def get_all_not_fully_invested(
        self,
        session: AsyncSession,
    ) -> list[Donation]:
        # «Свободные» пожертвования: в них осталась нераспределённая сумма.
        db_donations = await session.execute(
            select(Donation).where(
                Donation.fully_invested.is_(False)
            ).order_by(Donation.create_date)
        )
        return list(db_donations.scalars().all())


donation_crud = CRUDDonation(Donation)
