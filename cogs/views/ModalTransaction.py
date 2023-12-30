import disnake
from ..utils.Data import DataBase


class ModalComment(disnake.ui.Modal):
    def __init__(self, money: int, member: disnake.Member, sender: disnake.Member):
        self.db = DataBase()
        self.money = money
        self.member = member
        self.color = 0x2B2D31
        self.sender = sender
        components = [
            disnake.ui.TextInput(
                label="Комментарий",
                placeholder="Введите комментарий к платежу",
                custom_id="comment",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=64,
            ),
        ]
        super().__init__(title="Комментарий", custom_id="comment_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        comment = inter.text_values["comment"]
        user = await self.db.get_user(self.sender)
        await self.db.update_money(self.sender, -self.money)
        await self.db.update_money(self.member, self.money)
        await self.db.add_transaction(self.member.id, self.sender.id, self.money, comment)
        embed = disnake.Embed(title='Перевод средств',
                              description=f'**{self.sender.display_name}** ➡ **{self.member.display_name}**',
                              color=self.color).set_thumbnail(url=f'https://render.crafty.gg/3d/bust/{user[5]}')
        embed.add_field(name=f'Сумма', value=f'```{self.money}```')
        embed.add_field(name='Комментарий', value=f'```{comment}```')
        await inter.response.send_message(embed=embed)
