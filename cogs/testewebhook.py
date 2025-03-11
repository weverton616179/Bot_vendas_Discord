from discord.ext import commands
from flask import Flask, request, jsonify
import json
import threading

class TesteWebhook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_flask_server()

    def start_flask_server(self):
        # Cria uma instância do Flask
        app = Flask(__name__)

        # Endpoint do Webhook
        @app.route('/webhook/mercadopago', methods=['POST'])
        async def webhook():
            try:
                # Obtém os dados recebidos no webhook (normalmente em formato JSON)
                data = request.get_json()

                if data and "data" in data and "id" in data["data"]:
                    pagamento_id = data["data"]["id"]  # ID do pagamento no Mercado Pago

                    payment_response = self.sdk.payment().get(pagamento_id)
                    
                    # Aqui você pode consultar o status do pagamento na API do Mercado Pago
                    print(f"Pagamento recebido! ID: {pagamento_id}")
                    print(f"Status pagamento: {payment_response["status"]}")

                # Aqui você pode fazer o que quiser com os dados, como salvar no banco de dados, processar etc.
                print("Mensagem recebida do Mercado Pago:")
                print(json.dumps(data, indent=4))  # Exibe os dados em formato legível

                # Responder ao Mercado Pago que o webhook foi recebido com sucesso
                return jsonify({'status': 'received'}), 200

            except Exception as e:
                # Caso ocorra algum erro, retornamos um status de erro
                print(f"Erro ao processar o webhook: {str(e)}")
                return jsonify({'status': 'error', 'message': str(e)}), 500

        # Inicia o Flask em uma thread separada
        flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8000))
        flask_thread.start()

# Função setup obrigatória
async def setup(bot):
    await bot.add_cog(TesteWebhook(bot))
