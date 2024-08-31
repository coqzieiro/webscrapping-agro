from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import csv

# configurar o driver do Edge
driver = webdriver.Edge()

# abrir o site
driver.get("https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/derivativos/resumo-estatistico/sistema-pregao/")

# configurar datas
start_date = "01/01/2014"
end_date = "30/07/2024"

# converter strings de data para objetos datetime
current_date = datetime.strptime(start_date, "%d/%m/%Y")
end_date = datetime.strptime(end_date, "%d/%m/%Y")

# abrir o arquivo CSV para escrita e adicionar cabeçalhos
with open('dados_boi_gordo.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Data", "VENCTO", "AJUSTE"])

    # loop até a data atual atingir a data final
    while current_date <= end_date:
        try:
            # Esperar o campo de data estar disponível e preencher a data
            date_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "dData1")))
            date_field.clear()
            date_field.send_keys(current_date.strftime("%d/%m/%Y"))
            
            # selecionar a mercadoria "Boi gordo"
            select_mercadoria = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "comboMerc1")))
            for option in select_mercadoria.find_elements(By.TAG_NAME, 'option'):
                if option.text.strip() == "BGI  : Boi gordo":
                    option.click()
                    break
            
            # esperar os dados carregarem e extrair VENCTO e AJUSTE
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'VENCTO')]")))
            venctos = driver.find_elements(By.XPATH, "//td[@class='text-center'][1]")
            ajustes = driver.find_elements(By.XPATH, "//td[@class='text-center'][2]")
            
            # verificar se os dados foram encontrados
            if venctos and ajustes:
                # salvar dados em CSV
                for vencto, ajuste in zip(venctos, ajustes):
                    writer.writerow([current_date.strftime("%d/%m/%Y"), vencto.text, ajuste.text])
            else:
                print(f"Dados não encontrados para a data {current_date.strftime('%d/%m/%Y')}")
        
        except Exception as e:
            print(f"Ocorreu um erro na data {current_date.strftime('%d/%m/%Y')}: {e}")
        
        # atualizar a data (avançar um dia)
        current_date += timedelta(days=1)

# fechar o navegador
driver.quit()
