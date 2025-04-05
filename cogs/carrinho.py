import discord
from discord import app_commands
from discord.ext import commands
from collections import namedtuple
from datetime import datetime, timedelta
import sqlite3

class Carrinho(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()   

    @discord.app_commands.command()
    async def listar_carrinhos(self, interact:discord.Interaction):
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")

        if cargo_obeso:
            # conn = sqlite3.connect('produtos.db') pepes
            cog1 = self.bot.get_cog("Banco_novo")
            conn = cog1.connect_to_railway_mysql()
            cursor = conn.cursor()
            cursor.execute("SELECT produto_id, usuario, quantia FROM carrinho")
            carrinhos = cursor.fetchall()
            conn.close()
            embed = discord.Embed(title="📦 Lista de Todos Produtos dos carrinhos", color=discord.Color.blue())
            for produto_id, usuario, quantia in carrinhos:
                embed.add_field(name="produto", value=f"📝 Id produto: {produto_id}\n👤 ID Usuario: {usuario}\n💰 Quantia: {quantia}", inline=False)
            await interact.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command()
    async def apagar_carrinhos(self, interact:discord.Interaction):
        cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")

        if cargo_obeso:
            print('apagar carrinhos')
            # conn = sqlite3.connect('produtos.db') pepes
            cog1 = self.bot.get_cog("Banco_novo")
            conn = cog1.connect_to_railway_mysql()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carrinho;")
            conn.commit()
            conn.close()
            await interact.response.send_message("Carrinhos apagados com sucesso", ephemeral=True)

    async def carrinho(self, user, thread, ):
        idusuario = str(user.id)
        # conn = sqlite3.connect('produtos.db') pepes
        cog1 = self.bot.get_cog("Banco_novo")
        conn = cog1.connect_to_railway_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT produto_id, usuario, quantia FROM carrinho WHERE usuario = %s", (idusuario,))
        carrinhos = cursor.fetchall()
        # conn.close()

        meu_embed = discord.Embed(title='Seu Carrinho 🛒')
        meu_embed.set_image(url='https://media1.tenor.com/m/fsVMGgEsYm8AAAAd/shopping-cart-tpot-tpot.gif')
        meu_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1334154314490450003/1335433248620412968/15712867.gif?ex=67a026a1&is=679ed521&hm=af7f01dc62dc2062baa7550e4a86815416479a932b8784e67bf9579fca196672&')
        meu_embed.color = discord.Color.blue()
        bct = 0
        # conn = cog1.connect_to_railway_mysql()
        # cursor = conn.cursor()
        for produto_id, usuario, quantia in carrinhos:
            bct = bct + 1
            # conn = sqlite3.connect('produtos.db') pepes
            
            cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
            produto = cursor.fetchone()

            meu_embed.add_field(name=f'Produto {bct}', value=f'`{produto[1]}`', inline=True)
            meu_embed.add_field(name='Quantia desejada', value=f'`{int(quantia)}`', inline=True)
            meu_embed.add_field(name='Valor unitário', value=f'`R${produto[3]}`', inline=True)
        conn.close()

        # abaixo botao
        async def resposta_botao(interact:discord.Interaction):
            async def reposta_pix(interact:discord.Interaction):
                cog1 = self.bot.get_cog("PixCog")
                await cog1.pix(user, thread)

            async def reposta_cartao(interact:discord.Interaction):
                cog1 = self.bot.get_cog("Cartao")
                await cog1.cartao(user, thread)


            view = discord.ui.View(timeout=None)
            botao_pix = discord.ui.Button(label='❖ Pix', style=discord.ButtonStyle.green)
            botao_cartao = discord.ui.Button(label='💳 Cartão', style=discord.ButtonStyle.blurple, disabled=False)

            botao_pix.callback = reposta_pix
            botao_cartao.callback = reposta_cartao
            view.add_item(botao_pix)
            view.add_item(botao_cartao)
            
            await thread.purge(limit=100)
            await interact.response.send_message('⚠️⚠️Nós não fazemos **reembolso ou estorno** de pagamentos!!!⚠️⚠️\n\n🚨Lembre-se de deixar sua DM ativa para receber os produtos diretamente no seu privado!🚨\n\nSelecione uma forma de pagamento', view=view)

        async def resposta_cancelar(interact:discord.Interaction):
            await interact.channel.delete()
            # conn = sqlite3.connect('produtos.db') pepes
            cog1 = self.bot.get_cog("Banco_novo")
            conn = cog1.connect_to_railway_mysql()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carrinho WHERE usuario = %s", (idusuario,))
            conn.commit()
            conn.close()

        async def resposta_editar(interact:discord.Interaction):
            cogCarrinho = self.bot.get_cog("Carrinho")
            async def select_resposta(interaction: discord.Interaction):
                escolha = interaction.data['values'][0]
                print(escolha)
                
                class EditarProdutoModal(discord.ui.Modal):
                    def __init__(selfes):
                        super().__init__(title="Editar Produto")

                    edicao = discord.ui.TextInput(label=f'Digite a quantia de {escolha}')

                    async def on_submit(selfes, interaction: discord.Interaction):
                        def eh_inteiro(valor):
                            try:
                                return float(valor).is_integer()  # Verifica se é número e se não tem casa decimal
                            except ValueError:
                                return False
                        
                        if eh_inteiro(selfes.edicao.value):
                            if float(selfes.edicao.value) <= 0:
                                print('menor que 0')
                                # conn = sqlite3.connect('produtos.db') pepes
                                cog1 = self.bot.get_cog("Banco_novo")
                                conn = cog1.connect_to_railway_mysql()
                                cursor = conn.cursor()
                                cursor.execute('''DELETE FROM carrinho WHERE produto_id = %s AND usuario = %s''', 
                                            (escolha, idusuario))
                                conn.commit()
                                conn.close()
                                await interaction.response.send_message("Produto editado com sucesso!", ephemeral=True)
                                await cogCarrinho.carrinho(user, thread)
                            else:
                                # conn = sqlite3.connect('produtos.db') pepes
                                cog1 = self.bot.get_cog("Banco_novo")
                                conn = cog1.connect_to_railway_mysql()
                                cursor = conn.cursor()
                                cursor.execute('''UPDATE carrinho SET quantia = %s WHERE produto_id = %s AND usuario = %s''', 
                                            (selfes.edicao.value, escolha, idusuario))
                                conn.commit()
                                conn.close()
                                await interaction.response.send_message("Produto editado com sucesso!", ephemeral=True)
                                await cogCarrinho.carrinho(user, thread)
                        else:
                            print('valor nao inteiro')
                            await interaction.response.send_message("Valor digitado invalido", ephemeral=True)
                await interaction.response.send_modal(EditarProdutoModal())
                

            menuSelecao = discord.ui.Select(placeholder='Selecione uma opção')
            opcoes = []
            cog1 = self.bot.get_cog("Banco_novo")
            conn = cog1.connect_to_railway_mysql()
            cursor = conn.cursor()
            for produto_id, usuario, quantia in carrinhos:
                # conn = sqlite3.connect('produtos.db') pepes
                
                cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
                produto = cursor.fetchone()
                
                opcoes.append(discord.SelectOption(label=produto[1], value=produto_id))

            conn.close()
            menuSelecao.options = opcoes
            menuSelecao.callback = select_resposta
            view = discord.ui.View()
            view.add_item(menuSelecao)

            await interact.response.send_message("O que você deseja editar?", view=view)

        view = discord.ui.View(timeout=None)
        botao_pagamento = discord.ui.Button(label='Gerar pagamento', style=discord.ButtonStyle.green)
        botao_quantia =  discord.ui.Button(label='📝 Editar quantia', style=discord.ButtonStyle.blurple)
        botao_cancelar = discord.ui.Button(label='✖ Cancelar', style=discord.ButtonStyle.red)
        botao_pagamento.callback = resposta_botao
        botao_cancelar.callback = resposta_cancelar
        botao_quantia.callback = resposta_editar

        view.add_item(botao_pagamento)
        view.add_item(botao_cancelar)
        view.add_item(botao_quantia)

        # chamadas
        await thread.purge(limit=20)
        await thread.send(f"{user.mention}", embed=meu_embed, view=view)
        print('embed ativado')
    
    async def carrinho_novo(self, interact, id):
        await interact.response.defer(ephemeral=True)
        user = interact.user
        print('cria thread', user, id)
        
        usuarioID = str(user.id)
        canal = self.bot.get_channel(1334296529665785901)
        thread = None

        # conn = sqlite3.connect('produtos.db') pepes
        cog1 = self.bot.get_cog("Banco_novo")
        conn = cog1.connect_to_railway_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT produto_id, usuario FROM carrinho")
        carrinhos = cursor.fetchall()
        # conn.close()

        controle = 0
        for produto_id, usuario in carrinhos:
            if produto_id == id and usuario == usuarioID:
                print('ja tem igual')
                controle = 1
        if controle == 0:
            # conn = sqlite3.connect('produtos.db') pepes
            # cog1 = self.bot.get_cog("Banco_novo")
            # conn = cog1.connect_to_railway_mysql()
            # cursor = conn.cursor()
            cursor.execute('''INSERT INTO carrinho (produto_id, usuario, quantia)
                            VALUES (%s, %s, %s)''', 
                        (id, usuarioID, 1))
            print('produto adicionado ao carrinho')
        conn.commit()
        conn.close()
        for topico in canal.threads:
            if usuarioID == topico.name:    
                await topico.delete()
                #thread = topico
                break

        if thread == None:
            thread = await canal.create_thread(
                name=f"{user.id}",  # Nome da thread
            )

        visao = discord.ui.View()
        botao_carrinho = discord.ui.Button(label='Ir para o carrinho 🛒', style=discord.ButtonStyle.link, url=f"https://discord.com/channels/1332118871053697027/{thread.id}")
        visao.add_item(botao_carrinho)
        cog1 = self.bot.get_cog("Carrinho")
        # await interact.response.defer(ephemeral=True)
        await cog1.carrinho(user, thread)
        await interact.followup.send('Carrinho criado com sucesso!', view=visao, ephemeral=True) #resposta que permite espera

async def setup(bot):
    await bot.add_cog(Carrinho(bot))