import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

# conn = sqlite3.connect('produtos.db')
# cursor = conn.cursor()
# cursor.execute("SELECT id FROM produtos")
# produtos = cursor.fetchall()
# conn.close()

# views = {}

# def conectar_db():
#     conn = sqlite3.connect('produtos.db')  # Nome do arquivo do banco de dados
#     return conn

# def criar_callback(id_produto):
#     async def botao_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

#         carrinho_cog = interaction.client.get_cog("Carrinho")  # Substitua pelo nome correto da cog
#         if carrinho_cog:
#             await carrinho_cog.carrinho_novo(interaction, id_produto)  # Chamando a função carrinho com o ID do produto
#         else:
#             await interaction.response.send_message(f"A cog de carrinho não foi encontrada.", ephemeral=True)
#     return botao_callback

# if produtos:
#     for id in produtos:
#         id_produto = id[0]
#         nome_classe = f'view_{id_produto}'

#         NovaView = type(
#             nome_classe,
#             (discord.ui.View,),
#             {
#                 "__init__": lambda self: super(self.__class__, self).__init__(timeout=None),

#                 "botao": discord.ui.button(
#                     label='Adicionar ao Carrinho 🛒',
#                     style=discord.ButtonStyle.green,
#                     custom_id=f"botao_{id_produto}"
#                 )(criar_callback(id_produto))
#             }
#         )

#         views[id_produto] = NovaView


