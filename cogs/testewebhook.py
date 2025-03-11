from discord.ext import commands
from quart import Quart, request, jsonify
import json
import asyncio

class TesteWebhook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.app = Quart(__name__)
        self.setup_routes()
        self.bot.loop.create_task(self.run_quart())

    def setup_routes(self):
        # Endpoint do Webhook
        @self.app.route('/webhook/mercadopago', methods=['POST'])
        async def webhook():
            try:
                # Obtém os dados recebidos no webhook (normalmente em formato JSON)
                data = await request.get_json()

                if data and "data" in data and "id" in data["data"]:
                    pagamento_id = data["data"]["id"]  # ID do pagamento no Mercado Pago

                    # Aqui você pode consultar o status do pagamento na API do Mercado Pago
                    # Exemplo fictício (substitua pelo SDK do Mercado Pago)
                    payment_response = {"status": "approved"}  # Simulação de resposta
                    print(f"Pagamento recebido! ID: {pagamento_id}")
                    print(f"Status pagamento: {payment_response['status']}")

                # Aqui você pode fazer o que quiser com os dados, como salvar no banco de dados, processar etc.
                print("Mensagem recebida do Mercado Pago:")
                print(json.dumps(data, indent=4))  # Exibe os dados em formato legível

                # Responder ao Mercado Pago que o webhook foi recebido com sucesso
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