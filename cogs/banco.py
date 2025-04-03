import discord
from discord import app_commands
from discord.ext import commands
import pymysql
from pymysql import Error

class Banco_novo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    def connect_to_railway_mysql(self):
        try:
            connection = pymysql.connect(
                host='hopper.proxy.rlwy.net',
                port=44999,
                database='railway',
                user='root',
                password='wqWlDNLwuqvyCFTZIFILwaIVFVxzfMtM',
                charset='utf8mb4',
                # cursorclass=pymysql.cursors.DictCursor
            )
            
            print("Conexão bem-sucedida ao MySQL!")
            
            # Exemplo de consulta
            with connection.cursor() as cursor:
                cursor.execute("SELECT DATABASE()")
                result = cursor.fetchone()
                
            return connection
        
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            return None
    
async def setup(bot):
    await bot.add_cog(Banco_novo(bot))