import streamlit as st
import pandas as pd
from database import get_initial_df

def fetch_filtered_data(df,department, min_price, max_price, limit, offset):
    return df[(df.DEPARTMENT.isin(department)&(df.PRICE>=min_price)&(df.PRICE<=max_price))].sort_values(by=['DEPARTMENT','PRODUCT_NAME','PRICE'])[offset*limit:((offset*limit)+limit)][['DEPARTMENT','PRODUCT_NAME','PRICE','Quantity','Select']]
   
def dataframe_with_selections(df):
    print("entered")
    df_with_selections = df.copy()
    #df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=("PRODUCT_NAME","DEPARTMENT","PRICE")
    )
    print(edited_df.columns)
    print(edited_df.shape)
    if edited_df.shape[0]>0:
        selected_rows = edited_df[edited_df.Select]
    else:
        selected_rows = edited_df
    print(selected_rows.columns)
    print("selection passed")
    print(selected_rows.columns)
    selected_rows.drop('Select', axis=1)
    print("drop passed")
    return edited_df, selected_rows.drop('Select', axis=1)

def order_page(conn):
    
    if "edited_data" not in st.session_state:
        st.session_state.df = get_initial_df(conn)
        print("entered")
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
    st.write(st.session_state)
    print("Initial print:",st.session_state.df)
    department = st.multiselect("Select department(s):", options=st.session_state.df.DEPARTMENT.unique())
    min_price, max_price = st.slider("Select Price Range:", min_value=st.session_state.df.PRICE.min(), max_value=st.session_state.df.PRICE.max(), value=(st.session_state.df.PRICE.min(), st.session_state.df.PRICE.max()))   
    st.session_state.department = department
    st.session_state.min_price = min_price
    st.session_state.max_price = max_price

    filtered_data = fetch_filtered_data(st.session_state.df,department, min_price, max_price, 10, offset=st.session_state.page_number)
    #st.session_state.df[st.session_state.df['department'].isin(department)]
    print(filtered_data.shape[0])
    prev_button_col, _, next_button_col = st.columns([1, 8, 1])
     # Place "Previous" button on the left bottom
    if prev_button_col.button("Prev") and st.session_state.page_number>0:
        print("Prev Clicked")
        st.session_state.page_number -= 1

    # Place "Next" button on the right bottom
    if next_button_col.button("Next"):
        #st.session_state.page_number<=filtered_data.shape[0]//10
        st.session_state.page_number += 1
        print("Next Clicked")

    if st.session_state.department!=st.session_state.prev_department or st.session_state.min_price!=st.session_state.prev_min_price or st.session_state.max_price!=st.session_state.prev_max_price or st.session_state.page_number!=st.session_state.prev_page_number:
        #st.session_state.total_order = pd.concat([st.session_state.total_order,st.session_state.selection])

        print("edited_data:",st.session_state.edited_data)
        print("df before update:",st.session_state.df)
        # Merging the two dataframes on the specified columns
        print("edited_data after parameter change:\n",st.session_state.edited_data)
        print("selection after parameter change:\n",st.session_state.selection)
        print("df after parameter change:\n",st.session_state.df)
        merged_df = pd.merge(st.session_state.df, st.session_state.edited_data,
                            on=['PRODUCT_NAME', 'DEPARTMENT', 'PRICE'],
                            how='left', suffixes=('', '_edited'))
        merged_df['Select'] = merged_df['Select_edited'].combine_first(merged_df['Select'])
        merged_df['Quantity'] = merged_df['Quantity_edited'].combine_first(merged_df['Quantity'])
        print("data after merging:",merged_df)
        merged_df = merged_df.drop(columns=['Select_edited','Quantity_edited'])
        merged_df.loc[merged_df['Select'] == False, 'Quantity'] = 0
        st.session_state.df = merged_df
        st.session_state.prev_department = st.session_state.department
        st.session_state.prev_min_price = st.session_state.min_price
        st.session_state.prev_max_price = st.session_state.max_price
        st.session_state.prev_page_number = st.session_state.page_number
        if st.session_state.department!=st.session_state.prev_department or st.session_state.min_price!=st.session_state.prev_min_price or st.session_state.max_price!=st.session_state.prev_max_price:
            st.session_state.page_number = 0
    
    #st.dataframe(fetch_data(department=departments, min_price=min_price, max_price=max_price, limit=10, offset=10), use_container_width=True)

    st.session_state.edited_data,st.session_state.selection = dataframe_with_selections(filtered_data)
    st.write("Edited Data:")
    st.write(st.session_state.edited_data)
    st.write("Your selection:")
    st.write(st.session_state.selection)
    st.write("All Orders:")
    #st.write(st.session_state.total_order)
    with st.container():
        st.write("Your order:")
        st.write(st.session_state.df[(st.session_state.df['Select'])&(st.session_state.df['Quantity']!=0)].drop('Select', axis=1))
        if st.button("Checkout"):
            merged_df = pd.merge(st.session_state.df, st.session_state.edited_data,
                            on=['PRODUCT_NAME', 'DEPARTMENT', 'PRICE'],
                            how='left', suffixes=('', '_edited'))
            print("columns before dropping:",merged_df.columns)
            # Filling NaN values in the "Select" column with False (unchecked) for rows not present in df1
            merged_df['Select'] = merged_df['Select_edited'].combine_first(merged_df['Select'])
            merged_df['Quantity'] = merged_df['Quantity_edited'].combine_first(merged_df['Quantity'])
            print("data after merging:",merged_df)
            # Dropping the redundant column used for merging
            merged_df = merged_df.drop(columns=['Select_edited','Quantity_edited'])
            print("columns after dropping:",merged_df.columns)
            #merged_df = merged_df.drop('Quantity_edited', axis=1)
            merged_df.loc[merged_df['Select'] == False, 'Quantity'] = 0
            print(merged_df)
            st.session_state.df = merged_df
            #st.write(st.session_state.df[(st.session_state.df['Select'])&(st.session_state.df['Quantity']!=0)].drop('Select', axis=1))
            st.session_state["page"] = "checkout"
