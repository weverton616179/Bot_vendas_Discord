import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3

conn = sqlite3.connect('produtos.db')
cursor = conn.cursor()

permissoes = discord.Intents.default()
permissoes.message_content = True
permissoes.members = True
bot = commands.Bot(command_prefix=".", intents=permissoes)



def criar_tabelas():
    conn = sqlite3.connect('produtos.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id TEXT NOT NULL,
        titulo TEXT NOT NULL,
        descricao TEXT NOT NULL,
        preco REAL NOT NULL,
        autor TEXT,
        img_um TEXT,
        img_dois TEXT,
        rodape TEXT,
        cor TEXT,
        chat TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chaves_produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id TEXT NOT NULL,
        chave TEXT NOT NULL,
        ativo INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carrinho (
        produto_id TEXT NOT NULL,
        usuario TEXT NOT NULL,
        quantia REAL NOT NULL,
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendas (
        produto_id TEXT NOT NULL,
        chave TEXT NOT NULL,
        usuario TEXT NOT NULL,
        valor REAL NOT NULL,
        data TEXT NOT NULL,
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
    ''')
    conn.commit()
    conn.close()

async def carregar_cogs():
    for arquivo in os.listdir('cogs'):
        if arquivo.endswith('.py'):
            await bot.load_extension(f'cogs.{arquivo[:-3]}')

@bot.event
async def on_ready():
    criar_tabelas()
    await carregar_cogs()
    await bot.tree.sync()
    print("banana")

@bot.event
async def on_disconnect():
    print("Bot desconectado!")

@bot.event
async def on_resumed():
    print("Bot reconectado!")

@bot.event
async def on_member_join(membro:discord.Member):
    canal = bot.get_channel(1333598010462044232)
    meu_embed = discord.Embed(title=f'{membro.display_name} entrou para a macacada!!! XD')
    meu_embed.set_thumbnail(url=membro.avatar)

    await canal.send(embed=meu_embed)
    print('entrou')




bot.run("MTMzMjExODQ1NzU1ODUwMzQ2Nw.GxShpZ.TpweAqwgIq5wCvX3352auYyDxr_lPqvo8E6HlI", reconnect=True)