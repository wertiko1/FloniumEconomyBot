import aiosqlite
import disnake
import datetime


class DataBase:
    def __init__(self):
        self.name = 'dbs/users.db'
        self.color = 0x2B2D31

    async def create_table(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            # fine_mode
            # 0 - неоплачен, 1 - оплачен, 2 - просрочен
            query = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                money INTEGER,
                fines INTEGER,
                warns INTEGER,
                voice_time INTEGER,
                skin TEXT,
                time INTEGER,
                reputation INTEGER
            );
            CREATE TABLE IF NOT EXISTS fines (
                number INTEGER PRIMARY KEY,
                fine_mode INTEGER,
                id1 INTEGER,
                id2 INTEGER,
                name1 TEXT,
                name2 TEXT,
                amount INTEGER,
                reason TEXT,
                time INTEGER
            );
            CREATE TABLE IF NOT EXISTS transactions (
                number INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                saver_id INTEGER,
                amount INTEGER,
                comment TEXT,
                time INTEGER
            );
            '''
            await cursor.executescript(query)
            await db.commit()

    async def add_user(self, user: disnake.Member):
        async with aiosqlite.connect(self.name) as db:
            if not await self.get_user(user):
                cursor = await db.cursor()
                query = 'INSERT INTO users (id, money, fines, warns, voice_time, skin, time, reputation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
                await cursor.execute(query, (user.id, 0, 0, 0, 0, user.display_name, 0, 5))
                await db.commit()

    async def add_time(self, member: int, time_rep: int, rep: int, member_rep: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'UPDATE users SET time = ? WHERE id = ?'
            await cursor.execute(query, (time_rep, member))
            query = 'UPDATE users SET reputation = reputation + ? WHERE id = ?'
            await cursor.execute(query, (rep, member_rep))
            await db.commit()

    async def get_rep_top(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM users ORDER BY reputation DESC'
            await cursor.execute(query)
            return await cursor.fetchall()

    async def add_fine(self, number: int, user1: disnake.Member, user2: disnake.Member, amount: int, reason: str,
                       time_fine: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'INSERT INTO fines (number, fine_mode, id1, id2, name1, name2, amount, reason, time) ' \
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
            await cursor.execute(query, (
                number, 0, user1.id, user2.id, user1.display_name, user2.display_name, amount, reason, time_fine))
            await db.commit()

    async def get_fine(self, number: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM fines WHERE number = ?'
            await cursor.execute(query, (number,))
            return await cursor.fetchone()

    async def get_fines(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM fines'
            await cursor.execute(query)
            return await cursor.fetchall()

    async def update_fine(self, number: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'UPDATE fines SET amount = amount + amount, fine_mode =? WHERE number =?'
            await cursor.execute(query, (2, number))
            await db.commit()

    async def fine_user(self, user: disnake.Member):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM fines WHERE id2 = ?'
            await cursor.execute(query, (user.id,))
            return await cursor.fetchall()

    async def fine_embeds(self, interaction):
        data = await self.fine_user(interaction.author)
        embeds = []
        n = 0
        for row in data:
            n += 1
            user = await self.get_user(interaction.author)
            embed = disnake.Embed(title=f"Штраф #{row[0]}",
                                  description=f'Пострадавший {interaction.guild.get_member(row[2]).mention}',
                                  color=self.color)
            embed.add_field(name=f"Сумма",
                            value=f"```{row[6]}```")
            embed.add_field(name=f"Причина",
                            value=f"```{row[7]}```")
            embed.add_field(name=f"Срок оплаты",
                            value=f"<t:{row[8]}:f>")
            if row[1] == 1:
                embed.add_field(name=f"Статус",
                                value=f"```Оплачено```")
            elif row[1] == 2:
                embed.add_field(name=f"Статус",
                                value=f"```Просрочено```")
            else:
                embed.add_field(name=f"Статус",
                                value=f"```Неоплачено```")
            embed.set_thumbnail(url=f'https://render.crafty.gg/3d/bust/{user[5]}')
            embeds.append(embed)
        return embeds

    async def buy_fine(self, number: int, mode: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'UPDATE fines SET fine_mode =? WHERE number =?'
            await cursor.execute(query, (mode, number))
            await db.commit()

    async def get_user(self, user: disnake.Member):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM users WHERE id = ?'
            await cursor.execute(query, (user.id,))
            return await cursor.fetchone()

    async def change_skin(self, user: disnake.Member, skin: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'UPDATE users SET skin =? WHERE id =?'
            await cursor.execute(query, (skin, user.id))
            await db.commit()

    async def update_money(self, user: disnake.Member, money: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'UPDATE users SET money = money + ? WHERE id = ?'
            await cursor.execute(query, (money, user.id))
            await db.commit()

    async def add_transaction(self, sender_id: int, saver_id: int, amount: int, comment: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'INSERT INTO transactions (sender_id, saver_id, amount, comment, time) VALUES (?, ?, ?, ?, ?)'
            await cursor.execute(query, (sender_id, saver_id, amount, comment, datetime.datetime.now()))
            await db.commit()

    async def get_top(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM users ORDER BY money DESC'
            await cursor.execute(query)
            return await cursor.fetchall()

    async def get_transactions(self, user_id: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM transactions WHERE sender_id = ? OR saver_id = ?'
            await cursor.execute(query, (user_id, user_id))
            return await cursor.fetchall()

    async def get_embeds(self, interaction):
        data = await self.get_transactions(interaction.author.id)
        embeds = []
        n = 0
        for row in data:
            n += 1
            user = await self.get_user(interaction.author)
            time = datetime.datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S.%f')
            embed = disnake.Embed(title=f"Транзакции {interaction.author.display_name}", color=self.color,
                                  timestamp=time)
            embed.add_field(name=f"Перевод",
                            value=f"{interaction.guild.get_member(row[1]).mention} ➡ {interaction.guild.get_member(row[2]).mention}")
            embed.add_field(name=f"Сумма", value=f'```{row[3]}```')
            embed.add_field(name=f"Комментарий", value=f'```{row[4]}```')
            embed.set_thumbnail(url=f'https://render.crafty.gg/3d/bust/{user[5]}')
            embeds.append(embed)
        embeds = embeds[::-1]
        return embeds

    async def select_info(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT sum(money) FROM users'
            await cursor.execute(query)
            money = await cursor.fetchall()
            query = 'SELECT sum(fines) FROM users'
            await cursor.execute(query)
            fines = await cursor.fetchall()
            return (money[0][0], fines[0][0])
