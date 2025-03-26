from core.Structures.EpicData import EpicData
from core.constants   import affilaiteCode

import aiohttp, platform, json

class auths:
    def __init__(self) -> None:
        self.userAgent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"

    async def sortAuths(self, auth:str):

        if auth == "psn":
            return "Playstation"
        elif auth == "ubisoft":
            return "Ubisoft"
        
        return auth

    async def get(self, user: 'EpicData'):

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="GET",
                url=f"https://account-public-service-prod03.ol.epicgames.com/account/api/public/account/{user.accountID}/externalAuths",
                headers={
                    "Authorization": f"Bearer {user.accessToken}"
                }
            ) as response:

                if response.status != 200:
                    return False

                data = await response.json()


            connections = []
            for auth in data:
                _Type = await self.sortAuths(auth.get("type", ""))
                connections.append(
                    {
                        "accountID": f"{auth.get("accountId", "")}",
                        "type": _Type,
                        "displayName": f"{auth.get("externalDisplayName", "")}",
                        "dateAdded": f"{str(auth.get("dateAdded", ""))}"
                    }
                )

            return connections
        
    async def create(self, user:'EpicData'):

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="GET",
                url=f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{user.accountID}/deviceAuth",
                headers={
                    "Authorization": f"Bearer {user.accessToken}",
                    "Content-Type": "application/json"
                }
            ) as response:

                if response.status != 200:
                    return False
                
                data = await response.json()

            print(data)
        
Auths = auths()