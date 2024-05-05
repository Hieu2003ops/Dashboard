import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Python nhóm 117", layout="wide")

# Function to load data with caching to improve performance
@st.cache_data
def load_data(file_name, sheet_name):
    return pd.read_excel(file_name, sheet_name=sheet_name)
# dành cho dashboard 1 
# Function to calculate metrics with caching
@st.cache_data
def calculate_metrics(data):
    unique_customers = data['Mã khách hàng'].nunique()
    unique_orders = data['Mã đơn hàng'].nunique()
    unique_groups = data['Mã PKKH'].nunique()
    total_items = data['Mã mặt hàng'].nunique()
    return unique_customers, unique_orders, unique_groups, total_items

# General function to create plots with caching

def plot_data(data, group_col, agg_col, agg_func='sum', chart_type='bar', title=""):
    if agg_func == 'sum':
        agg_data = data.groupby(group_col)[agg_col].sum().reset_index()
    elif agg_func == 'mean':
        agg_data = data.groupby(group_col)[agg_col].mean().reset_index()
    elif agg_func == 'nunique':
        agg_data = data.groupby(group_col)[agg_col].nunique().reset_index()
    else:
        raise ValueError("Unsupported aggregation function")

    color_scale = px.colors.sequential.Rainbow_r
    if chart_type == 'bar':
        fig = px.bar(agg_data, x=group_col, y=agg_col, title=title,
                     color=agg_col, color_continuous_scale=color_scale)
    elif chart_type == 'line':
        fig = px.line(agg_data, x=group_col, y=agg_col, title=title,
                      markers=True, color_continuous_scale=color_scale)
    else:
        raise ValueError("Unsupported chart type")
    return fig


def plot_time_series(data, x_col, group_col, value_col, agg_func, title):
    if agg_func == 'sum':
        agg_data = data.groupby([x_col, group_col])[value_col].sum().reset_index()
    elif agg_func == 'nunique':
        agg_data = data.groupby([x_col, group_col])[value_col].nunique().reset_index()

    fig = px.line(agg_data, x=x_col, y=value_col, color=group_col,
                  title=title, labels={group_col: "Kiểu PKKH", x_col: "Tháng", value_col: "Giá trị"})
    return fig


# dành cho dashboard 2
@st.cache_data
def process_segments(data):
    unique_segments = data[['Mã PKKH', 'Mô tả Phân Khúc Khách hàng']].drop_duplicates().set_index('Mã PKKH')
    segment_counts = data.groupby('Mã PKKH')['Mã khách hàng'].nunique()
    segment_percentage = segment_counts / segment_counts.sum()
    segment_percentage = segment_percentage.reset_index(name="Tỉ lệ phần trăm")
    return unique_segments, segment_percentage

def plot_customer_distribution(segment_percentage):
    fig = px.pie(
        segment_percentage, 
        values='Tỉ lệ phần trăm', 
        names='Mã PKKH', 
        title='Phân phối khách hàng',
        color='Mã PKKH',
        color_discrete_sequence=px.colors.diverging.Portland_r
    )
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        title='<b>Phân phối khách hàng theo phân khúc RFM</b>',
        showlegend=True,
        autosize=True,
        width=400,  # Adjusted width for better visualization
        height=600  # Adjusted height to match the DataFrame's height
    )
    return fig


def main():
    # Load data
    data = load_data('ELC_117.xlsx', 'Data_full')

    # Create header in the center
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 60px;'>Dashboard Nhóm 117</h1>", unsafe_allow_html=True)

    # Create button-based tabs
    tabs = ["Tab 1", "Tab 2", "Tab 3", "Tab 4", "Tab 5"]
    tab_buttons = st.columns(len(tabs))
    current_tab = None
    for i, button in enumerate(tab_buttons):
        if button.button(tabs[i]):
            current_tab = tabs[i]
            break
    if current_tab is None:
        current_tab = tabs[0]

    # Layout and content adjustments
    if current_tab == "Tab 1":
        st.header("Tổng Quan Thị Trường")

        unique_customers, unique_orders, unique_groups, total_items = calculate_metrics(data)

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Tổng số khách hàng", f"{unique_customers:,}")
        col_b.metric("Tổng số đơn hàng", f"{unique_orders:,}")
        col_c.metric("Tổng số phân khúc khách hàng", f"{unique_groups:,}")
        col_d.metric("Tổng số mặt hàng", f"{total_items:,}")

        # Bar chart
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            fig_orders = plot_data(data, 'Kiểu PKKH', 'Mã đơn hàng', 'nunique', 'bar', 'Tổng số đơn hàng với Kiểu PKKH')
            st.plotly_chart(fig_orders)
        with chart_col2:
            fig_revenue = plot_data(data, 'Kiểu PKKH', 'Thành tiền', 'sum', 'bar', 'Tổng doanh thu với Kiểu PKKH')
            st.plotly_chart(fig_revenue)

        # Time series line charts on the same row
        time_series_charts = st.columns(2)
        with time_series_charts[0]:
            fig_order_time_series = plot_time_series(data, 'Tháng', 'Kiểu PKKH', 'Mã đơn hàng', 'nunique', 'Đơn hàng theo tháng và kiểu PKKH')
            st.plotly_chart(fig_order_time_series)
        with time_series_charts[1]:
            fig_revenue_time_series = plot_time_series(data, 'Tháng', 'Kiểu PKKH', 'Thành tiền', 'sum', 'Doanh thu theo tháng và kiểu PKKH')
            st.plotly_chart(fig_revenue_time_series)
    # Content for Tab 2
    elif current_tab == "Tab 2":
        st.header("Phân Tích Khách Hàng")
            # Process and cache unique segments and customer distribution
        unique_segments, segment_percentage = process_segments(data)
        
        # Layout for DataFrame and Pie Chart, adjust 'gap' for better spacing
        col1, col2 = st.columns([1, 1], gap="medium")
        
        with col1:
            st.markdown("### Bảng phân khúc khách hàng duy nhất:")
            # Improved display using st.table for a cleaner look
            st.table(unique_segments.style.format(precision=2).set_properties(**{'background-color': 'lightblue', 'color': 'black', 'border': '1px solid black'}))   
        with col2:
            st.markdown("### Phân phối khách hàng:")
            fig = plot_customer_distribution(segment_percentage)
            st.plotly_chart(fig, use_container_width=True)
            



            
    elif current_tab == "Tab 3":
        st.header("Phân Tích Doanh Thu")
    elif current_tab == "Tab 4":
        st.header("Phân Tích Hành Vi Mua")
    elif current_tab == "Tab 5":
        st.header("Phân Tích RFM")   
if __name__ == '__main__':
    main()
