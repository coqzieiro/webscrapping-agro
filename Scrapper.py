from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import csv

# Configurar o driver do Edge
driver = webdriver.Edge()

# Abrir o site
driver.get("https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-sistema-pregao-ptBR.asp")

# Configurar datas
start_date = datetime.strptime("01/01/2014", "%d/%m/%Y")
end_date = datetime.strptime("30/07/2024", "%d/%m/%Y")

# Abrir o arquivo CSV para escrita e adicionar cabeçalhos
with open('dados_boi_gordo.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Data", "VENCTO", "AJUSTE"])

    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:  # Considerar apenas dias úteis (segunda a sexta)
            try:
                # Esperar o campo de data estar disponível e clicar para abrir o calendário
                date_field = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "dData1")))
                date_field.click()

                # Selecionar o dia no calendário
                day_to_select = WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                    (By.XPATH, f"//a[@class='ui-state-default' and text()='{current_date.day}']")))
                day_to_select.click()
                
                # Selecionar a mercadoria "Boi gordo"
                select_mercadoria = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "comboMerc1")))
                select_mercadoria.click()
                
                # Usar JavaScript para rolar até a opção "BGI  : Boi gordo" e clicar
                options = select_mercadoria.find_elements(By.TAG_NAME, 'option')
                for option in options:
                    if "BGI  : Boi gordo" in option.text.strip():
                        driver.execute_script("arguments[0].scrollIntoView(true);", option)
                        option.click()
                        break
                
                # Verificar se a opção foi selecionada corretamente
                selected_option = select_mercadoria.find_element(By.CSS_SELECTOR, "option:checked").text
                if "BGI  : Boi gordo" not in selected_option:
                    raise Exception("Erro ao selecionar a mercadoria 'BGI : Boi gordo'")

                # Trocar para o iframe onde a tabela está presente
                iframe = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@id, 'bvmf_iframe')]")))
                driver.switch_to.frame(iframe)
                
                # Esperar os dados carregarem e extrair VENCTO e AJUSTE
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'VENCTO')]")))
                venctos = driver.find_elements(By.XPATH, "//td[@class='text-center'][1]")
                ajustes = driver.find_elements(By.XPATH, "//td[@class='text-center'][6]")  # Coluna de ajuste
                
                # Verificar se os dados foram encontrados
                if venctos and ajustes:
                    for vencto, ajuste in zip(venctos, ajustes):
                        writer.writerow([current_date.strftime("%d/%m/%Y"), vencto.text, ajuste.text])
                else:
                    print(f"Dados não encontrados para a data {current_date.strftime('%d/%m/%Y')}")
            
                driver.switch_to.default_content()
            
            except Exception as e:
                print(f"Ocorreu um erro na data {current_date.strftime('%d/%m/%Y')}: {e}")
        
        current_date += timedelta(days=1)

# Fechar o navegador
driver.quit()
