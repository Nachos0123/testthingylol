from core.Structures.EpicData import EpicData

import aiohttp, platform, json

class stw:
    def __init__(self) -> None:
        self.userAgent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"

    async def set(self, user: 'EpicData', affiliateCode: str) -> dict:

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="POST",
                url=f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{user.accountID}/client/SetAffiliateName?profileId=common_core",
                headers={
                    "Authorization": f"Bearer {user.accessToken}",
                    "content-type": "application/json"
                }
            ) as response:

                if response.status != 200:
                    return False

                data = await response.json()
                with open('stw.json', 'w') as f:
                    json.dump(data, f, indent=4)
        
STW = stw()