import discord
from discord.ext import commands
from quart import Quart, request, jsonify
import json
import sqlite3
import mercadopago
import datetime

class TesteWebhook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.app = Quart(__name__)
        self.sdk = mercadopago.SDK("APP_USR-858971298465680-021921-8b0ac97868ffc64211357c5da2beb2fc-259696807")
        self.setup_routes()
        self.bot.loop.create_task(self.run_quart())

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

    # def setup_routes(self):
    #     # Endpoint do Webhook
    #     @self.app.route('/webhook/mercadopago', methods=['POST'])
    #     async def webhook():
    #         try:
    #             data = await request.get_json()

    #             if data and "data" in data and "id" in data["data"]:
    #                 pagamento_id = data["data"]["id"]  # ID do pagamento no Mercado Pago                  
    #                 payment_response = self.sdk.payment().get(pagamento_id)                    
    #                 payment_info = payment_response["response"]
    #                 status = payment_info["status"]
    #                 print(f"Pagamento recebido! ID: {pagamento_id}")
    #                 print(f"status: {status}")

    #                 conn = sqlite3.connect('produtos.db')
    #                 cursor = conn.cursor()
    #                 cursor.execute(f"SELECT canal_id, usuario_id, produtos FROM pagamentosAbertos WHERE payment_id = {pagamento_id}")
    #                 abertos = cursor.fetchone()
    #                 conn.close()              

    #                 if status == "approved":
    #                     print("aprovado")
    #                     if abertos:
    #                         print("ta no banco")
    #                         canal_id, usuario_id, produtos = abertos
    #                         produtos_tabela = json.loads(produtos)
    #                         canal = self.bot.get_channel(canal_id)

    #                         if canal:
    #                             print("canal existe, realizar entrega")
    #                             user = await self.bot.fetch_user(usuario_id)

    #                             await canal.send(f"✅ **Pagamento confirmado!** Obrigado!")
    #                             data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #                             for id in produtos_tabela:
    #                                 print(id[0], 'perarararara', produtos_tabela)
    #                                 conn = sqlite3.connect('produtos.db')
    #                                 cursor = conn.cursor()
    #                                 cursor.execute(f"SELECT produto_id, chave FROM chaves_produtos WHERE id = {float(id[0])}")
    #                                 produtes = cursor.fetchall()
    #                                 conn.close()

    #                                 for produto_id, cheves in produtes:
    #                                         conn = sqlite3.connect('produtos.db')
    #                                         cursor = conn.cursor()
    #                                         cursor.execute("SELECT preco FROM produtos WHERE id = ?", (produto_id,))
    #                                         produto = cursor.fetchone()
    #                                         conn.close()
                                            

    #                                         await canal.send(f"🔑 chave do produto {produto_id}: {cheves}")
    #                                         conn = sqlite3.connect('produtos.db')
    #                                         cursor = conn.cursor()
    #                                         cursor.execute('''INSERT INTO vendas (produto_id, chave, usuario, valor, data)
    #                                                         VALUES (?, ?, ?, ?, ?)''', 
    #                                                     (produto_id, cheves, str(user.id), produto[0], data_atual))
    #                                         conn.commit()
    #                                         conn.close()

    #                             for id in produtos_tabela:
    #                                 print(id[0], 'perarararara', produtos_tabela)
    #                                 conn = sqlite3.connect('produtos.db')
    #                                 cursor = conn.cursor()
    #                                 cursor.execute(f"SELECT produto_id, chave FROM chaves_produtos WHERE id = {float(id[0])}")
    #                                 produtes = cursor.fetchall()
    #                                 conn.close()

    #                                 try:
    #                                     for produto_id, cheves in produtes:
    #                                         await user.send(f"🔑 chave do produto {produto_id}: {cheves}")
    #                                 except:
    #                                     await canal.send("🚨 SEU PRIVADO ESTÁ BLOQUEADO, os produtos não forma enviados diretamnete no seu privado")
    #                                     break 
    #                             await canal.edit(name=f"PAGO-{data_atual}_{str(user.id)}")
    #                             await canal.edit(archived=True)

    #                             refund = self.sdk.refund().create(pagamento_id)
    #                             if refund['status'] == 200:
    #                                 print(f"Estorno realizado com sucesso para o pagamento {pagamento_id}")
    #                             else:
    #                                 print("Erro ao realizar o estorno:", refund)
    #                         else:
    #                             print("canal nao existe, extornar")
    #                             conn = sqlite3.connect('produtos.db')
    #                             cursor = conn.cursor()
    #                             cursor.execute("DELETE FROM pagamentosAbertos WHERE payment_id = ?", (pagamento_id,))
    #                             conn.commit()
    #                             conn.close()

    #                             await self.devolveChaves(produtos_tabela)

    #                             refund = self.sdk.refund().create(pagamento_id)
    #                             if refund['status'] == 200:
    #                                 print(f"Estorno realizado com sucesso para o pagamento {pagamento_id}")
    #                             else:
    #                                 print("Erro ao realizar o estorno:", refund)

    #                     else:
    #                         print("nao ta no banco")
    #                         refund = self.sdk.refund().create(pagamento_id)
    #                         if refund['status'] == 200:
    #                             print(f"Estorno realizado com sucesso para o pagamento {pagamento_id}")
    #                         else:
    #                             print("Erro ao realizar o estorno:", refund)

    #                 elif status == "cancelled" or status == "expired" or status == "rejected":
    #                     print("cancelado")
    #                     if abertos:
    #                         print("cancelado mas ta no banco")
    #                         conn = sqlite3.connect('produtos.db')
    #                         cursor = conn.cursor()
    #                         cursor.execute("DELETE FROM pagamentosAbertos WHERE payment_id = ?", (pagamento_id,))
    #                         conn.commit()
    #                         conn.close()

    #                         canal_id, usuario_id, produtos = abertos
    #                         produtos_tabela = json.loads(produtos)
    #                         await self.devolveChaves(produtos_tabela)

    #                         canal = self.bot.get_channel(canal_id)
    #                         if canal:
    #                             await canal.send(f"❌ O pagamento foi cancelado ou recusado.")
    #                             await canal.delete()
    #                 elif status == "pending":
    #                     print("pendente")                    

    #             # print("Mensagem recebida do Mercado Pago:")
    #             # print(json.dumps(data, indent=4))

    #             return jsonify({'status': 'received'}), 200

    #         except Exception as e:
    #             # Caso ocorra algum erro, retornamos um status de erro
    #             print(f"Erro ao processar o webhook: {str(e)}")
    #             return jsonify({'status': 'error', 'message': str(e)}), 500

    # async def run_quart(self):
    #     """Inicia o servidor Quart."""
    #     await self.app.run_task(host='0.0.0.0', port=8000)

# Função setup obrigatória
async def setup(bot):
    await bot.add_cog(TesteWebhook(bot))