import disnake


class Paginator(disnake.ui.View):
    def __init__(self, embeds, author, footer: bool, timeout=30.0):
        self.embeds = embeds
        self.author = author
        self.footer = footer
        self.timeout = timeout
        self.page = 0
        super().__init__(timeout=self.timeout)
        if self.footer:
            for emb in self.embeds:
                emb.set_footer(text=f'Страница {self.embeds.index(emb) + 1} из {len(self.embeds)}')

    @disnake.ui.button(label='◀️', style=disnake.ButtonStyle.grey)
    async def back(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if self.author.id == interaction.author.id:
            if self.page == 0:
                self.page = len(self.embeds) - 1
            else:
                self.page -= 1
        else:
            return

        await self.button_callback(interaction)

    @disnake.ui.button(label='▶️', style=disnake.ButtonStyle.grey)
    async def next(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if self.author.id == interaction.author.id:
            if self.page == len(self.embeds) - 1:
                self.page = 0
            else:
                self.page += 1
        else:
            return

        await self.button_callback(interaction)

    async def button_callback(self, interaction):
        await interaction.response.edit_message(embed=self.embeds[self.page])
