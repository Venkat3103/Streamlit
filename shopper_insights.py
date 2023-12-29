import streamlit as st
import plotly.express as px
import pandas as pd

def insights(conn):
    st.title("Insights for shoppers")

    with st.expander("Average Order Amount Over Time"):
        query2 = """
        SELECT
            distinct(order_date),
            AVG(order_amount) OVER (ORDER BY order_date) AS avg_order_amount
        FROM
            orders.order_details
        ORDER BY
            order_date;
        """

        df2 = pd.read_sql(query2, conn)
        fig2 = px.line(df2, x='ORDER_DATE', y='AVG_ORDER_AMOUNT',
                    labels={'AVG_ORDER_AMOUNT': 'Average Order Amount'},
                    title="Average Order Amount Over Time",
                    line_shape='linear',
                    color_discrete_sequence=['lightcoral'])
        st.plotly_chart(fig2,use_container_width=True)

    with st.expander("Order Frequency Distribution"):
        query3 = """
        SELECT
            EXTRACT(DAY FROM order_date) AS order_day,
            COUNT(order_id) OVER (PARTITION BY EXTRACT(DAY FROM order_date)) AS order_count
        FROM
            orders.order_details
        ORDER BY
            order_day;
        """

        df3 = pd.read_sql(query3, conn)
        fig3 = px.bar(df3, x='ORDER_DAY', y='ORDER_COUNT',
                    labels={'ORDER_COUNT': 'Order Count'},
                    title="Order Frequency Distribution",
                    color_discrete_sequence=['green'])
        st.plotly_chart(fig3,use_container_width=True)

    with st.expander("Top Departments by Sales"):
        query4 = """
        SELECT
            DEPARTMENT,
            SUM(quantity * unit_price) AS total_sales
        FROM
            orders.order_items
            JOIN PRODUCT.product_catalogue USING (product_id)
        GROUP BY
            DEPARTMENT
        ORDER BY
            total_sales DESC
        LIMIT 10;
        """

        df4 = pd.read_sql(query4, conn)
        fig4 = px.bar(df4, x='DEPARTMENT', y='TOTAL_SALES',
                    labels={'TOTAL_SALES': 'Total Sales'},
                    title="Top Products by Sales",
                    color_discrete_sequence=['skyblue'])
        st.plotly_chart(fig4,use_container_width=True)

    with st.expander("Order Time Analysis"):
        query7 = """
        SELECT
            EXTRACT(HOUR FROM order_time) AS order_hour,
            COUNT(order_id) AS order_count
        FROM
            orders.order_details
        GROUP BY
            order_hour
        ORDER BY
            order_hour;
        """

        df7 = pd.read_sql(query7, conn)
        fig7 = px.bar(df7, x='ORDER_HOUR', y='ORDER_COUNT',
                    labels={'ORDER_COUNT': 'Order Count'},
                    title="Order Time Analysis",
                    color_discrete_sequence=['black'])
        st.plotly_chart(fig7,use_container_width=True)
