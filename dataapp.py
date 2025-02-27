import streamlit as st
import pandas as pd
import plotly.express as px

# Excelデータの読み込み（仮）
file_path = "/Users/isikawahirisi/Desktop/POSデータ分析/data.xlsx"  # 実際のパスに変更
@st.cache_data
def load_data():
    xls = pd.ExcelFile(file_path)
    df_this_year = pd.read_excel(xls, sheet_name="今年")
    df_last_year = pd.read_excel(xls, sheet_name="前年")
    return df_this_year, df_last_year

df_this_year, df_last_year = load_data()

# 店舗リストの取得
stores = df_this_year['店舗名'].unique()
st.sidebar.header("店舗選択")
selected_store = st.sidebar.selectbox("店舗を選んでください", stores)

# 選択した店舗のデータを抽出
df_store_this = df_this_year[df_this_year['店舗名'] == selected_store]
df_store_last = df_last_year[df_last_year['店舗名'] == selected_store]

# 売上前年比較
df_comparison = pd.merge(
    df_store_this[['部門名', '総計']],
    df_store_last[['部門名', '総計']].rename(columns={'総計': '総計_前年'}),
    on='部門名', how='left'
)
df_comparison['前年比(%)'] = ((df_comparison['総計'] - df_comparison['総計_前年']) / df_comparison['総計_前年']) * 100

# 部門別売上グラフ
fig = px.bar(df_comparison, x='部門名', y='前年比(%)', title='部門別 売上前年比', color='前年比(%)')
st.plotly_chart(fig)

# 高収益部門 vs 低収益部門
st.subheader("高収益部門 vs 低収益部門")
high_low_df = df_comparison.sort_values(by='総計', ascending=False)
st.write("上位5部門:")
st.write(high_low_df.head(5))
st.write("下位5部門:")
st.write(high_low_df.tail(5))

# 時間帯別売上
time_cols = df_store_this.columns[3:]
time_data = pd.DataFrame({
    '時間帯': time_cols,
    '今年': df_store_this[time_cols].sum().values,
    '前年': df_store_last[time_cols].sum().values
})
fig_time = px.line(time_data, x='時間帯', y=['今年', '前年'], title='時間帯別 売上推移')
st.plotly_chart(fig_time)

# 3つの時間帯の売上割合
time_ranges = {
    '06-10時': ['06時', '07時', '08時', '09時', '10時'],
    '11-15時': ['11時', '12時', '13時', '14時', '15時'],
    '16-23時': ['16時', '17時', '18時', '19時', '20時', '21時', '22時', '23時']
}

def calculate_time_ratio(df, time_ranges):
    total_sales = df[time_cols].sum().sum()
    ratios = {key: df[times].sum().sum() / total_sales * 100 for key, times in time_ranges.items()}
    return pd.Series(ratios)

ratios_this_year = calculate_time_ratio(df_store_this, time_ranges)
ratios_last_year = calculate_time_ratio(df_store_last, time_ranges)

df_time_ratio = pd.DataFrame({
    '時間帯': ratios_this_year.index,
    '今年の割合(%)': ratios_this_year.values,
    '前年の割合(%)': ratios_last_year.values,
    '差分(%)': ratios_this_year.values - ratios_last_year.values
})

# 時間帯別の売上割合グラフ
fig_ratio = px.bar(df_time_ratio, x='時間帯', y=['今年の割合(%)', '前年の割合(%)'],
                    title='時間帯別 売上割合', barmode='group')
st.plotly_chart(fig_ratio)

# 問題点の洗い出し & アクションプランの提案
st.subheader("問題点の洗い出し & アクションプラン")
if df_comparison['前年比(%)'].min() < -5:
    st.write("売上が大幅に減少している部門があります。特に商品ラインナップやプロモーションの見直しを検討しましょう。")
else:
    st.write("全体的に安定した売上ですが、成長のための追加施策を検討してください。")
