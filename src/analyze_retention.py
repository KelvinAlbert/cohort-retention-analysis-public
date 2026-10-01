import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def run_cohort_pipeline():
    db_path = os.path.join('data', 'database.sqlite')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Banco de dados '{db_path}' não encontrado. Execute generate_data.py primeiro.")

    os.makedirs('output', exist_ok=True)
    
    # 1. Carregando a consulta analítica
    with open(os.path.join('src', 'query.sql'), 'r', encoding='utf-8') as f:
        sql_query = f.read()
    
    print("Executando agregações analíticas no SQLite...")
    conn = sqlite3.connect(db_path)
    df_raw = pd.read_sql_query(sql_query, conn)
    conn.close()

    # 2. Pivotando os dados para construir a matriz de contagem absoluta
    cohort_counts = df_raw.pivot(
        index='cohort_month', 
        columns='period_number', 
        values='active_customers'
    )

    # 3. Calculando a Matriz de Retenção Percentual
    # A coluna 0 representa o tamanho original (Mês 0 = 100%)
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention_matrix = cohort_counts.divide(cohort_sizes, axis=0)

    # 4. Formatação e Plotagem
    plt.figure(figsize=(13, 7))
    sns.set_theme(style='white')

    # Paleta corporativa customizada
    ax = sns.heatmap(
        retention_matrix, 
        annot=True, 
        fmt='.1%', 
        cmap='Blues', 
        vmin=0.0, 
        vmax=0.5,
        linewidths=1.0,
        linecolor='#ffffff',
        cbar_kws={'label': 'Taxa de Retenção'}
    )

    plt.title('Matriz de Retenção de Clientes por Cohort Mensal', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Meses Decorridos após a 1ª Compra (Período 0 = Aquisição)', fontsize=11, labelpad=10)
    plt.ylabel('Safra de Aquisição (Cohort)', fontsize=11, labelpad=10)
    
    plt.tight_layout()
    output_image_path = os.path.join('output', 'cohort_retention_matrix.png')
    plt.savefig(output_image_path, dpi=300)
    plt.close()
    
    print(f"Sucesso: Matriz de retenção gerada em '{output_image_path}'.")

if __name__ == "__main__":
    run_cohort_pipeline()