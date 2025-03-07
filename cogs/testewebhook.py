from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Endpoint do Webhook
@app.route('/botvendasdiscord-production.up.railway.app/webhook/mercadopago', methods=['POST'])
def webhook():
    try:
        # Obtém os dados recebidos no webhook (normalmente em formato JSON)
        data = request.get_json()

        # Aqui você pode fazer o que quiser com os dados, como salvar no banco de dados, processar etc.
        print("Mensagem recebida do Mercado Pago:")
        print(json.dumps(data, indent=4))  # Exibe os dados em formato legível

        # Responder ao Mercado Pago que o webhook foi recebido com sucesso
        return jsonify({'status': 'received'}), 200

    except Exception as e:
        # Caso ocorra algum erro, retornamos um status de erro
        print(f"Erro ao processar o webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Roda o servidor Flask na porta 5000
    app.run(host='0.0.0.0', port=8000)
