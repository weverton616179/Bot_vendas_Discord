import discord
from discord.ext import commands
from quart import Quart, request, jsonify
import json
import sqlite3
import mercadopago
import datetime
import asyncio

class Cartao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sdk = mercadopago.SDK("TEST-858971298465680-021921-a974dd4d3bbfe15908060e8e9dd7e1f0-259696807")

    async def devolveChaves(self, produtos):
        print("devolvechaves")
        for chave in produtos:
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute(f"UPDATE chaves_produtos SET ativo = ? WHERE id = ?", (0, chave[0],))
            conn.commit()
            conn.close()
        cog1 = self.bot.get_cog("ProdutosCog")
        await cog1.atualiza_estoque()
    #---------------------------------------------VERIFICAR SE O LINK DE PAGAMENTO JÁ FOI USADE E APAGAR CHAT (usar o external_ref par pegar o payment id e verificar se ta aprovado)
    #----------------------------------------------------------------------------------------------------caso nao, apagar o chat e definir status como cancelado
    async def cancela_pg(self, payment_id):
        await asyncio.sleep(600)
        print(f"passou de 10 min, cancelar {payment_id}")
        resultado = self.sdk.payment().update(payment_id, {"status": "cancelled"})
        
        # Verifica se o cancelamento foi bem-sucedido
        if resultado["status"] == 200:
            print(f"Pagamento {payment_id} cancelado com sucesso!")
        else:
            print(f"Erro ao cancelar o pagamento: {resultado['response']['message']}")

    async def cartao(self, user, thread):
        conn = sqlite3.connect('produtos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT produto_id, quantia FROM carrinho WHERE usuario = ?", (str(user.id),))
        carrinhos = cursor.fetchall()
        conn.close()

        external_reference = str(user.id)+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        print
        valorTotal = 0
        produtos = []

        for produto_id, quantia in carrinhos:
            print(produto_id, quantia)
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM chaves_produtos WHERE produto_id = ? AND ativo = ? ", (produto_id, 0,))
            quantidade = cursor.fetchone()[0]
            conn.close()
            if quantia > quantidade:
                await thread.send(f"quantidade de {produto_id} nao disponivel")
                return
            else:
                conn = sqlite3.connect('produtos.db')
                cursor = conn.cursor()
                cursor.execute("SELECT preco FROM produtos WHERE id = ?", (produto_id,))
                produto = cursor.fetchone()
                conn.close()
                valorTotal = valorTotal + (float(produto[0]) * quantia)

                conn = sqlite3.connect('produtos.db')
                cursor = conn.cursor()
                cursor.execute(f"SELECT id FROM chaves_produtos WHERE produto_id = ? AND ativo = ? ", (produto_id, 0,))
                chaves = cursor.fetchmany(int(quantia))
                conn.close()
                for chave in chaves:
                    print(chave[0])
                    conn = sqlite3.connect('produtos.db')
                    cursor = conn.cursor()
                    cursor.execute(f"UPDATE chaves_produtos SET ativo = ? WHERE id = ?", (1, chave[0],))
                    conn.commit()
                    conn.close()
                    produtos.append(chave)
                    cog1 = self.bot.get_cog("ProdutosCog")
                    await cog1.atualiza_estoque()
            print(produtos)

        await thread.purge(limit=100)
        arredonda = round(valorTotal, 2)
        print("arredonda", arredonda)
        if valorTotal <= 0:
            await thread.send("❌ O valor deve ser maior que zero.")
            return
        
        preference_data = {
            "items": [
                {
                    "title": "Produto de Exemplo",
                    "quantity": 1,
                    "unit_price": arredonda,
                    "currency_id": "BRL",  # Moeda (BRL para Real Brasileiro)
                }
            ],
            "back_urls": {
                "success": "https://seusite.com/success",
                "failure": "https://seusite.com/failure",
                "pending": "https://seusite.com/pending"
            },
            "auto_return": "approved",  # Redirecionamento automático após pagamento aprovado
            "external_reference": external_reference,
            "payment_methods": {
                "excluded_payment_types": [
                    {"id": "ticket"},  # Bloqueia boleto
                    {"id": "bank_transfer"},  # Bloqueia transferência bancária (Pix)
                    {"id": "atm"}  # Bloqueia pagamento em lotéricas
                ],
                "excluded_payment_methods": [
                    # Aqui você pode bloquear métodos de pagamento específicos, se necessário
                ],
                "installments": 1  # Número máximo de parcelas (opcional)
            }
        }
        
        preference_response = self.sdk.preference().create(preference_data)
        preference = preference_response["response"]
        print(preference_response)
        checkout_url = preference["init_point"]        

        print('external_reference ', external_reference)
                
        produtos_json = json.dumps(produtos)
        conn = sqlite3.connect('produtos.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO pagamentosAbertos (payment_id, canal_id, usuario_id, produtos)
                        VALUES (?, ?, ?, ?)''', 
                    (str(external_reference), thread.id, user.id, produtos_json))
        conn.commit()
        conn.close()

        conn = sqlite3.connect('produtos.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM carrinho WHERE usuario = ?", (str(user.id),))
        conn.commit()
        conn.close()

        await thread.send(f"link para pagamento no valor de R${arredonda}: {checkout_url}")


async def setup(bot):
    await bot.add_cog(Cartao(bot))









# # Configuração do SDK
# # APP_USR-858971298465680-021921-8b0ac97868ffc64211357c5da2beb2fc-259696807
# # TEST-858971298465680-021921-a974dd4d3bbfe15908060e8e9dd7e1f0-259696807
# sdk = mercadopago.SDK("TEST-858971298465680-021921-a974dd4d3bbfe15908060e8e9dd7e1f0-259696807")

# # Criação da preferência de pagamento
# preference_data = {
#     "items": [
#         {
#             "title": "Produto de Exemplo",
#             "quantity": 1,
#             "unit_price": 100.0,
#             "currency_id": "BRL",  # Moeda (BRL para Real Brasileiro)
#         }
#     ],
#     "back_urls": {
#         "success": "https://seusite.com/success",
#         "failure": "https://seusite.com/failure",
#         "pending": "https://seusite.com/pending"
#     },
#     "auto_return": "approved",  # Redirecionamento automático após pagamento aprovado
#     "external_reference": "23asdasdas",
#     "payment_methods": {
#         "excluded_payment_types": [
#             {"id": "ticket"},  # Bloqueia boleto
#             {"id": "bank_transfer"},  # Bloqueia transferência bancária (Pix)
#             {"id": "atm"}  # Bloqueia pagamento em lotéricas
#         ],
#         "excluded_payment_methods": [
#             # Aqui você pode bloquear métodos de pagamento específicos, se necessário
#         ],
#         "installments": 1  # Número máximo de parcelas (opcional)
#     }
# }

# preference_response = sdk.preference().create(preference_data)
# preference = preference_response["response"]

# # URL para redirecionar o usuário ao Checkout Pro
# checkout_url = preference["init_point"]
# print("URL do Checkout Pro:", checkout_url)