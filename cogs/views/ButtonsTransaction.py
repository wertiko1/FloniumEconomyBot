import disnake


class ButtonTransaction(disnake.ui.View):
    def __init__(self, embeds, interaction):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.interaction = interaction
        self.offset = 0
        self.color = 0x2B2D31

        for emb in self.embeds:
            emb.set_footer(text=f'Страница {self.embeds.index(emb) + 1}/{len(self.embeds)}')

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

    @disnake.ui.button(label='Закрыть', style=disnake.ButtonStyle.red)
    async def close(self, _, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        await interaction.delete_original_response()
