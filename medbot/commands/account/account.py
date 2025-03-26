from core.Auth import Auth
from core.Structures.EpicData import EpicData
from core.methods.affiliate import Affiliate
from core.methods.vbucks import VBucks
from core.methods.friends import Friends
from core.methods.auths import Auths
from core.methods.profile import Profile
from core.methods.stw import STW
from core.methods.skins import Skins

from discord.ext.commands import *
from discord import app_commands
from medbot.managers.bot import Bot

import datetime, discord

class Account(Cog):
    def __init__(self, bot):
        self.bot:discord.Client = bot
        self.footer = self.bot.FooterText
        self.color  = self.bot.SuccessColor

    AccountGroup = app_commands.Group(name="account", description="Fortnite account options")

    ### LOGIN COMMAND
    @AccountGroup.command(
        name="login",
        description="Login to a fortnite account"
    )
    async def login(self, interaction:discord.Interaction):
        
        accessToken = await Auth.fetchAccessToken()
        link, code  = await Auth.createDeviceCode(accessToken=accessToken)

        message = await interaction.response.send_message(
            embed=discord.Embed(
                title="Login Steps",
                description="We use the Epic Games API to make it a seemless login process for you. No login information is received by us. Clicking the link below will take you to the official epic games page. Once you're there, login to your account. Once compeleted, click the confirm button.",
                color=self.color
            ).set_footer(
                text=self.footer
            ),
            view=LoginView(custom=[self.footer, self.color], link=link, code=code)
        )
    
    ### UNFRIEND USERS
    @AccountGroup.command(
        name="unfriend",
        description="Unfriend all the user's on your account"
    )
    async def unfriend(self, interaction:discord.Interaction):
        await interaction.response.send_message("Not Completed")


