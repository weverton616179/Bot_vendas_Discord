import discord
from discord.ext import commands
import sqlite3
import json

conn = sqlite3.connect('produtos.db')
cursor = conn.cursor()
cursor.execute("SELECT id FROM produtos")
produtos = cursor.fetchall()
conn.close()

views = {}

def criar_callback(id_produto):
    async def botao_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        carrinho_cog = interaction.client.get_cog("Carrinho")
        if carrinho_cog:
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM chaves_produtos WHERE produto_id = ? AND ativo = ? ", (id_produto, 0,))
            quantidade = cursor.fetchone()[0]
            conn.close()
            if quantidade > 0:
                await carrinho_cog.carrinho_novo(interaction, id_produto)  # Chamando a função carrinho com o ID do produto
            else:
                await interaction.response.send_message("Produto indisponivel", ephemeral=True)
        else:
            await interaction.response.send_message(f"A cog de carrinho não foi encontrada.", ephemeral=True)
    return botao_callback

if produtos:
    for id in produtos:
        id_produto = id[0]
        nome_classe = f'view_{id_produto}'

        NovaView = type(
            nome_classe,
            (discord.ui.View,),
            {
                "__init__": lambda self: super(self.__class__, self).__init__(timeout=None),

                "botao": discord.ui.button(
                    label='Adicionar ao Carrinho 🛒',
                    style=discord.ButtonStyle.green,
                    custom_id=f"botao_{id_produto}"
                )(criar_callback(id_produto))
            }
        )

        views[id_produto] = NovaView

class ProdutosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def atualiza_estoque(self):
        print('atualiza estoque')
        conn = sqlite3.connect('produtos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, chat FROM produtos")
        produtos = cursor.fetchall()
        conn.close()

        for id, chat in produtos:
            channel = self.bot.get_channel(int(chat))
            if channel:
                async for message in channel.history(limit=10):
                    if message.embeds:
                        embed = message.embeds[0]
                        field = embed.fields[1]
                        conn = sqlite3.connect('produtos.db')
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT COUNT(*) FROM chaves_produtos WHERE produto_id = ? AND ativo = ? ", (id, 0,))
                        quantidade = cursor.fetchone()[0]
                        conn.close()
                        embed.set_field_at(index=1, name=field.name, value=f'`{quantidade}`', inline=field.inline)
                        await message.edit(embed=embed)

    @discord.app_commands.command()
    async def adicionar_produto(self, interact: discord.Interaction, id: str):
        print('adicionar')
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")

        if cargo_obeso:

            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM produtos")
            produtos = cursor.fetchall()
            conn.close()
            controle = 0
            for id_banco in produtos:
                if id_banco[0] == id:
                    controle = 1
                    break
                    
            if controle == 0:
                class AdicionarProdutoModal(discord.ui.Modal):
                    def __init__(self):
                        super().__init__(title="Adicionar Produto")

                    titulo = discord.ui.TextInput(label='Título do produto')
                    descricao = discord.ui.TextInput(label='Descrição do produto')
                    preco = discord.ui.TextInput(label='Preço (para valores quebrados utilizar ponto)')

                    async def on_submit(self, interaction: discord.Interaction):
                        conn = sqlite3.connect('produtos.db')
                        cursor = conn.cursor()
                        cursor.execute('''INSERT INTO produtos (id, titulo, descricao, preco)
                                        VALUES (?, ?, ?, ?)''', 
                                    (id, self.titulo.value, self.descricao.value, float(self.preco.value)))
                        conn.commit()
                        conn.close()

                        id_produto = id
                        nome_classe = f'view_{id_produto}'

                        NovaView = type(
                            nome_classe,
                            (discord.ui.View,),
                            {
                                "__init__": lambda self: super(self.__class__, self).__init__(timeout=None),

                                "botao": discord.ui.button(
                                    label='Adicionar ao Carrinho 🛒',
                                    style=discord.ButtonStyle.green,
                                    custom_id=f"botao_{id_produto}"
                                )(criar_callback(id_produto))
                            }
                        )

                        views[id_produto] = NovaView

                        await interaction.response.send_message("Produto cadastrado com sucesso!", ephemeral=True)

                await interact.response.send_modal(AdicionarProdutoModal())

            else:
                await interact.response.send_message("Produto com o mesmo id já existente", ephemeral=True)

    @discord.app_commands.command()
    async def listar_produtos(self, interact: discord.Interaction):
        print('listar')
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
        if cargo_obeso:
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, titulo, descricao, preco, autor, img_um, img_dois, rodape, cor, chat FROM produtos")
            produtos = cursor.fetchall()
            conn.close()

            if not produtos:
                await interact.response.send_message("Nenhum produto encontrado.", ephemeral=True)
                return

            embed = discord.Embed(title="📦 Lista de Produtos", color=discord.Color.blue())

            for id, titulo, descricao, preco, autor, img_um, img_dois, rodape, cor, chat in produtos:
                embed.add_field(name=titulo, value=f"💾 ID: {id}\n📝 Descrição: {descricao}\n💰 Preço: R$ {preco}\n👤 Autor: {autor}\n📷 Imagem thumb: {img_um}\n📷 Imagem príncipal: {img_dois}\n🦶 Rodapé: {rodape}\n🎨 Cor: {cor}\n💬 ID Chat: {chat}", inline=False)

            await interact.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command()
    async def apagar_produto(self, interact: discord.Interaction, id_produto: str):
        print("apagar")
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")

        if cargo_obeso:
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM produtos WHERE id = ?''', (id_produto,))
            produto = cursor.fetchone()
            conn.close()

            if produto:
                conn = sqlite3.connect('produtos.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
                conn.commit()
                conn.close()

                await interact.response.send_message("Produto apagado com sucesso!", ephemeral=True)
            else:
                await interact.response.send_message("Produto não encontrado", ephemeral=True)

    @discord.app_commands.command()
    async def editar_produto(self, interact: discord.Interaction, id_produto: str):
        print("editar")
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")

        if cargo_obeso:
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM produtos WHERE id = ?''', (id_produto,))
            produto = cursor.fetchone()
            conn.close()

            if produto:

                async def select_resposta(interaction: discord.Interaction):
                    escolha = interaction.data['values'][0]

                    class EditarProdutoModal(discord.ui.Modal):
                        def __init__(self):
                            super().__init__(title="Editar Produto")

                        edicao = discord.ui.TextInput(label=f'Digite o novo valor de {escolha}')

                        async def on_submit(self, interaction: discord.Interaction):
                            conn = sqlite3.connect('produtos.db')
                            cursor = conn.cursor()
                            cursor.execute(f'''UPDATE produtos SET {escolha} = ? WHERE id = ?''', 
                                           (self.edicao.value, id_produto))
                            conn.commit()
                            conn.close()
                            await interaction.response.send_message("Produto editado com sucesso!", ephemeral=True)

                    await interaction.response.send_modal(EditarProdutoModal())

                menuSelecao = discord.ui.Select(placeholder='Selecione uma opção')
                opcoes = [
                    discord.SelectOption(label='Título', value='titulo'),
                    discord.SelectOption(label='Descrição', value='descricao'),
                    discord.SelectOption(label='Preço', value='preco'),
                    discord.SelectOption(label='Autor', value='autor'),
                    discord.SelectOption(label='Imagem thumbnail', value='img_um'),
                    discord.SelectOption(label='Imagem principal', value='img_dois'),
                    discord.SelectOption(label='Rodapé', value='rodape'),
                    discord.SelectOption(label='Cor', value='cor'),

                ]
                menuSelecao.options = opcoes
                menuSelecao.callback = select_resposta
                view = discord.ui.View()
                view.add_item(menuSelecao)

                await interact.response.send_message("O que você deseja editar?", view=view, ephemeral=True)

            else:
                await interact.response.send_message("Produto não encontrado", ephemeral=True)

    @discord.app_commands.command()
    async def editar_embed_produto(self, interact: discord.Interaction, id_produto: str):
        print('editar embed')
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")

        if cargo_obeso:

            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM produtos WHERE id = ?''', (id_produto,))
            produto = cursor.fetchone()
            conn.close()

            if produto:
                class EditarEmbedModal(discord.ui.Modal):
                    def __init__(self):
                        super().__init__(title="Editar embed (todas os campos são opcionais)")

                    autor = discord.ui.TextInput(label='Autor (usiaro ID)', placeholder='1423576587895675', required=False)
                    img_um = discord.ui.TextInput(label='Imagen thumbnail (link)', required=False)
                    img_dois = discord.ui.TextInput(label='Imagem principal (link)', required=False)
                    rodape = discord.ui.TextInput(label='Texto rodapé', placeholder='Texto muito legal ;D', required=False)
                    cor = discord.ui.TextInput(label='Cor (hexadecimal)', placeholder='0xFF5733 (sempre utilizar o 0x)', required=False)

                    async def on_submit(self, interaction: discord.Interaction):
                        conn = sqlite3.connect('produtos.db')
                        cursor = conn.cursor()
                        cursor.execute(f'''UPDATE produtos 
                                        SET autor = ?, img_um = ?, img_dois = ?, rodape = ?, cor = ?
                                        WHERE id = ?''', 
                                       (self.autor.value, self.img_um.value, self.img_dois.value, self.rodape.value, self.cor.value, id_produto))
                        conn.commit()
                        conn.close()
                        await interaction.response.send_message("Embed editado com sucesso!", ephemeral=True)

                await interact.response.send_modal(EditarEmbedModal())

            else:
                await interact.response.send_message("Produto não encontrado", ephemeral=True)

    @discord.app_commands.command()
    async def atualizar_produtos(self, interact: discord.Interaction):
        print('Atualizar produtos')
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
        if cargo_obeso:
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, titulo, descricao, preco, autor, img_um, img_dois, rodape, cor FROM produtos")
            produtos = cursor.fetchall()
            conn.close()

            if not produtos:
                await interact.response.send_message("Nenhum produto encontrado.", ephemeral=True)
                return

            categoria_id = 1339397689099419678
            categoria = discord.utils.get(interact.guild.categories, id=categoria_id)
            if categoria is None:
                await interact.response.send_message("Categoria não encontrada.", ephemeral=True)
                return        
            for canal in categoria.channels:
                await canal.delete()
            
            for id, titulo, descricao, preco, autor, img_um, img_dois, rodape, cor in produtos:                
                novo_canal = await categoria.create_text_channel(titulo)
                conn = sqlite3.connect('produtos.db')
                cursor = conn.cursor()
                cursor.execute(f'''UPDATE produtos SET chat = ? WHERE id = ?''', 
                               (novo_canal.id, id))
                conn.commit()
                conn.close()
                
                meu_embed = discord.Embed(title=titulo, description=f'`{descricao}`')
                if autor:
                    user = await self.bot.fetch_user(autor)
                    meu_embed.set_author(name=user.name, icon_url=user.avatar.url)
                if img_um:
                    meu_embed.set_thumbnail(url=img_um)
                if img_dois:
                    meu_embed.set_image(url=img_dois)
                if rodape: 
                    meu_embed.set_footer(text=rodape)
                if cor:
                    meu_embed.color = discord.Colour(int(cor, 16))

                meu_embed.add_field(name='Valor à vista', value=f"`R${preco}`")
                meu_embed.add_field(name='Em estoque', value='`0`')

                minha_view = views[id]()
                await novo_canal.send(embed=meu_embed, view=minha_view)
            await self.atualiza_estoque()

    @discord.app_commands.command()
    async def adicionar_chaves(selfes, interact:discord.Interaction, id_produto: str):
        print('adicionar chaves')
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
        if cargo_obeso:

            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM produtos WHERE id = ?", (id_produto,))
            produto = cursor.fetchone()
            conn.close()
            controle = 0
            if produto:
                class AdicionarChavesModal(discord.ui.Modal):
                    def __init__(self):
                        super().__init__(title="Adicionar chaves")

                    chaves = discord.ui.TextInput(label='Digite as chaves', style=discord.TextStyle.paragraph, placeholder='Exemplos:\n1423576587895675\n12312512332123\n123123334123')

                    async def on_submit(self, interaction: discord.Interaction):
                        linhas = self.chaves.value.splitlines()
                        for linha in linhas:
                            conn = sqlite3.connect('produtos.db')
                            cursor = conn.cursor()
                            cursor.execute('''INSERT INTO chaves_produtos (produto_id, chave)
                                            VALUES (?, ?)''', 
                                        (id_produto, linha))
                            conn.commit()
                            conn.close()
                        await interaction.response.send_message("Chaves adicionadas com sucesso!", ephemeral=True)
                        await selfes.atualiza_estoque()
                await interact.response.send_modal(AdicionarChavesModal())            
            else:
                await interact.response.send_message('Produto não existente', ephemeral=True)

    @discord.app_commands.command()
    async def listar_chaves(self, interact: discord.Interaction):
        print('listar chaves')
        await self.atualiza_estoque()
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
        if cargo_obeso:
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, produto_id, chave, ativo FROM chaves_produtos")
            chaves = cursor.fetchall()
            conn.close()

            if not chaves:
                await interact.response.send_message("Nenhum produto encontrado.", ephemeral=True)
                return

            embed = discord.Embed(title="🔑 Lista de chaves", color=discord.Color.blue())

            for id, produto_id, chave, ativo in chaves:
                embed.add_field(name=produto_id, value=f"🔑 Chave: {chave}\n💬 ID Chave: {id}\n👤Já Ativada (0=não, 1=sim): {ativo}", inline=False)

            await interact.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command()
    async def apagar_chaves(self, interact:discord.Interaction):
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
        if cargo_obeso:
            print('apagar chaves')
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chaves_produtos;")
            conn.commit()
            conn.close()
            await interact.response.send_message("Chaves apagadas com sucesso", ephemeral=True)
            await self.atualiza_estoque()

    @discord.app_commands.command()
    async def apagar_chaves_usadas(self, interact:discord.Interaction):
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
        if cargo_obeso:
            print('apagar chaves')
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chaves_produtos WHERE ativo = ?", (1,))
            conn.commit()
            conn.close()
            await interact.response.send_message("Chaves apagadas com sucesso", ephemeral=True)
            await self.atualiza_estoque()

    @discord.app_commands.command()
    async def listar_vendas(self, interact:discord.Interaction):
        print('listar vendas')
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
        if cargo_obeso:
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("SELECT produto_id, chave, usuario, valor, data FROM vendas")
            produtos = cursor.fetchall()
            conn.close()

            if not produtos:
                await interact.response.send_message("Nenhuma venda feita.", ephemeral=True)
                return
            
            embed = discord.Embed(title="📦 Lista de vendas", color=discord.Color.blue())

            for produto_id, chave, usuario, valor, data in produtos:
                user = self.bot.get_user(int(usuario))
                embed.add_field(name=user.name, value=f"ID Usuario: {usuario}\nID Produto: {produto_id}\nChave: {chave}\nValor: {valor}\nData da compra: {data}", inline=False)

            await interact.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command()
    async def apagar_vendas(self, interact:discord.Interaction):
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
        if cargo_obeso:
            print('apagar vendas')
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vendas;")
            conn.commit()
            conn.close()
            await interact.response.send_message("Vendas apagadas com sucesso", ephemeral=True)
            await self.atualiza_estoque()

    @discord.app_commands.command()
    async def listar_pagamentos_abertos(self, interact:discord.Interaction):
        print('listar vendas')
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
        if cargo_obeso:
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("SELECT payment_id, canal_id, usuario_id, produtos FROM pagamentosAbertos")
            abertos = cursor.fetchall()
            conn.close()

            if not abertos:
                await interact.response.send_message("Nenhuma venda feita.", ephemeral=True)
                return
            
            embed = discord.Embed(title="📦 Lista de Pagamentos em Aberto", color=discord.Color.blue())      
            for payment_id, canal_id, usuario_id, produtos in abertos:
                produtos_tabela = json.loads(produtos)
                embed.add_field(name=payment_id, value=f"ID Usuario: {usuario_id}\nID Produtos: {produtos_tabela}\nCanal: {canal_id}", inline=False)

            await interact.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    for viewfilho in views.values():
        bot.add_view(viewfilho())
    await bot.add_cog(ProdutosCog(bot))
