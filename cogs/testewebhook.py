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
                    print(f"Pagamento recebido! ID: {pagamento_id}")

                    conn = sqlite3.connect('produtos.db')
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT canal_id, usuario_id, produtos FROM pagamentosAbertos WHERE payment_id = {pagamento_id}")
                    abertos = cursor.fetchone()
                    conn.close()

                    #verificar se o pagamento foi aprovado e se o canal existe ainda
                    #verificar se o pagamento foi aprovado sem o canal (extornar)
                    #verificar se pagamento aprovado sem estar no banco (extornar)
                    #se pagamento cancelado ou aprovado, apagar do banco dedados

                    payment_info = payment_response["response"]
                    status = payment_info["status"]
                    print(f"status: {status}")

                    if abertos:
                        canal_id, usuario_id, produtos = abertos
                        produtos_tabela = json.loads(produtos)
                        print(canal_id, usuario_id, produtos_tabela)
                    else:
                        print(f"{pagamento_id} nao se encontra no banco de dados")
                    
                    

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