class Embeds_teste(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
    
    @commands.command()
    async def embed(self, ctx:commands.Context):
        usuario = ctx.author
        meu_embed = discord.Embed(title='olá conguitos!!!', description='Descrição teste :D')
        meu_embed.set_image(url='https://c.tenor.com/YrlJFgOrfwsAAAAd/tenor.gif')
        meu_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1332118871842361368/1333591141546721290/pngwing.com.png?ex=67997309&is=67982189&hm=0bb282533eb48d22b775e6e390078046318cc76da1a7f0e219b81d775de5a503&')
        meu_embed.set_footer(text='footer teste ( . Y . ) - - c==B')
        meu_embed.color = discord.Color.green()
        meu_embed.set_author(name=usuario.display_name, url='https://www.youtube.com/watch?v=NBUI1QvNLPk&ab_channel=FelpsLIVE', icon_url=usuario.avatar.url)

        meu_embed.add_field(name='valor do petroleo', value='$8 barril')
        meu_embed.add_field(name='Valor da BCT', value='$99999e99')

        # abaixo botao
        async def resposta_botao(interact:discord.Interaction):
            await interact.response.send_message('aperta de novo vai 🥵', ephemeral=True)

        view = discord.ui.View()
        botao = discord.ui.Button(label='Botão', style=discord.ButtonStyle.green)
        botao.callback = resposta_botao

        botao_url =  discord.ui.Button(label='Utubo', url='https://www.youtube.com/', style=discord.ButtonStyle.red)

        view.add_item(botao)
        view.add_item(botao_url)

        # abaixo lista
        async def resposta_selecao(interact:discord.Interaction):
            escolha = interact.data['values']
            await interact.response.send_message(escolha)

        selecao = discord.ui.Select(placeholder='selecione a quantia')   
        selecao.options = [
            discord.SelectOption(label='1', value='1'),
            discord.SelectOption(label='2', value='2'),
            discord.SelectOption(label='3', value='3'),
            discord.SelectOption(label='4', value='4'),
            discord.SelectOption(label='5', value='5')
        ]
        selecao.callback = resposta_selecao
        view.add_item(selecao)

        # chamadas

        await ctx.reply(embed=meu_embed, view=view)
        print('embed ativado')
    
    @commands.command()
    async def minecraft(self, ctx:commands.Context):

        #cog1 = self.bot.get_command('carrinho') ################################################

        usuario = ctx.author
        meu_embed = discord.Embed(title='Minecraft original', description='Conta Original - Minecraft Java & Badrock Edition')
        meu_embed.set_image(url='https://4kwallpapers.com/images/walls/thumbs_3t/11212.jpg')
        meu_embed.set_thumbnail(url='https://media.tenor.com/glcPxQrM51EAAAAj/minecraft.gif')
        meu_embed.color = discord.Color.green()

        meu_embed.add_field(name='Valor à vista', value='R$25,00')
        meu_embed.add_field(name='Em estoque', value='0')

        # abaixo botao
        view = discord.ui.View()
        botao = discord.ui.Button(label='Adicionar ao Carrinho 🛒', style=discord.ButtonStyle.green)

        async def resposta_botao(interact):
            usuario = interact.user
            usuarioID = str(usuario.id)
            canal = self.bot.get_channel(1334296529665785901)
            thread = None

            for topico in canal.threads:
                if usuarioID == topico.name:                    
                    thread = topico
                    break

            if thread == None:
                cog1 = self.bot.get_cog("Carrinho")
                thread = await canal.create_thread(
                    name=f"{usuario.id}",  # Nome da thread
                    auto_archive_duration=60  # Duração automática de arquivamento em minutos (60 = 1 hora)
                )
                await thread.send(f'Carrinho de <@{interact.user.id}> criado!')
                await cog1.carrinho(usuario, thread, 1)

            visao = discord.ui.View()
            botao_carrinho = discord.ui.Button(label='Ir para o carrinho 🛒', style=discord.ButtonStyle.link, url=f"https://discord.com/channels/1332118871053697027/{thread.id}")
            visao.add_item(botao_carrinho)
            await interact.response.send_message(f'carrinho criado com sucesso!', view=visao, ephemeral=True)

                   
        botao.callback = resposta_botao

        view.add_item(botao)

        # chamadas

        await ctx.send(embed=meu_embed, view=view)
        print('embed ativado')

    # @discord.app_commands.command()
    # async def atualizar_produtos(self, interact: discord.Interaction):
    #     print('Atualizar produtos')
    #     cargo_obeso = discord.utils.get(interact.user.roles, name="OBESO")
    #     if cargo_obeso:
    #         conn = conectar_db()
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT id, titulo, descricao, preco, autor, img_um, img_dois, rodape, cor FROM produtos")
    #         produtos = cursor.fetchall()
    #         conn.close()

    #         if not produtos:
    #             await interact.response.send_message("Nenhum produto encontrado.", ephemeral=True)
    #             return

    #         categoria_id = 1339397689099419678
    #         categoria = discord.utils.get(interact.guild.categories, id=categoria_id)
    #         if categoria is None:
    #             await interact.response.send_message("Categoria não encontrada.", ephemeral=True)
    #             return        
    #         for canal in categoria.channels:
    #             await canal.delete()
            
    #         for id, titulo, descricao, preco, autor, img_um, img_dois, rodape, cor in produtos:                
    #             novo_canal = await categoria.create_text_channel(titulo)
    #             conn = conectar_db()
    #             cursor = conn.cursor()
    #             cursor.execute(f'''UPDATE produtos SET chat = ? WHERE id = ?''', 
    #                            (novo_canal.id, id))
    #             conn.commit()
    #             conn.close()
                
    #             meu_embed = discord.Embed(title=titulo, description=descricao)
    #             if autor:
    #                 user = await self.bot.fetch_user(autor)
    #                 meu_embed.set_author(name=user.name, icon_url=user.avatar.url)
    #             if img_um:
    #                 meu_embed.set_thumbnail(url=img_um)
    #             if img_dois:
    #                 meu_embed.set_image(url=img_dois)
    #             if rodape: 
    #                 meu_embed.set_footer(text=rodape)
    #             if cor:
    #                 meu_embed.color = discord.Colour(int(cor, 16))

    #             meu_embed.add_field(name='Valor à vista', value=f"R${preco}")
    #             meu_embed.add_field(name='Em estoque', value='0')

    #             minha_view = views[id]()
    #             await novo_canal.send(embed=meu_embed, view=minha_view)

async def setup(bot):
    # for viewfilho in views.values():
    #     bot.add_view(viewfilho())
    await bot.add_cog(Embeds_teste(bot))