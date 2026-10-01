import sqlite3
import random
from datetime import datetime, timedelta
import os

def create_database():
    os.makedirs('data', exist_ok=True)
    db_path = os.path.join('data', 'database.sqlite')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criação da tabela de pedidos
    cursor.execute("""
    DROP TABLE IF EXISTS orders;
    """)
    
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        order_status TEXT NOT NULL,
        total_amount REAL NOT NULL
    );
    """)
    
    print("Criando registros sintéticos com padrão realista de compras...")
    
    # Parâmetros da simulação
    random.seed(42)
    num_customers = 600
    base_start_date = datetime(2025, 1, 1)
    orders_to_insert = []
    
    for customer_id in range(1, num_customers + 1):
        # Cada cliente entra em uma data aleatória ao longo do primeiro semestre
        acquisition_offset_days = random.randint(0, 180)
        first_purchase_date = base_start_date + timedelta(days=acquisition_offset_days)
        
        # Primeira compra (sempre realizada e concluída)
        orders_to_insert.append((
            customer_id,
            first_purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
            'completed',
            round(random.uniform(50.0, 350.0), 2)
        ))
        
        # Simula compras recorrentes subsequentes nos próximos meses
        # A probabilidade de recompra decai naturalmente (churn)
        current_date = first_purchase_date
        churn_chance = 0.65 # Taxa de perda esperada inicial
        
        for month_step in range(1, 12):
            if random.random() > churn_chance:
                current_date += timedelta(days=random.randint(25, 35))
                if current_date > datetime(2026, 6, 30):
                    break
                
                status = 'completed' if random.random() > 0.05 else 'cancelled'
                orders_to_insert.append((
                    customer_id,
                    current_date.strftime('%Y-%m-%d %H:%M:%S'),
                    status,
                    round(random.uniform(40.0, 450.0), 2)
                ))
            else:
                # Se não recomprou neste ciclo, a chance de retorno diminui ainda mais
                churn_chance = min(churn_chance + 0.1, 0.95)
    
    cursor.executemany("""
    INSERT INTO orders (customer_id, order_date, order_status, total_amount)
    VALUES (?, ?, ?, ?);
    """, orders_to_insert)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM orders;")
    total_orders = cursor.fetchone()[0]
    conn.close()
    
    print(f"Sucesso: Banco criado em '{db_path}' com {total_orders} pedidos registrados.")

if __name__ == "__main__":
    create_database()