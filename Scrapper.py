from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO

# Configurar o driver do Edge
driver = webdriver.Edge()

# URL base com placeholders para a data
url_base = "https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-sistema-pregao-ptBR.asp?Data={}&Mercadoria=BGI"

# Configurar datas
start_date = datetime.strptime("01/01/2014", "%d/%m/%Y")
end_date = datetime.strptime("30/07/2024", "%d/%m/%Y")

# Abrir o arquivo CSV para escrita inicial e adicionar cabeçalhos
with open('dados_boi_gordo.csv', mode='w', newline='') as file:
    df_init = pd.DataFrame(columns=["Data", "VENCTO", "AJUSTE"])
    df_init.to_csv(file, index=False)

current_date = start_date

while current_date <= end_date:
    if current_date.weekday() < 5:  # Apenas dias úteis (segunda a sexta)
        try:
            # Formatar a data no formato dd/mm/yyyy
            formatted_date = current_date.strftime("%d/%m/%Y")
            # Construir o URL com a data atual
            url = url_base.format(formatted_date)
            
            # Navegar para o URL
            driver.get(url)
            
            # Obter o conteúdo da página
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Procurar a mensagem de dados não disponíveis
            no_data_message = soup.find(string="Não há dados para a data consultada.")
            
            if no_data_message:
                # Se não houver dados, adicionar uma linha nula
                with open('dados_boi_gordo.csv', mode='a', newline='') as file:
                    df_null = pd.DataFrame({
                        "Data": [formatted_date],
                        "VENCTO": ["NULL"],
                        "AJUSTE": ["NULL"]
                    })
                    df_null.to_csv(file, index=False, header=False)
                print(f"Dados não disponíveis para a data {formatted_date}. Registrado como NULL.")
            else:
                # Encontrar as tabelas principais
                table_vencto = soup.find('td', {'id': 'MercadoFut0'}).find('table')  # Tabela de VENCTO
                table_ajuste = soup.find('td', {'id': 'MercadoFut2'}).find('table')  # Tabela de AJUSTE

                # Extrair os dados de VENCTO e AJUSTE
                vencto_data = [row.text.strip() for row in table_vencto.find_all('td', class_='text-center')]
                ajuste_data = [row.text.strip() for row in table_ajuste.find_all('td', class_='text-right')[5::9]]  # Pega a coluna "AJUSTE"

                # Criar um DataFrame com VENCTO e AJUSTE
                df_filtered = pd.DataFrame({
                    "Data": [formatted_date] * len(vencto_data),
                    "VENCTO": vencto_data,
                    "AJUSTE": ajuste_data
                })
                
                # Salvar os dados diretamente no arquivo CSV
                with open('dados_boi_gordo.csv', mode='a', newline='') as file:
                    df_filtered.to_csv(file, index=False, header=False)
                print(f"Dados salvos para a data {formatted_date}.")
        
        except Exception as e:
            print(f"Ocorreu um erro na data {formatted_date}: {e}")
    
    # Incrementar a data
    current_date += timedelta(days=1)

# Fechar o navegador
driver.quit()
