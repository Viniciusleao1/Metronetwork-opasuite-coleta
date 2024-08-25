from playwright.sync_api import sync_playwright
import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='pass',
        database='metronw-opasuite'
    )

def get_pending_conversations():
    login_url = "https://metronetwork.opasuite.com.br/atendente/login/"
    main_url = "https://metronetwork.opasuite.com.br/atendente/"
    username = "juliana.farias@metronetwork.com.br"
    password = "123mudar"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  
        page = browser.new_page()
        
        page.goto(login_url)
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        
        page.wait_for_load_state('networkidle')  
        
        page.goto(main_url)
        

        try:
 
            page.screenshot(path='screenshot.png')

            element = page.wait_for_selector('[data-id="aguard"]', timeout=30000)  
            if element:
                notif1_element = element.query_selector('.notif1')
                if notif1_element:
                    quantidade = int(notif1_element.inner_text().strip())
                    return quantidade
                else:
                    print("Elemento .notif1 não encontrado dentro do elemento com data-id='aguard'.")
                    return None
            else:
                print("Elemento com data-id='aguard' não encontrado.")
                return None
        except Exception as e:
            print(f"Erro ao encontrar o elemento: {e}")
            
            page.screenshot(path='error_screenshot.png')
            return None
        finally:
            browser.close()

def insert_pending_conversations(quantidade):
    if quantidade is not None:
        connection = connect_db()
        cursor = connection.cursor()
        try:
            query = "INSERT INTO aguardando (quantidade) VALUES (%s) ON DUPLICATE KEY UPDATE quantidade=%s"
            cursor.execute(query, (quantidade, quantidade))
            connection.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao inserir os dados: {err}")
        finally:
            cursor.close()
            connection.close()

def main():
    quantidade = get_pending_conversations()
    insert_pending_conversations(quantidade)

if __name__ == "__main__":
    main()
