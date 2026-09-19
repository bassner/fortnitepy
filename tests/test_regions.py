"""Region compatibility through the actual party metadata serializers."""
import copy
import json
import unittest
from types import SimpleNamespace

from fortnitepy import PartyPrivacy, Region
from fortnitepy.party import PartyMemberMeta, PartyMeta


class RegionMetadataTest(unittest.TestCase):
    def make_party_meta(self, region):
        party = SimpleNamespace(config={"privacy": PartyPrivacy.PRIVATE.value})
        return PartyMeta(party, {"Default:RegionId_s": region})

    def make_member_meta(self):
        client = SimpleNamespace(user=SimpleNamespace(id="bot"))
        return PartyMemberMeta(SimpleNamespace(id="native-player", client=client))

    def test_native_na_party_can_be_read(self):
        self.assertIs(self.make_party_meta("NA").region, Region.NORTHAMERICA)

    def test_na_serializes_in_both_v1_region_fields_without_changing_other_settings(self):
        party = self.make_party_meta("EU")
        party.set_custom_key("test-key")
        member = self.make_member_meta()
        member.set_playlist("playlist_showdown_cts_solo", -1)
        before = member.get_prop("Default:MatchmakingInfo_j")["MatchmakingInfo"]

        party_update = party.set_region(Region.NORTHAMERICA)
        member_update = member.set_playlist_region(Region.NORTHAMERICA)

        self.assertEqual({"Default:RegionId_s": "NA"}, party_update)
        self.assertEqual("test-key", party.get_prop("Default:CustomMatchKey_s"))
        actual = json.loads(member_update["Default:MatchmakingInfo_j"])["MatchmakingInfo"]
        expected = copy.deepcopy(before)
        island = json.loads(expected["islandSelection"]["island"])
        island["MatchmakingSettingsV1"]["regionId"] = "NA"
        expected["islandSelection"]["island"] = json.dumps(island)
        expected["islandSelection"]["timestamp"] = actual["islandSelection"]["timestamp"]
        self.assertEqual(expected, actual)

    def test_legacy_and_other_regions_keep_their_exact_values(self):
        member = self.make_member_meta()
        for value in ("NAE", "NAW", "NAC", "EU", "BR", "OCE", "ASIA", "ME"):
            with self.subTest(value=value):
                region = Region(value)
                self.assertIsNot(region, Region.NORTHAMERICA)
                party = self.make_party_meta(value)
                self.assertIs(party.region, region)
                self.assertEqual({"Default:RegionId_s": value}, party.set_region(region))
                update = member.set_playlist_region(region)
                info = json.loads(update["Default:MatchmakingInfo_j"])["MatchmakingInfo"]
                island = json.loads(info["islandSelection"]["island"])
                self.assertEqual(value, island["MatchmakingSettingsV1"]["regionId"])

    def test_unknown_region_still_rejects(self):
        with self.assertRaises(ValueError):
            _ = self.make_party_meta("INVALID").region


if __name__ == "__main__":
    unittest.main()
