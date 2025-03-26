import discord, json, os, asyncpg
from discord.ext import commands

class Bot(commands.Bot):

    def __init__(self):

        super().__init__(
            help_command=None,
            command_prefix="!",
            intents=discord.Intents.all(),
            activity=discord.Activity(
                type=discord.ActivityType.streaming,
                name="discord.gg/heals", 
                url="https://twitch.tv/tfue"
            ),
            ### If you want to remove the activity you can set the status with the code below
            # status=discord.Status.dnd (sets to do not disturb)
        )

        ### Getting the configuration file and turning it into a python dictionary

        print(os.getcwd())

        with open('medbot/managers/config.json') as file:
            data = json.load(file)

        ### Setting the configuration data

        # BotAuth
        self.BotAuth = data['BotAuth']

        self.Token = self.BotAuth['Token']

        # EmbedSettings
        self.EmbedSettings = data['EmbedSettings']

        self.SuccessColor = discord.Colour.from_str(self.EmbedSettings['SuccessColor'])
        self.ErrorColor   = discord.Colour.from_str(self.EmbedSettings['ErrorColor'])
        self.FooterText   = self.EmbedSettings['FooterText']

        # Database
        self.DatabaseConfig = data['DatabaseConfig']

        self.ModuleFolder:str = self.DatabaseConfig['ModuleFolder']
        self.SchemaPath = self.DatabaseConfig['SchemaPath']

        self.db = None
        
        self.run()

    async def setup_hook(self):
        
        #self.db = await asyncpg.create_pool(user='postgres', password='Medbot1234', database='medbot', port=5432, host="127.0.0.1")

        #try:
        #    if os.path.getsize(self.SchemaPath) > 0:
        #        with open(self.SchemaPath) as file:
        #            await self.db.execute(file.read())
        #            print("Database schema updated.")
        #except Exception as error:
        #    print(f"Schema file couldn't be found.\nError: {error}")
        
        for folder in os.listdir(self.ModuleFolder):
            if folder.endswith(".py"):
                FileName = folder[:-3]
                try:
                    a = self.ModuleFolder.replace("/", ".").replace("..", ".")[1:]
                    await self.load_extension(f"{a}.{folder}")
                    print(f"Loaded cog {self.ModuleFolder}.{FileName}")
                except Exception as error:
                    print(error)
            else:
                for file in os.listdir(f"{self.ModuleFolder}/{folder}"):
                    if file.endswith(".py"):
                        FileName = file[:-3]
                        try:
                            a = self.ModuleFolder.replace("/", ".").replace("..", ".")[1:]
                            await self.load_extension(f"{a}.{folder}.{FileName}")
                            print(f"Loaded cog {self.ModuleFolder}.{folder}.{FileName}")
                        except Exception as error:
                            print(error)

    def run(self):
        super().run(
            token=self.Token,
            reconnect=True
        )

    async def on_ready(self):
        print("Bot has started...")

    #async def on_message(self, message: discord.Message):
#
    #    if f"{self.user.mention}" in message.content:
    #        await message.reply(
    #            embed=discord.Embed(
    #                title="Medkit Skin-Checker",
    #                description="This bot allows you to access certain things regarding your account. Such as see your skins, vbucks, game history, and other information that can be useful.",
    #                color=self.SuccessColor
    #            ).set_footer(
    #                text=self.FooterText
    #            )
    #        )