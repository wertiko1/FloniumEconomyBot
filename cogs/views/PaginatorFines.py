import disnake
from ..utils.Data import DataBase
import datetime


class PaginatorView(disnake.ui.View):
    def __init__(self, embeds, interaction):
        super().__init__(timeout=300)
        self.embeds = embeds
        self.interaction = interaction
        self.db = DataBase()
        self.color = 0x2B2D31
        self.offset = 0

        for emb in self.embeds:
            emb.set_footer(text=f'Штраф {self.embeds.index(emb) + 1}/{len(self.embeds)}')

    async def update_button(self):
        offset = self.offset
        is_first_page = offset == 0
        is_last_page = offset == len(self.embeds) - 1

        self.back.disabled = is_first_page
        self.forward.disabled = is_last_page

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if self.interaction.author.id != interaction.user.id:
            embed = disnake.Embed(color=0xff0000).set_author(name="Ошибка")
            embed.description = (
                f"{interaction.author.mention}, Вы **не** можете использовать эту кнопку, "
                f"так как она предназначена для пользователя {self.interaction.author.mention}!")
            embed.set_thumbnail(url=interaction.author.display_avatar)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        return True

    @disnake.ui.button(label='Назад', style=disnake.ButtonStyle.grey)
    async def back(self, _, interaction: disnake.MessageInteraction):
        self.offset -= 1
        await self.update_button()
        await interaction.response.edit_message(embed=self.embeds[self.offset], view=self)

    @disnake.ui.button(label='Вперед', style=disnake.ButtonStyle.grey)
    async def forward(self, _, interaction: disnake.MessageInteraction):
        self.offset += 1
        await self.update_button()
        await interaction.response.edit_message(embed=self.embeds[self.offset], view=self)

    @disnake.ui.button(label='Оплатить', style=disnake.ButtonStyle.primary)
    async def close(self, _, interaction: disnake.MessageInteraction):
        embed = self.embeds[self.offset]
        ind = str(embed.title).find('#')
        number = int(embed.title[ind + 1:])
        fine = await self.db.get_fine(number=number)
        saver = interaction.guild.get_member(fine[2])
        sender = interaction.guild.get_member(fine[3])
        user = await self.db.get_user(sender)
        if user[1] < fine[6]:
            embed = disnake.Embed(title=f'У вас недостаточно средств!',
                                  color=self.color)
            return await interaction.response.edit_message(embed=embed)
        if fine[1] != 1:
            await self.db.buy_fine(number=number, mode=1)
            await self.db.update_money(user=sender, money=(-fine[6]))
            await self.db.update_money(user=saver, money=fine[6])
            embed = disnake.Embed(title=f'Вы успешно оплатили штраф #{fine[0]}',
                                  description=f'Пострадавший {saver.mention}',
                                  color=self.color,
                                  timestamp=datetime.datetime.now())
            embed.add_field(name=f"Сумма", value=f'```{fine[6]}```')
            await interaction.response.edit_message(embed=embed)
        else:
            embed = disnake.Embed(title=f'Вы уже оплатили штраф #{fine[0]}',
                                  color=self.color,
                                  timestamp=datetime.datetime.now())
            await interaction.response.edit_message(embed=embed)

    @disnake.ui.button(label='Закрыть', style=disnake.ButtonStyle.red)
    async def clos(self, _, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        await interaction.delete_original_response()
