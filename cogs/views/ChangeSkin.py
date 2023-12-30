import disnake
from ..utils.Data import DataBase


class ModalSkin(disnake.ui.Modal):
    def __init__(self):
        self.color = 0x2B2D31
        self.db = DataBase()
        components = [
            disnake.ui.TextInput(
                label="Никнейм",
                placeholder="Введите лицензионный никнейм",
                custom_id="nickname",
                style=disnake.TextInputStyle.short,
                min_length=5,
                max_length=16,
            ),
        ]
        super().__init__(title="Никнейм", custom_id="nickname_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        nick = inter.text_values["nickname"]
        user = await self.db.get_user(inter.author)
        await self.db.change_skin(inter.author, nick)
        embed = disnake.Embed(title='Скин успешно изменен',
                              description=f'```{user[5]} ➡ {nick}```',
                              color=self.color).set_thumbnail(url=f'https://render.crafty.gg/3d/bust/{nick}')
        await inter.response.edit_message(embed=embed, view=None)


class ButtonSkin(disnake.ui.View):
    def __init__(self, inter, timeout=30):
        self.interaction = inter
        self.color = 0x2B2D31
        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if self.interaction.id != interaction.user.id:
            embed = disnake.Embed(color=self.color)
            embed.description = (
                f"{interaction.author.mention}, Вы **не** можете использовать эту кнопку, "
                f"так как она предназначена для пользователя {self.interaction.mention}!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        return True

    @disnake.ui.button(label='Ввод никнейма', style=disnake.ButtonStyle.grey, custom_id='input_nick')
    async def input_nick(self, button: disnake.ui.Button, inter):
        await inter.response.send_modal(ModalSkin())
