from datetime import datetime, timezone
from typing import List, Dict
from .enums import RankingType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client


class SingleRankedProgress:
    __slots__ = ('raw', 'client')

    def __init__(self, client: 'Client', data: dict) -> None:
        self.raw = data
        self.client = client

    def __repr__(self):
        return ('<SingleRankedProgress ranking_type={0.ranking_type} current_division={0.current_division} '
                'highest_division={0.highest_division} promotion_progress={0.promotion_progress} '
                'last_updated={0.last_updated} trackguid={0.track_guid}>'.format(self))

    @property
    def ranking_type(self) -> RankingType:
        return RankingType(self.raw['rankingType'])

    @property
    def last_updated(self) -> datetime:
        return self.client.from_iso(self.raw['lastUpdated'])

    @property
    def track_guid(self) -> str:
        return self.raw['trackguid']

    @property
    def current_division(self) -> int:
        return self.raw['currentDivision']

    @property
    def highest_division(self) -> int:
        return self.raw['highestDivision']

    @property
    def promotion_progress(self) -> float:
        return self.raw['promotionProgress']


class RankedProgress:
    __slots__ = ('raw', 'type_to_ranked_progress')

    def __init__(self, client: 'Client', data: List[dict]) -> None:
        self.raw = data
        self.type_to_ranked_progress: Dict[RankingType, List[SingleRankedProgress]] = {}
        epoch_time = datetime(1970, 1, 1, tzinfo=timezone.utc)

        for ranked_progress in data:
            if ranked_progress['rankingType'] in [RankingType.ZERO_BUILD.value, RankingType.BATTLE_ROYALE.value] \
                    and ranked_progress['gameId'] == 'fortnite':
                single_ranked_progress = SingleRankedProgress(client, ranked_progress)
                if single_ranked_progress.last_updated != epoch_time:
                    ranking_type = RankingType(ranked_progress['rankingType'])
                    if ranking_type not in self.type_to_ranked_progress:
                        self.type_to_ranked_progress[ranking_type] = []
                    self.type_to_ranked_progress[ranking_type].append(single_ranked_progress)

        # Sort the lists
        for ranking_type in self.type_to_ranked_progress:
            self.type_to_ranked_progress[ranking_type].sort(key=lambda x: x.last_updated)

    def __repr__(self):
        return '<RankedProgress type_to_ranked_progress={0.type_to_ranked_progress}>'.format(self)

    def for_type(self, ranking_type: RankingType) -> List[SingleRankedProgress]:
        return self.type_to_ranked_progress.get(ranking_type, [])

    @property
    def battle_royale(self) -> List[SingleRankedProgress]:
        return self.for_type(RankingType.BATTLE_ROYALE)

    @property
    def zero_build(self) -> List[SingleRankedProgress]:
        return self.for_type(RankingType.ZERO_BUILD)
