from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.card_repository import CardRepository
from app.schemas.card import CardWithPlayerResponse, CardPriceResponse, CardResponse
from app.schemas.player import PlayerListItemResponse


class CardService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CardRepository(session)

    async def get_cards(
        self,
        player_id: Optional[int] = None,
        rarity: Optional[str] = None,
        season_year: Optional[int] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[CardWithPlayerResponse], int]:
        cards, total = await self.repo.get_cards(player_id, rarity, season_year, page, page_size)
        resp_list = []
        for c in cards:
            player_dict = None
            if c.player:
                player_dict = PlayerListItemResponse.model_validate(c.player).model_dump()
                
            c_dict = {
                "id": c.id,
                "sorare_id": c.sorare_id,
                "asset_id": c.asset_id,
                "player_id": c.player_id,
                "season_year": c.season_year,
                "rarity": c.rarity,
                "position": c.position,
                "power": c.power,
                "grade": c.grade,
                "image_url": c.image_url,
                "latest_price": c.prices[0].price if c.prices else None,
                "currency": c.prices[0].currency if c.prices else "EUR",
                "player": player_dict
            }
            resp_list.append(CardWithPlayerResponse(**c_dict))
        return resp_list, total

    async def get_card_by_id(self, card_id: int) -> Optional[CardWithPlayerResponse]:
        card = await self.repo.get_by_id(card_id)
        if not card:
            return None
        player_dict = None
        if card.player:
            player_dict = PlayerListItemResponse.model_validate(card.player).model_dump()
            
        c_dict = {
            "id": card.id,
            "sorare_id": card.sorare_id,
            "asset_id": card.asset_id,
            "player_id": card.player_id,
            "season_year": card.season_year,
            "rarity": card.rarity,
            "position": card.position,
            "power": card.power,
            "grade": card.grade,
            "image_url": card.image_url,
            "latest_price": card.prices[0].price if card.prices else None,
            "currency": card.prices[0].currency if card.prices else "EUR",
            "player": player_dict
        }
        return CardWithPlayerResponse(**c_dict)

    async def get_card_prices(self, card_id: int, limit: int = 30) -> List[CardPriceResponse]:
        prices = await self.repo.get_card_prices(card_id, limit)
        return [CardPriceResponse.model_validate(p) for p in prices]
