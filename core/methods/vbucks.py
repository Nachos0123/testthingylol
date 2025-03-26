from core.Structures.EpicData import EpicData
from core.constants   import affilaiteCode

import aiohttp, platform, json

class vbucks:
    def __init__(self) -> None:
        self.userAgent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"

    async def fetch(self, user: 'EpicData') -> dict:

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="POST",
                url=f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{user.accountID}/client/QueryProfile?profileId=common_core&rvn=-1",
                headers={
                    "Authorization": f"Bearer {user.accessToken}",
                    "content-type": "application/json"
                },
                json={}
            ) as response:

                if response.status != 200:
                    print(response.text)
                    return False

                data = await response.json()
                return await self.format(data)
            
    async def format(self, response:dict):
        
        cats = [
            "Currency:MtxPurchased",
            "Currency:MtxEarned",
            "Currency:MtxGiveaway",
            "Currency:MtxPurchaseBonus"
        ]

        TotalVbucks = 0
        Items:dict = response.get("profileChanges", [{}])[0].get("profile", {}).get("items", {})

        for ItemID, ItemData, in Items.items():

            if ItemData.get("templateId") in cats:
                TotalVbucks += ItemData.get("quantity", 0)

        return TotalVbucks
        
VBucks = vbucks()