from core.Structures.EpicData import EpicData
from core.constants   import affilaiteCode

import aiohttp, platform, json

class affiliate:
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
                },
                json={
                    "affiliateName": affiliateCode
                }
            ) as response:

                if response.status != 200:
                    return False

                data = await response.json()
                return await self.check(data)
            
    async def check(self, response):

        if isinstance(response, str):
            if '403' in response:
                return False
            
            return False
        
        return True
        
Affiliate = affiliate()