class LoginView(discord.ui.View):
    def __init__(self, custom:list, link:str, code:str):
        super().__init__(timeout=600.0)

        self.link = link
        self.code = code

        self.footer = custom[0]
        self.color  = custom[1]

        button = discord.ui.Button(
            label="Login URL",
            style=discord.ButtonStyle.url,
            url=self.link
        )
        self.add_item(button)

        self.accountEmbed:discord.Message = None

    async def on_timeout(self):
            
        if self.accountEmbed:
            await self.accountEmbed.delete()

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def ConfirmButton(self, interaction:discord.Interaction, button: discord.ui.Button):
        
        embedList = []
        user:EpicData = await Auth.waitForDeviceCode(self.code)

        await interaction.response.defer(thinking=False)

        affiliateSuccess = await Affiliate.set(user, "tfue")
        vbucksSuccess    = await VBucks.fetch (user)
        authsSuccess     = await Auths.get    (user)
        profile          = await Profile.get  (user)
        stw              = await STW.get      (user)
        skins            = await Skins.get    (user)
        #test            = await Profile.restrictions(user)

        embed=discord.Embed(
            title="Successful Login",
            description=f"You successfully logged into your account. If you'd like to logout, use the /logout command.",
            color=self.color
        ).add_field(
            name="Display Name", value=user.displayName
        ).add_field(
            name="Account ID", value=user.accountID
        ).add_field(
            name="VBucks", value=vbucksSuccess
        ).set_footer(
            text=self.footer
        )

        embedList.append(
            embed
        )

        ### Friends

        FriendData = await Friends.info(user)

        if not FriendData:
            return

        embed = discord.Embed(
            title="Friend Info",
            description="This is a summary of your friend history.",
            color=self.color
        ).add_field(
            name="Total Inbound", value=f"**{FriendData['TotalInbound']}** / **{FriendData['TotalFriends']}**"
        ).add_field(
            name="Total Outbound", value=f"**{FriendData['TotalOutbound']}** / **{FriendData['TotalFriends']}**"
        ).add_field(
            name="Total Favorited", value=f"**{FriendData['TotalFavorited']}** / **{FriendData['TotalFriends']}**"
        ).add_field(
            name="Oldest Friend", value=f"<t:{round(datetime.datetime.strptime(FriendData['OldestFriend'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp())}:R>"
        ).add_field(
            name="Average Friend", value=f"<t:{round(datetime.datetime.strptime(FriendData['AverageFriend'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp())}:R>"
        ).add_field(
            name="Newest Friend", value=f"<t:{round(datetime.datetime.strptime(FriendData['NewestFriend'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp())}:R>"
        )

        embedList.append(
            embed
        )

        ### Connections

        embed = discord.Embed(
            title="Authenticated Connections",
            description="These 3rd Party connections such as xbox, playstation, and nintendo.",
            color=self.color
        )
        for auth in authsSuccess:

            accountID   = auth.get("accountID"  , "")
            _Type       = auth.get("type"       , "")
            displayName = auth.get("displayName", "")
            dateAdded   = auth.get("dateAdded"  , "")

            embed.add_field(
                name="Connection", value=_Type
            ).add_field(
                name="Display Name", value=displayName
            ).add_field(
                name="Date Added", value=f"<t:{round(datetime.datetime.strptime(dateAdded, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())}:R>"
            )

        embedList.append(
            embed
        )

        ### Season Shit

        embed = discord.Embed(
            title="Season Info",
            color=self.color
        )

        def iconType(vip):
            if not vip:
                return "<:free_battlepass:1350855963619492002>"
            
            return "<:battlepass:1350833562462457858>"

        currentSeason = profile.get("season", {})
        seasonDescription = ""
        embed.add_field(
            name="Current Seasons",
            value=f"<:calender_black:1350929664138281092> Season **{currentSeason.get("season_num")}**\n<:battlepass:1350833562462457858> Tier **{currentSeason.get("book_level")}** ({currentSeason.get("level")})\n<:Victory_CrownItemFortnite:1350927790567981077> {currentSeason.get("wins")} Win{'s' if currentSeason.get("wins") > 1 else ''}"
        )

        textList = []

        seasons:list = profile.get("seasons", [{}])
        seasons.reverse()
        for season in seasons:
            
            level = season.get("bookLevel", 0)
            number = season.get("seasonNumber", 0)
            vip = season.get("vip", False)
            wins = season.get("wins", 0)
            maxlevel = season.get("level", 0)

            line1 = f"<:calender_black:1350929664138281092> Season **{number}**"
            line2 = f"{iconType(vip)} Tier **{level}** ({maxlevel})"
            line3 = f"<:Victory_CrownItemFortnite:1350927790567981077> **{wins}** Win{'s' if wins > 1 or wins < 1 else ''}\n\n"

            totalLength = len(line1) + len(line2) + len(line3)
            if totalLength + len(seasonDescription) > 1024:
                textList.append(seasonDescription)
                seasonDescription = ""

            seasonDescription = seasonDescription + f"{line1}\n{line2}\n{line3}"

        textList.append(seasonDescription)

        for i, item in enumerate(textList):
            if i == 0:
                embed.add_field(
                    name="Past Seasons",
                    value=item, inline=False
                )
                if len(embedList) >= 8:
                    embedList.append(embed)
            else:
                embed = discord.Embed(
                    description=item,
                    color=self.color
                )
                if len(embedList) >= 8:
                    embedList.append(embed)

        ### Stats

        stats = profile.get("profile")
        embed = discord.Embed(
            title="Summary",
            color=self.color
        ).add_field(
            name="Account Level",
            value=stats.get("info", {}).get("accountLevel", 0)
        ).add_field(
            name="Lifetime Wins",
            value=stats.get("info", {}).get("lifetimeWins", 0)
        ).add_field(
            name="‎ ",
            value="‎ ",
            inline=False
        ).add_field(
            name="Last Match",
            value=stats.get("info", {}).get("lastMatch", "idk nigga")
        ).add_field(
            name="Last STW Match",
            value=stats.get("info", {}).get("lastStwMatch", 0)
        )

        embedList.append(embed)

        def bars(pl):

            _ = {
                0: "<:progressDull1:1352374865428086875><:progressDull2:1352374866715742228><:progressDull2:1352374866715742228><:progressDull2:1352374866715742228><:progressDull3:1352374868187807858>",
                1: "<:progress1:1352374861900812288><:progressDull2:1352374866715742228><:progressDull2:1352374866715742228><:progressDull2:1352374866715742228><:progressDull3:1352374868187807858>",
                2: "<:progress1:1352374861900812288><:progress2:1352374863024750652><:progressDull2:1352374866715742228><:progressDull2:1352374866715742228><:progressDull3:1352374868187807858>",
                3: "<:progress1:1352374861900812288><:progress2:1352374863024750652><:progress2:1352374863024750652><:progressDull2:1352374866715742228><:progressDull3:1352374868187807858>",
                4: "<:progress1:1352374861900812288><:progress2:1352374863024750652><:progress2:1352374863024750652><:progress2:1352374863024750652><:progressDull3:1352374868187807858>",
                5: "<:progress1:1352374861900812288><:progress2:1352374863024750652><:progress2:1352374863024750652><:progress2:1352374863024750652><:progress3:1352374864107012159>"
            }
            decimalPoint = round(pl % 1, 2)
            filledBars = min(int(decimalPoint / .2), 5)
            progress = _[filledBars]
            return progress

        embed = discord.Embed(
            title="STW Info",
            color=self.color
        ).add_field(
            name="Power Level",
            value=f"**{int(stw.get("PowerLevel", 1))}**\n{bars(144.7)}"
        ).add_field(
            name="Venture Power Level",
            value=f"**{int(stw.get("VenturePowerLevel", 1))}**\n{bars(stw.get("VenturePowerLevel", 1))}"
        )

        embedList.append(embed)

        await interaction.channel.send(
            embeds=embedList
        )
            
async def setup(bot: Bot):
    await bot.add_cog(Account(bot))