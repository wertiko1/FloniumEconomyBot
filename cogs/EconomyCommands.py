import disnake
import json, datetime, time
from disnake.ext import commands
from .utils.Data import DataBase
from .configs import Config
from .views.PaginatorEco import Paginator
from .views.ModalTransaction import ModalComment
from .views.ButtonsTransaction import ButtonTransaction
from .views.ChangeSkin import ButtonSkin
from .views.PaginatorFines import PaginatorView


def load_fine_data(filename, key):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get(key, 0)
    except FileNotFoundError:
        return 0


def save_fine_data(filename, key, value):
    data = {key: value}
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file)


class EcoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DataBase()
        self.color = 0x2B2D31

    @commands.Cog.listener()
    async def on_command_error(self, interaction, error):
        if isinstance(error, commands.MissingRole):
            embed = disnake.Embed(
                description=f'**{interaction.user.display_name}** у вас недостаточно прав для выполнеия данной команды!',
                color=disnake.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name='баланс', description='Посмотреть баланс')
    async def balance(self, inter,
                      member: disnake.Member = commands.Param(default=None, name='пользователь',
                                                              description="Укажите пользователя")):
        if not member:
            member = inter.author
        user = await self.db.get_user(member)
        url = f'https://render.crafty.gg/3d/bust/{user[5]}'
        embed = disnake.Embed(color=self.color, title=f'{member.display_name}').set_thumbnail(
            url=f'https://render.crafty.gg/3d/bust/{user[5]}')
        embed.add_field(name='Деньги', value=f'```{user[1]}```')
        await inter.response.send_message(embed=embed)

    @commands.has_any_role(Config.roles['bank'])
    @commands.slash_command(name='выдать', description='Выдать валюту')
    async def give(self, interaction,
                   member: disnake.Member = commands.Param(name='пользователь', description="Укажите пользователя"),
                   money: int = commands.Param(name='монеты', description="Укажите кол-во монет")):
        user = await self.db.get_user(member)
        if user:
            await self.db.update_money(member, money)
            embed = disnake.Embed(color=self.color, title=f'{member.display_name} пополнил баланс').set_thumbnail(
                url=f'https://render.crafty.gg/3d/bust/{user[5]}')
            embed.add_field(name='Зачислено', value=f'```{money}```')
            embed.set_footer(icon_url=f'https://cravatar.eu/avatar/{interaction.author.display_name}',
                             text=f'Банкир {interaction.author.display_name}')
            await interaction.response.send_message(embed=embed)

    @commands.slash_command(name='топ', description='Посмотреть топ пользователей')
    async def top(self, interaction):
        top = await self.db.get_top()
        embeds = []
        loop_count = 0
        n = 0
        text = ''
        for user in top:
            n += 1
            loop_count += 1
            member = self.bot.get_user(user[0])
            text += f'**{n}.** {member.mention} - {user[1]}\n'
            if loop_count % 10 == 0 or loop_count - 1 == len(top) - 1:
                embed = disnake.Embed(color=self.color, title='Топ пользователей')
                embed.description = text
                embed.set_thumbnail(url=interaction.guild.icon)
                embeds.append(embed)
                text = ''
        view = Paginator(embeds, interaction.author, True)
        await interaction.response.send_message(embed=embeds[0], view=view)

    @commands.slash_command(name='перевести', description='Перевести деньги')
    async def transfer(self, interaction,
                       member: disnake.Member = commands.Param(name='пользователь',
                                                               description="Укажите пользователя"),
                       money: int = commands.Param(name='монеты', description="Укажите кол-во монет")):
        if member == interaction.author:
            return await interaction.response.send_message('Вы не можете перевести деньги самому себе!', ephemeral=True)
        if money <= 0:
            return await interaction.response.send_message('Неверная сумма!', ephemeral=True)
        user = await self.db.get_user(interaction.author)
        if user[1] < money:
            return await interaction.response.send_message('У вас недостаточно денег!', ephemeral=True)
        await interaction.response.send_modal(ModalComment(money=money, member=member, sender=interaction.author))

    @commands.slash_command(name='переводы', description="Посмотреть переводы")
    async def transactions(self, interaction):
        embeds = await self.db.get_embeds(interaction)
        if len(embeds) == 0:
            return await interaction.response.send_message(embed=disnake.Embed(title='Ошибка',
                                                           description=f'{interaction.author.mention} '
                                                           f'у вас нет **транзакций**\nСовершите **перевод** '
                                                           f'чтобы он отобразился здесь',
                                                           color=self.color), ephemeral=True)
        view = ButtonTransaction(embeds, interaction)
        await view.update_button()
        await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    @commands.slash_command(name='сменить-скин', description='Сменить ваш скин')
    async def change_skin(self, interaction):
        user = await self.db.get_user(interaction.author)
        embed = disnake.Embed(title='Смена скина', description='Ваш скин на картинке\n'
                                                               'Чтобы сменить отображение скина\n'
                                                               'Пропишите **никнейм лицензионного джава игрока**!',
                              color=self.color).set_thumbnail(url=f'https://render.crafty.gg/3d/bust/{user[5]}')
        embed.add_field(name='Например', value='```Notch```')
        await interaction.response.send_message(embed=embed, view=ButtonSkin(inter=interaction.author))

    @commands.has_any_role(Config.roles['fsb'])
    @commands.slash_command(name='выдать-штраф', description='Выдать штраф пользователю')
    async def give_fine(self, inter, victim: disnake.Member = commands.Param(name='пострадавший',
                                                                             description="Укажите пострадавшего"),
                        guilty: disnake.Member = commands.Param(name='виновный', description="Укажите виновного"),
                        amount: int = commands.Param(name='сумма', description="Сумма штрафа"),
                        reason: str = commands.Param(name='причина', description="Причина штрафа")):
        num = load_fine_data('fines.json', 'fine') + 1
        save_fine_data('fines.json', 'fine', num)
        current_datetime = datetime.datetime.now()
        new_datetime = current_datetime + datetime.timedelta(days=7)
        time_fine = str(time.mktime(time.strptime(new_datetime.strftime("%d.%m.%Y %H:%M:%S"), "%d.%m.%Y %H:%M:%S")))[
                    :10]
        await self.db.add_fine(number=num, user1=victim, user2=guilty, amount=amount, reason=reason,
                               time_fine=int(time_fine))
        await inter.response.send_message(f'Штраф успешно выдан!', ephemeral=True)
        channel = inter.guild.get_channel(Config.FINE_CHANNEL)
        embed = disnake.Embed(title=f'Игроку {guilty.display_name} выписан штраф #{num}',
                              description=f'Пострадавший **{victim.mention}**',
                              color=0xFF3C18).set_thumbnail(
            url=f'https://render.crafty.gg/3d/bust/{guilty.display_name}')
        embed.add_field(name='Сумма штрафа', value=f'```{amount}```')
        embed.add_field(name='Причина штрафа', value=f'```{reason}```')
        embed.add_field(name='Срок выплаты', value=f'<t:{time_fine}:f>')
        user = await self.db.get_user(inter.author)
        embed.set_footer(icon_url=f'https://cravatar.eu/avatar/{user[5]}', text=f'Выписал {inter.author.display_name}')
        await channel.send(f'{guilty.mention}')
        await channel.send(embed=embed)

    @commands.slash_command(name='штрафы', description='Посмотреть штрафы')
    async def fines(self, inter):
        fines = await self.db.fine_embeds(inter)
        if len(fines) == 0:
            return await inter.response.send_message(
                embed=disnake.Embed(title='Ошибка', description=f'{inter.author.mention}, у вас нет **штрафов**',
                                    color=self.color), ephemeral=True)
        view = PaginatorView(fines, inter)
        await view.update_button()
        await inter.response.send_message(embed=fines[0], view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(EcoCommands(bot))
