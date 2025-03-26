from core.Structures.EpicData import EpicData
from core.constants   import affilaiteCode

import aiohttp, platform, json

async def formatData(data:dict):

    Profile:dict = data.get("profileChanges", [{}])[0].get("profile", {})

    # Layer 1
    created = Profile.get("created", 0)
    updated = Profile.get("updated", 0)

    Attributes:dict = Profile.get("stats", {}).get("attributes", {})

    # Layer 2
    currentSeason = {
        "book_level": Attributes.get("book_level", 0),
        "season_num": Attributes.get("season_num", 0),
        "wins"      : Attributes.get("season", {}).get("numWins", 0),
        "level"     : Attributes.get("level", 0)
    }

    Account = {
        "created": created,
        "updated": updated,
        "info": {
            "lifetimeWins": Attributes.get("lifetime_wins", 0),
            "accountLevel": Attributes.get("accountLevel", 0),
            "lastStwMatch": Attributes.get("last_stw_match_end_datetime", ""),
            "lastMatch"   : Attributes.get("last_match_end_datetime", "")
        }
    }

    Seasons = Attributes.get("past_seasons", [{}])

    seasonsData = []
    for season in Seasons:
        seasonsData.append(
            {
                "bookLevel": season.get("bookLevel", 0),
                "seasonNumber": season.get("seasonNumber", 0),
                "vip": season.get("purchasedVIP", False),
                "wins": season.get("numWins", 0),
                "level": season.get("seasonLevel", 0)
            }
        )

    profileStats = {
        "profile": Account,
        "season": currentSeason,
        "seasons": seasonsData
    }

    return profileStats

class profile:
    def __init__(self) -> None:
        self.userAgent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"

    async def get(self, user: 'EpicData'):

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="POST",
                url=f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{user.accountID}/client/QueryProfile?profileId=common_core",
                headers={
                    "Authorization": f"Bearer {user.accessToken}",
                    "content-type": "application/json"
                },
                json={}
            ) as response:

                if response.status != 200:
                    return False
                
                data = await response.json()
                return await formatData(data)
            
    async def restrictions(self, user: 'EpicData'):

        #https://www.epicgames.com/help/api/restriction-removal/availability
        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="POST",
                url=f"https://www.epicgames.com/help/api/restriction-removal/availability",
                headers={
                    "Authorization": f"Bearer {user.accessToken}",
                    "content-type": "application/json"
                },
                json={}
            ) as response:

                if response.status != 200:
                    text = await response.text()
                    print(text)
                    return
                
                data = await response.json()
                print(data)
        
Profile = profile()