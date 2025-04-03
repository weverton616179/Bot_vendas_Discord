import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3
import pymysql
from pymysql import Error

conn = sqlite3.connect('produtos.db')
cursor = conn.cursor()

permissoes = discord.Intents.default()
permissoes.message_content = True
permissoes.members = True
bot = commands.Bot(command_prefix=".", intents=permissoes)

def connect_to_railway_mysql():
    try:
        connection = pymysql.connect(
            host='hopper.proxy.rlwy.net',
            port=44999,
            database='railway',
            user='root',
            password='wqWlDNLwuqvyCFTZIFILwaIVFVxzfMtM',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("Conexão bem-sucedida ao MySQL!")
        
        # Exemplo de consulta
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            result = cursor.fetchone()
            print(f"Banco de dados conectado: {result['DATABASE()']}")
            
        return connection
    
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def criar_tabelas():
    conn = sqlite3.connect('produtos.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id VARCHAR(50) NOT NULL,
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

    cursor.execute("""CREATE TABLE IF NOT EXISTS pagamentosAbertos (
        payment_id TEXT NOT NULL,
        canal_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        produtos TEXT NOT NULL
    )""")

    conn.commit()
    conn.close()


    conn = connect_to_railway_mysql()
    if conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id VARCHAR(50) NOT NULL PRIMARY KEY,
                titulo VARCHAR(150) NOT NULL,
                descricao TEXT NOT NULL,
                preco REAL NOT NULL,
                autor VARCHAR(100),
                img_um TEXT,
                img_dois TEXT,
                rodape TEXT,
                cor TEXT,
                chat TEXT
            )
            ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chaves_produtos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                produto_id VARCHAR(50) NOT NULL,
                chave TEXT NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
            )
            ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carrinho (
                produto_id VARCHAR(50) NOT NULL,
                usuario VARCHAR(100) NOT NULL,
                quantia REAL NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
            )
            ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                produto_id VARCHAR(50) NOT NULL,
                chave TEXT NOT NULL,
                usuario VARCHAR(100) NOT NULL,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
            )
            ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagamentosAbertos (
                payment_id VARCHAR(255),
                canal_id BIGINT NOT NULL,
                usuario_id BIGINT NOT NULL,
                produtos TEXT NOT NULL
            )
            ''')

        conn.commit()
        conn.close()
        print("Conexão encerrada")

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

bot.run("MTMzMjExODQ1NzU1ODUwMzQ2Nw.GxShpZ.TpweAqwgIq5wCvX3352auYyDxr_lPqvo8E6HlI", reconnect=True)