import disnake
import datetime
import time
from .views.PaginatorEco import Paginator
from disnake.ext import commands
from .utils.Data import DataBase


class Reputation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = DataBase()
        self.color = 0x2B2D31

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent):
        guild = await self.bot.fetch_guild(payload.guild_id)
        channel = await guild.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        author_id = message.author.id
        if payload.emoji.id == 1186357016659234827:
            rep = 1
        elif payload.emoji.id == 1186357309048377504:
            rep = -1
        else:
            return
        if payload.user_id == author_id or message.author.bot:
            return
        member = payload.member
        user = await self.db.get_user(member)
        current_datetime = datetime.datetime.now()
        time_reaction = str(time.mktime(
            time.strptime(current_datetime.strftime("%d.%m.%Y %H:%M:%S"), "%d.%m.%Y %H:%M:%S")))[:10]
        if user[6] < int(time_reaction):
            new_datetime = current_datetime + datetime.timedelta(hours=1)
            time_reaction = str(time.mktime(
                time.strptime(new_datetime.strftime("%d.%m.%Y %H:%M:%S"), "%d.%m.%Y %H:%M:%S")))[:10]
            time_reaction = int(time_reaction)
            await self.db.add_time(member=user[0], time_rep=time_reaction, rep=rep, member_rep=author_id)

    @commands.slash_command(name='лидеры', description='Посмотреть топ по репутациям')
    async def reputation_top(self, inter):
        top = await self.db.get_rep_top()
        embeds = []
        loop_count = 0
        n = 0
        text = ''
        for user in top:
            n += 1
            loop_count += 1
            member = self.bot.get_user(user[0])
            text += f'**{n}.** {member.mention} - {user[7]} 🧡\n'
            if loop_count % 10 == 0 or loop_count - 1 == len(top) - 1:
                embed = disnake.Embed(color=self.color, title='Топ репутаций')
                embed.description = text
                embed.set_thumbnail(url=inter.guild.icon)
                embeds.append(embed)
                text = ''
        view = Paginator(embeds, inter.author, True)
        await inter.response.send_message(embed=embeds[0], view=view)


def setup(bot):
    bot.add_cog(Reputation(bot))
