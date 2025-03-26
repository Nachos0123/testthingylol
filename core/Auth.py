
# Project Imports

from core.Structures.EpicData import EpicData
from core.constants   import SWITCH_TOKEN, IOS_TOKEN

# Python Imports

import platform, json, aiohttp, asyncio

class DeviceCode:
    def __init__(self):
        self.userAgent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"

    async def handler(self) -> None:

        # Getting the access_token allowing us to authenticate as a user
        accessToken = await self.fetchAccessToken()
        
        # Creates the user authorization link
        link, code = await self.createDeviceCode()
        print(link)

        # Waits for the user to login to their account, once completed returns their data
        user = await self.waitForDeviceCode(code)
        return user

        # Turns the EpicData into a dictionary for me to print
        # data = EpicData.to_dict(user)
        # print(json.dumps(data, indent=4))

    async def fetchAccessToken(self): # Step 1
        
        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="POST",
                url="https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"basic {SWITCH_TOKEN}"
                },
                data={
                    "grant_type": "client_credentials"
                }
            ) as response:

                data:dict = await response.json()
                return data.get('access_token', False)
        
    async def createDeviceCode(self, accessToken:str): # Step 2

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="POST",
                url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization",
                headers={
                    "Authorization": f"bearer {accessToken}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            ) as response:
                
                data:dict = await response.json()
                print(data)
                return data.get('verification_uri_complete', False), data.get('device_code')
            
    async def waitForDeviceCode(self, code:str) -> str: # Step 3

        while True:

            async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

                async with session.request(
                    method="POST",
                    url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
                    headers={
                        "Authorization": f"basic {SWITCH_TOKEN}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={
                        "grant_type": "device_code",
                        "device_code": code
                    }
                ) as response:
                    
                    # Token Data
                    data = await response.json()
                    if response.status == 200:
                        break

                    await asyncio.sleep(5)

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="GET",
                url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange",
                headers={
                    "Authorization": f"bearer {data['access_token']}"
                }
            ) as response:
                
                # Exchange Data
                data = await response.json()

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="POST",
                url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
                headers={
                    "Authorization": f"basic {IOS_TOKEN}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "grant_type": "exchange_code",
                    "exchange_code": data["code"]
                }
            ) as response:
                
                data = await response.json()
                return EpicData.from_dict(data=data)

    async def createExchangeCode(self, user: 'EpicData') -> str: # Step 4
        
        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="GET",
                url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange",
                headers={
                    "Authorization": f"bearer {user.accessToken}"},
            ) as response:
                
                data:dict = await response.json()
                return data.get('code', False)
            
Auth = DeviceCode()