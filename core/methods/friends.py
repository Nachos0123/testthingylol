from core.Structures.EpicData import EpicData
from core.constants   import affilaiteCode

import aiohttp, platform, asyncio, datetime

class friends:
    def __init__(self) -> None:
        self.userAgent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"

    async def delete(self, user: 'EpicData'):

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="GET",
                url=f"https://friends-public-service-prod.ol.epicgames.com/friends/api/public/friends/{user.accountID}",
                headers={
                    "Authorization": f"Bearer {user.accessToken}"
                }
            ) as response:

                if response.status != 200:
                    return False

                friends = await response.json()
            
            deleted = 0
            total   = 0
            for friend in friends:
                print(friend)
                asyncio.sleep(1)

                async with session.request(
                    method="DELETE",
                    url=f"https://friends-public-service-prod.ol.epicgames.com/friends/api/public/friends/{user.accountID}/{friend['accountId']}",
                    headers={
                        "Authorization": f"Bearer {user.accessToken}"
                    }
                ) as response:
                    
                    if response.status == 204:
                        deleted += 1

                    elif response.status == 429: # Ratelimited

                        print("waiting")
                        await asyncio.sleep(int(response.headers.get('Retry-After')))
                        
                        async with session.request(
                            method="DELETE",
                            url=f"https://friends-public-service-prod.ol.epicgames.com/friends/api/public/friends/{user.accountID}/{friend['accountId']}",
                            headers={
                                "Authorization": f"Bearer {user.accessToken}"
                            }
                        ) as response:
                            
                            if response.status == 204:
                                deleted += 1

                            elif response.status == 429:
                                print("WHAT THE FUCK")

                    total += 1
            
            return [total, deleted]
        
    async def info(self, user: 'EpicData'):

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="GET",
                url=f"https://friends-public-service-prod.ol.epicgames.com/friends/api/public/friends/{user.accountID}",
                headers={
                    "Authorization": f"Bearer {user.accessToken}"
                }
            ) as response:
                
                if response.status != 200:
                    return False
                
                Friends = await response.json()

            # Count
            TotalFriends   = 0
            TotalInbound   = 0
            TotalOutbound  = 0
            TotalFavorited = 0

            # Date
            FriendDates    = []
            OldestFriend   = ""
            NewestFriend   = ""
            AverageFriend  = ""

            for Friend in Friends:

                FriendDates.append(datetime.datetime.strptime(Friend['created'], "%Y-%m-%dT%H:%M:%S.%fZ"))

                if Friend['favorite']:
                    TotalFavorited += 1

                if Friend['direction'] == 'INBOUND':
                    TotalInbound += 1

                else:
                    TotalOutbound += 1

                TotalFriends += 1

            OldestFriend = str(min(FriendDates)).split(".")[0]
            NewestFriend = str(max(FriendDates)).split(".")[0]

            Timestamps = [Date.timestamp() for Date in FriendDates]
            AverageTimestamp = sum(Timestamps) / len(Timestamps)

            AverageFriend = str(datetime.datetime.fromtimestamp(AverageTimestamp)).split(".")[0]

            return {
                'TotalFriends'  : TotalFriends,
                'TotalInbound'  : TotalInbound,
                'TotalOutbound' : TotalOutbound,
                'TotalFavorited': TotalFavorited,

                'OldestFriend'  : str(OldestFriend),
                'AverageFriend' : str(AverageFriend),
                'NewestFriend'  : str(NewestFriend)
            }
        
Friends = friends()