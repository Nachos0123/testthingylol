from core.Structures.EpicData    import EpicData
from core.Structures.STWSurvivor import STWSurvivor
from core.util.PowerLevelCurves  import PowerLevelCurves

import aiohttp, platform, json

class stw:
    def __init__(self) -> None:
        self.userAgent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"

    async def get(self, user: 'EpicData') -> dict:

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="POST",
                url=f"https://fngw-mcp-gc-livefn.ol.epicgames.com/fortnite/api/game/v2/profile/{user.accountID}/client/QueryProfile?profileId=campaign",
                headers={
                    "Authorization": f"Bearer {user.accessToken}",
                    "content-type": "application/json"
                },
                json={}
            ) as response:

                if response.status != 200:
                    return False

                data = await response.json()

                plClass = PowerLevel(data)
                PL  = plClass.calculate_power_level()
                VPL = plClass.calculate_venture_power_level()

                return {
                    "PowerLevel"       : PL,
                    "VenturePowerLevel": VPL
                }

class PowerLevel:# 
    def __init__(self, profile):
        profile_items = profile["profileChanges"][0].get("profile", {}).get("items", {})
        items = []

        for item_id, item in profile_items.items():
            item_type = item["templateId"].split(":")[0]

            if item_type == "Worker":
                items.append(STWSurvivor(item))
            else:
                items.append({
                    "id": item_id,
                    "templateId": item["templateId"],
                    "quantity": item["quantity"],
                    "attributes": item["attributes"]
                })

        self.items = items

    def calculate_power_level(self):
        total_FORT_stats = sum(reversed(self.FORT_stats().values()))
        return PowerLevelCurves["homebaseRating"].eval(total_FORT_stats * 4)

    def calculate_venture_power_level(self):
        total_FORT_stats = sum(self.research_FORT_stats(True).values())
        return PowerLevelCurves["homebaseRating"].eval(total_FORT_stats * 4)

    def FORT_stats(self):
        FORT_stats = {"fortitude": 0, "offense": 0, "resistance": 0, "tech": 0}

        for FORT_stat in [self.survivor_FORT_stats(), self.research_FORT_stats(False)]:
            for k in FORT_stat:
                FORT_stats[k] += FORT_stat[k]

        return FORT_stats

    def get_survivor_squads(self):
        squads = {
            "trainingteam": [],
            "fireteamalpha": [],
            "closeassaultsquad": [],
            "thethinktank": [],
            "emtsquad": [],
            "corpsofengineering": [],
            "scoutingparty": [],
            "gadgeteers": [],
        }

        survivors = [i for i in self.items if isinstance(i, STWSurvivor)]

        for survivor in filter(lambda s: s.squad, survivors):
            squads[survivor.squad["name"]].append(survivor)

        return squads

    def survivor_FORT_stats(self):
        survivor_FORT_stats = {"fortitude": 0, "offense": 0, "resistance": 0, "tech": 0}

        for squad in self.get_survivor_squads().values():
            lead_survivor = next((x for x in squad if x.squad["slotIdx"] == 0), None)

            for survivor in squad:
                total_bonus = survivor.power_level
                if survivor.squad["slotIdx"] == 0:
                    total_bonus += survivor.lead_bonus
                elif lead_survivor:
                    total_bonus += survivor.calc_survivor_bonus(lead_survivor)

                squad_type = survivor.squad["type"]
                if squad_type == "medicine":
                    survivor_FORT_stats["fortitude"] += total_bonus
                elif squad_type == "arms":
                    survivor_FORT_stats["offense"] += total_bonus
                elif squad_type == "synthesis":
                    survivor_FORT_stats["tech"] += total_bonus
                elif squad_type == "scavenging":
                    survivor_FORT_stats["resistance"] += total_bonus

        return survivor_FORT_stats

    def research_FORT_stats(self, is_ventures):
        FORT_stats = {"fortitude": 0, "offense": 0, "resistance": 0, "tech": 0}

        for item in self.items:
            # Ensure item is a dictionary before trying to access keys
            if isinstance(item, dict) and "templateId" in item:
                template_id = item["templateId"]
                if template_id.startswith("Stat:"):
                    if (is_ventures and "phoenix" in template_id) or (not is_ventures and "phoenix" not in template_id):
                        if "fortitude" in template_id:
                            FORT_stats["fortitude"] += item["quantity"]
                        elif "resistance" in template_id:
                            FORT_stats["resistance"] += item["quantity"]
                        elif "technology" in template_id:
                            FORT_stats["tech"] += item["quantity"]
                        elif "offense" in template_id:
                            FORT_stats["offense"] += item["quantity"]

        return FORT_stats
        
STW = stw()