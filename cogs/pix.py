import discord
import mercadopago
from discord.ext import commands
import sqlite3
import qrcode
from io import BytesIO
import json
import threading
import asyncio
import datetime

class PixCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sdk = mercadopago.SDK("APP_USR-858971298465680-021921-8b0ac97868ffc64211357c5da2beb2fc-259696807")  # Substitua pelo seu Access Token
        #self.start_flask_server()

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

    async def pix(self, user, thread):

        conn = sqlite3.connect('produtos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT produto_id, quantia FROM carrinho WHERE usuario = ?", (str(user.id),))
        carrinhos = cursor.fetchall()
        conn.close()
        
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

        payment_data = {
            "transaction_amount": float(arredonda),
            "description": "Pagamento via PIX",
            "payment_method_id": "pix",
            "payer": {
                "email": "pagador@exemplo.com"  # E-mail fictício
            }
        }
        payment_response = self.sdk.payment().create(payment_data)
        
        if payment_response["status"] == 201:
            payment_info = payment_response["response"]
            try:
                # Obter dados do PIX
                qrcode_data = payment_info["point_of_interaction"]["transaction_data"]["qr_code"]

                """Gera uma imagem de QR Code a partir dos dados fornecidos."""
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qrcode_data)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                img_io = BytesIO()
                img.save(img_io, format="PNG")
                img_io.seek(0)
                qr_image = discord.File(img_io, filename="pix_qrcode.png")

                # Enviar o QR Code e o código de copia e cola para o canal
                await thread.send(
                    f"⚠️⚠️Nós não fazemos **reembolso ou estorno** de pagamentos!!!⚠️⚠️\n\n🚨Lembre-se de deixar sua **DM ativa** para o bot poder enviar os produtos diretamente no seu privado!🚨\n\n⏱️ Você tem **10 minutos** para fazer o pagamento ou o pedido será cancelado!!!\n\n🔹 **PIX para pagamento de R${valorTotal:.2f}:**",
                )

                embed = discord.Embed(
                    title=f"📌 **Copia e Cola:**",
                    description=f"`{qrcode_data}`",
                    color=discord.Color.green()
                )
                embed.set_image(url="attachment://pix_qrcode.png")
                await thread.send(embed=embed, file=qr_image)
                

                payment_id = payment_info["id"]
                print('payment id ', payment_id)
                
                produtos_json = json.dumps(produtos)  # Converter lista para JSON
                conn = sqlite3.connect('produtos.db')
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO pagamentosAbertos (payment_id, canal_id, usuario_id, produtos)
                                VALUES (?, ?, ?, ?)''', 
                            (payment_id, thread.id, user.id, produtos_json))
                conn.commit()
                conn.close()

                conn = sqlite3.connect('produtos.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM carrinho WHERE usuario = ?", (str(user.id),))
                conn.commit()
                conn.close()
                # print(payment_id, thread.id, user.id, produtos_json)
                # await self.verificar_pagamento(payment_id, thread, arredonda, produtos, user)

            except KeyError:
                await thread.send("❌ Ocorreu um erro ao gerar o QR Code para o pagamento PIX.")
                await self.devolveChaves(produtos)
        else:
            error_message = payment_response.get("response", {}).get("message", "Erro desconhecido")
            await thread.send(f"❌ Ocorreu um erro ao gerar o pagamento: `{error_message}`")
            await self.devolveChaves(produtos)

    async def verificar_pagamento(self, payment_id: int, canal: discord.TextChannel, valor: float, produtos, user):
        """
        Verifica periodicamente o status do pagamento e notifica quando confirmado.

        :param payment_id: ID do pagamento no Mercado Pago.
        :param canal: Canal do Discord para enviar a notificação.
        :param valor: Valor do pagamento.
        """
        tempo = 0
        while True:
            await asyncio.sleep(10)  # Verifica a cada 30 segundos
            tempo = tempo + 1
            print('verifica pagamento', tempo)
            conn = sqlite3.connect('produtos.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carrinho WHERE usuario = ?", (str(user.id),))
            conn.commit()
            conn.close()

            # Consulta o status do pagamento
            payment_response = self.sdk.payment().get(payment_id)
            if payment_response["status"] == 200:
                payment_info = payment_response["response"]
                status = payment_info["status"]
                #status = "approved"
                print(status)
                if status == "approved":
                    await canal.send(f"✅ **Pagamento de R${valor:.2f} confirmado!** Obrigado!")
                    data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    for id in produtos:
                        print(id[0], 'perarararara', produtos)
                        conn = sqlite3.connect('produtos.db')
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT produto_id, chave FROM chaves_produtos WHERE id = {float(id[0])}")
                        produtes = cursor.fetchall()
                        conn.close()

                        for produto_id, cheves in produtes:
                                conn = sqlite3.connect('produtos.db')
                                cursor = conn.cursor()
                                cursor.execute("SELECT preco FROM produtos WHERE id = ?", (produto_id,))
                                produto = cursor.fetchone()
                                conn.close()
                                

                                await canal.send(f"🔑 chave do produto {produto_id}: {cheves}")
                                conn = sqlite3.connect('produtos.db')
                                cursor = conn.cursor()
                                cursor.execute('''INSERT INTO vendas (produto_id, chave, usuario, valor, data)
                                                VALUES (?, ?, ?, ?, ?)''', 
                                            (produto_id, cheves, str(user.id), produto[0], data_atual))
                                conn.commit()
                                conn.close()

                    for id in produtos:
                        print(id[0], 'perarararara', produtos)
                        conn = sqlite3.connect('produtos.db')
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT produto_id, chave FROM chaves_produtos WHERE id = {float(id[0])}")
                        produtes = cursor.fetchall()
                        conn.close()

                        try:
                            for produto_id, cheves in produtes:
                                await user.send(f"🔑 chave do produto {produto_id}: {cheves}")
                        except:
                            await canal.send("🚨 SEU PRIVADO ESTÁ BLOQUEADO, os produtos não forma enviados diretamnete no seu privado")
                            break 
                    await canal.edit(name=f"PAGO-{data_atual}_{str(user.id)}")
                    await canal.edit(archived=True)
                    break
                elif tempo == 60 and status in ["pending", "in_process"]:
                    print('tempo acabou')
                    if canal:
                        try:
                            await canal.purge(limit=100)
                            await canal.send(f"❌ Tempo para pagamento acabou")
                            await canal.delete()
                        except:
                            print('chat do carrinho nao existe mais')
                    await self.devolveChaves(produtos)

                    cancel_data = {
                        "status": "cancelled"
                    }
                    cancel_response = self.sdk.payment().update(payment_id, cancel_data)
                    if cancel_response["status"] == 200:
                        print(f"Pagamento de ID {payment_id} foi cancelado com sucesso!")
                    else:
                        print(f"Erro ao cancelar pagamento de ID {payment_id}: {cancel_response['response']['message']}")
                    break
                elif status in ["pending", "in_process"]:
                    continue  # Continua verificando
                else:
                    await canal.send(f"❌ O pagamento de R${valor:.2f} foi cancelado ou recusado.")
                    await self.devolveChaves(produtos)
                    break
            else:
                await canal.send("❌ Erro ao verificar o status do pagamento.")
                break


async def setup(bot):
    await bot.add_cog(PixCog(bot))
    #git status, add ., commit -m "msg", push