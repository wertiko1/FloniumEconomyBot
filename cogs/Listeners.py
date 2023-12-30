import time
import datetime
import disnake
from disnake.ext import commands, tasks
from .configs import Config
from .utils.Data import DataBase


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DataBase()
        self.count = 0

    @tasks.loop(seconds=10)
    async def user_db(self):
        guild = self.bot.get_guild(Config.SERVER_ID)
        for member in guild.members:
            if member.bot:
                continue
            results = await self.db.get_user(member)
            if not results:
                await self.db.add_user(member)

    @commands.Cog.listener()
    async def on_slash_command_error(self, interaction: disnake.CommandInteraction, error):
        embed = disnake.Embed(
            title=f'{interaction.user.display_name}',
            description=f'Неизвестная ошибка!',
            color=disnake.Color.red())
        if isinstance(error, commands.MissingAnyRole):
            embed = disnake.Embed(
                title=f'{interaction.user.display_name}',
                description='У вас недостаточно прав для выполнения данной команды!',
                color=disnake.Color.red())
        await interaction.send(embed=embed, ephemeral=True)

    @tasks.loop(seconds=60)
    async def update_fines(self):
        current_datetime = datetime.datetime.now()
        time_fine = str(
            time.mktime(time.strptime(current_datetime.strftime("%d.%m.%Y %H:%M:%S"), "%d.%m.%Y %H:%M:%S")))[:10]
        result = await self.db.get_fines()
        for fine in result:
            if fine[1] == 0 and fine[8] < int(time_fine):
                await self.db.update_fine(fine[0])
                channel = self.bot.get_channel(Config.FINE_CHANNEL)
                guild = self.bot.get_guild(Config.SERVER_ID)
                member = guild.get_member(fine[3])
                user = await self.db.get_user(member)
                await channel.send(f"{member.mention}")
                total_fine = fine[0] + fine[0]
                embed = disnake.Embed(title=f"Вы просрочили штраф #{total_fine}",
                                      color=0xFF3C18,
                                      timestamp=current_datetime).set_thumbnail(
                    url=f'https://render.crafty.gg/3d/bust/{user[5]}')
                embed.add_field(name=f"Теперь сумма", value=f'```{fine[6]}```')
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        self.user_db.start()
        self.update_fines.start()


def setup(bot):
    bot.add_cog(Listeners(bot))
