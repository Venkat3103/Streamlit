import streamlit as st
import pandas as pd
from database import get_initial_df

def fetch_filtered_data(df,department, min_price, max_price):
    print(department)
    return df[(df.DEPARTMENT==department)&(df.PRICE>=min_price)&(df.PRICE<=max_price)].sort_values(by=['DEPARTMENT','PRODUCT_NAME','PRICE'])[['DEPARTMENT','PRODUCT_NAME','PRICE','Quantity','Select']]
   
def dataframe_with_selections(df):
    df_with_selections = df.copy()
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=("PRODUCT_NAME","DEPARTMENT","PRICE")
    )
    if edited_df.shape[0]>0:
        selected_rows = edited_df[edited_df.Select]
    else:
        selected_rows = edited_df
    selected_rows.drop('Select', axis=1)
    return edited_df, selected_rows.drop('Select', axis=1)

def merge_data():
    merged_df = pd.merge(st.session_state.df, st.session_state.edited_data,
                            on=['PRODUCT_NAME', 'DEPARTMENT', 'PRICE'],
                            how='left', suffixes=('', '_edited'))
    merged_df['Select'] = merged_df['Select_edited'].combine_first(merged_df['Select'])
    merged_df['Quantity'] = merged_df['Quantity_edited'].combine_first(merged_df['Quantity'])
    merged_df = merged_df.drop(columns=['Select_edited','Quantity_edited'])
    merged_df.loc[merged_df['Select'] == False, 'Quantity'] = 0
    if st.session_state.department!=st.session_state.prev_department or st.session_state.min_price!=st.session_state.prev_min_price or st.session_state.max_price!=st.session_state.prev_max_price:
        st.session_state.page_number = 0
        st.session_state.prev_page_number = 0
    st.session_state.df = merged_df
    st.session_state.prev_department = st.session_state.department
    st.session_state.prev_min_price = st.session_state.min_price
    st.session_state.prev_max_price = st.session_state.max_price
    st.session_state.prev_page_number = st.session_state.page_number
    return 

def order_page(conn):
    
    if "edited_data" not in st.session_state:
        st.session_state.df = get_initial_df(conn)
        st.session_state.edited_data = st.session_state.df.copy()
    if "selection" not in st.session_state:
        st.session_state.selection = pd.DataFrame(columns = st.session_state.df.columns)
    if "prev_department" not in st.session_state:
        st.session_state.prev_department = []
    if "department" not in st.session_state:
        st.session_state.department = []
    if "max_price" not in st.session_state:
        st.session_state.max_price = -1
    if "min_price" not in st.session_state:
        st.session_state.min_price = -1
    if "page_number" not in st.session_state:
        st.session_state.page_number = 0
    if "prev_max_price" not in st.session_state:
        st.session_state.prev_max_price = -1
    if "prev_min_price" not in st.session_state:
        st.session_state.prev_min_price = -1
    if "prev_page_number" not in st.session_state:
        st.session_state.prev_page_number = 0
    #if "total_order" not in st.session_state:
        #st.session_state.total_order = pd.DataFrame(columns=st.session_state.df.columns)
    department = st.selectbox("Select department(s):", options=st.session_state.df.DEPARTMENT.unique())
    min_price, max_price = st.slider("Select Price Range:", min_value=st.session_state.df.PRICE.min(), max_value=st.session_state.df.PRICE.max(), value=(st.session_state.df.PRICE.min(), st.session_state.df.PRICE.max()))   
    st.session_state.department = department
    st.session_state.min_price = min_price
    st.session_state.max_price = max_price
    limit = 10
    st.session_state.filtered_data = fetch_filtered_data(st.session_state.df,department, min_price, max_price)
    if st.session_state.department!=st.session_state.prev_department or st.session_state.min_price!=st.session_state.prev_min_price or st.session_state.max_price!=st.session_state.prev_max_price or st.session_state.page_number!=st.session_state.prev_page_number:
       print("inside first if")
       merge_data()
    
    prev_button_col, _, next_button_col = st.columns([1, 8, 1])

    if prev_button_col.button("Prev") and st.session_state.page_number>0:
        print("Prev Clicked")
        st.session_state.page_number -= 1

    if next_button_col.button("Next") and st.session_state.page_number<=st.session_state.edited_data.shape[0]//10:
        print("Next Clicked")
        st.session_state.page_number += 1
    st.session_state.edited_data,st.session_state.selection = dataframe_with_selections(st.session_state.filtered_data[st.session_state.page_number*limit:((st.session_state.page_number*limit)+limit)])

    
    st.write("Your selection:")
    st.write(st.session_state.selection)
    with st.container():
        st.write("Your order:")
        st.write(st.session_state.df[(st.session_state.df['Select'])&(st.session_state.df['Quantity']!=0)].drop('Select', axis=1))
        if st.button("Checkout"):
            merge_data()
            st.session_state["page"] = "checkout"
            st.rerun()
