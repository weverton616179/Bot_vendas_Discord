import discord
from discord.ext import commands
from quart import Quart, request, jsonify
import json
import sqlite3
import mercadopago

class TesteWebhook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.app = Quart(__name__)
        self.sdk = mercadopago.SDK("APP_USR-858971298465680-021921-8b0ac97868ffc64211357c5da2beb2fc-259696807")
        self.setup_routes()
        self.bot.loop.create_task(self.run_quart())

    def setup_routes(self):
        # Endpoint do Webhook
        @self.app.route('/webhook/mercadopago', methods=['POST'])
        async def webhook():
            try:
                data = await request.get_json()

                if data and "data" in data and "id" in data["data"]:
                    pagamento_id = data["data"]["id"]  # ID do pagamento no Mercado Pago                  
                    payment_response = self.sdk.payment().get(pagamento_id)                    
                    payment_info = payment_response["response"]
                    status = payment_info["status"]
                    print(f"Pagamento recebido! ID: {pagamento_id}")
                    print(f"status: {status}")

                    conn = sqlite3.connect('produtos.db')
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT canal_id, usuario_id, produtos FROM pagamentosAbertos WHERE payment_id = {pagamento_id}")
                    abertos = cursor.fetchone()
                    conn.close()              

                    if status == "approved":
                        print("aprovado")
                        if abertos:
                            print("ta no banco")
                            canal_id, usuario_id, produtos = abertos
                            produtos_tabela = json.loads(produtos)
                            canal = self.bot.get_channel(canal_id)

                            if canal:
                                print("canal existe, realizar entrega")
                            else:
                                print("canal nao existe, extornar")
                                conn = sqlite3.connect('produtos.db')
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM pagamentosAbertos WHERE payment_id = ?", (pagamento_id,))
                                conn.commit()
                                conn.close()

                                refund = self.sdk.payment_refund(pagamento_id)
                                if refund['status'] == 200:
                                    print(f"Estorno realizado com sucesso para o pagamento {pagamento_id}")
                                else:
                                    print("Erro ao realizar o estorno:", refund)

                        else:
                            print("nao ta no banco")
                            refund = self.sdk.payment_refund(pagamento_id)
                            if refund['status'] == 200:
                                print(f"Estorno realizado com sucesso para o pagamento {pagamento_id}")
                            else:
                                print("Erro ao realizar o estorno:", refund)

                    elif status == "cancelled":
                        print("cancelado")
                        if abertos:
                            print("cancelado mas ta no banco")
                            conn = sqlite3.connect('produtos.db')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM pagamentosAbertos WHERE payment_id = ?", (pagamento_id,))
                            conn.commit()
                            conn.close()
                    elif status == "pending":
                        print("pendente")                    

                # print("Mensagem recebida do Mercado Pago:")
                # print(json.dumps(data, indent=4))

                return jsonify({'status': 'received'}), 200

            except Exception as e:
                # Caso ocorra algum erro, retornamos um status de erro
                print(f"Erro ao processar o webhook: {str(e)}")
                return jsonify({'status': 'error', 'message': str(e)}), 500

    async def run_quart(self):
        """Inicia o servidor Quart."""
        await self.app.run_task(host='0.0.0.0', port=8000)

# Função setup obrigatória
async def setup(bot):
    await bot.add_cog(TesteWebhook(bot))