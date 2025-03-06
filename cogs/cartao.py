import discord
from discord.ext import commands
from discord import app_commands
import mercadopago

sdk = mercadopago.SDK("TEST-858971298465680-021921-a974dd4d3bbfe15908060e8e9dd7e1f0-259696807")

class cogCartao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cartao_credito(self, user, thread, interact:discord.Interaction):
        print("cartao credito", user, thread, interact.user.id)
        await interact.response.send_message("banana", ephemeral=True)

    async def cartao_debito(self, user, thread, interact:discord.Interaction):
        print("cartao debito", user, thread, interact.user.id)

        await interact.response.send_message("banana", ephemeral=True)


# import discord
# from discord.ext import commands
# from discord import app_commands
# import mercadopago

# # Configuração do Mercado Pago
# ACCESS_TOKEN = "TEST-858971298465680-021921-a974dd4d3bbfe15908060e8e9dd7e1f0-259696807"  # Substitua pelo seu Access Token do Mercado Pago
# sdk = mercadopago.SDK(ACCESS_TOKEN)

# # Dados do cartão de teste (hardcoded)
# CARTAO_TESTE = {
#     "card_number": "5031433215406351",  # Número do cartão de teste Mastercard
#     "security_code": "123",  # Código de segurança (CVV)
#     "expiration_month": "11",  # Mês de expiração
#     "expiration_year": "2025",  # Ano de expiração
#     "cardholder": {
#         "name": "APRO",  # Nome do titular do cartão
#         "identification": {
#             "type": "CPF",  # Tipo de identificação
#             "number": "12345678909"  # Número do CPF
#         }
#     }
# }

# class PagamentoCog(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     # Comando de pagamento via slash command
#     @app_commands.command(name="pagamento", description="Realiza um pagamento com cartão de teste")
#     @app_commands.describe(
#         amount="Valor da transação",
#         email="Email do pagador"
#     )
#     async def pagamento(self, interaction: discord.Interaction, amount: float, email: str):
#         await interaction.response.defer(ephemeral=True)  # Resposta inicial (para evitar timeout)

#         try:
#             # Gera o token do cartão
#             card_token_response = sdk.card_token().create(CARTAO_TESTE)
#             card_token = card_token_response["response"]["id"]
#             print(f"Token gerado: {card_token}")  # Log do token

#             # Dados do pagamento
#             payment_data = {
#                 "transaction_amount": amount,
#                 "token": card_token,
#                 "description": "Pagamento via Discord Bot",
#                 "installments": 1,
#                 "payment_method_id": "master",  # Método de pagamento (master para Mastercard)
#                 "payer": {
#                     "email": email,
#                     "identification": {
#                         "type": "CPF",
#                         "number": "12345678909"  # CPF do pagador
#                     }
#                 }
#             }

#             # Realiza o pagamento
#             payment_response = sdk.payment().create(payment_data)
#             payment = payment_response["response"]
#             print(f"Resposta da API: {payment}")  # Log da resposta completa

#             # Verifica o status do pagamento
#             if payment.get("status") == "approved":
#                 await interaction.followup.send(f"✅ Pagamento aprovado! ID: {payment['id']}", ephemeral=True)
#             else:
#                 status_detail = payment.get("status_detail", "N/A")
#                 await interaction.followup.send(
#                     f"❌ Pagamento não aprovado.\n"
#                     f"Status: {payment.get('status')}\n"
#                     f"Detalhes: {status_detail}\n"
#                     f"ID do pagamento: {payment.get('id', 'N/A')}",
#                     ephemeral=True
#                 )
#         except Exception as e:
#             print(f"Erro ao processar pagamento: {e}")  # Log de erro
#             await interaction.followup.send(f"⚠️ Erro ao processar o pagamento: {str(e)}", ephemeral=True)

# # Função para carregar o cog
# async def setup(bot):
#     await bot.add_cog(PagamentoCog(bot))


async def setup(bot):
    await bot.add_cog(cogCartao(bot))