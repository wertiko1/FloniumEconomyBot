import disnake
from disnake.ext import commands
from .utils.Data import DataBase


class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DataBase()
        self.color = 0x2B2D31

    # @commands.slash_command(name="банк", description="Информация о банке")
    # async def info(self, inter):
    #     result = await self.db.select_info()
    #     embed = disnake.Embed(title='Банк', color=self.color).set_thumbnail(url=inter.guild.icon)
    #     embed.add_field(name='Всего средств', value=f'```{result[0]}```')
    #     embed.add_field(name='Всего штрафов', value=f'```{result[1]}```')
    #     await inter.response.send_message(embed=embed)
    #
    # @commands.slash_command(name="хелп", description="Информация о системе")
    # async def help(self, inter):
    #     embed = disnake.Embed(title='Flonium.space', color=self.color).set_thumbnail(url=inter.guild.icon)
    #     await inter.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(UserCommands(bot))
