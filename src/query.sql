-- Consulta compatível com SQLite e bancos relacionais modernos
WITH cleaned_orders AS (
    SELECT 
        customer_id,
        strftime('%Y-%m-01', order_date) AS order_month
    FROM orders
    WHERE order_status = 'completed'
),

cohort_first_touch AS (
    SELECT 
        customer_id,
        MIN(order_month) AS cohort_month
    FROM cleaned_orders
    GROUP BY customer_id
),

cohort_monthly_activity AS (
    SELECT DISTINCT
        c.cohort_month,
        o.order_month,
        -- Cálculo da diferença em meses entre o mês da atividade e o mês de entrada
        (CAST(strftime('%Y', o.order_month) AS INTEGER) - CAST(strftime('%Y', c.cohort_month) AS INTEGER)) * 12 +
        (CAST(strftime('%m', o.order_month) AS INTEGER) - CAST(strftime('%m', c.cohort_month) AS INTEGER)) AS period_number,
        o.customer_id
    FROM cleaned_orders o
    INNER JOIN cohort_first_touch c ON o.customer_id = c.customer_id
)

SELECT 
    cohort_month,
    period_number,
    COUNT(DISTINCT customer_id) AS active_customers
FROM cohort_monthly_activity
GROUP BY cohort_month, period_number
ORDER BY cohort_month, period_number;