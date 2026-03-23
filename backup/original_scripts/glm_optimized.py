import pandas as pd
import numpy as np
import statsmodels.api as sm
import holidays
import time
from datetime import timedelta
from scipy import sparse
import os

# ============ 并行计算设置（放在最开头）============
os.environ["OMP_NUM_THREADS"] = "8"
os.environ["OPENBLAS_NUM_THREADS"] = "8"
os.environ["MKL_NUM_THREADS"] = "8"

total_start = time.time()

def log_time(msg, start_time):
    elapsed = time.time() - start_time
    print(f"[{timedelta(seconds=int(elapsed))}] {msg}")

# ============ Step 1: 读取数据（优化数据类型）============
step_start = time.time()
data = pd.read_csv("RoadLinkData_V1.csv", low_memory=False,
                   dtype={'Avg mph': 'float32', 'Total Volume': 'float32',
                          'air_temperature': 'float32', 'prcp_amt': 'float32'})
data['datetime'] = pd.to_datetime(data['time'])
log_time(f"Step 1: 数据读取完成 ({len(data)} 行)", total_start)

# ============ Step 2: 清理数据 ============
mask = (~data['Avg mph'].isna()) & (data['Avg mph'] > 0) & (~data['prcp_amt'].isna()) & (~data['air_temperature'].isna())
data = data[mask].reset_index(drop=True)
log_time(f"Step 2: 数据清理完成 ({len(data)} 行)", total_start)

# ============ Step 3-6: 构建特征 ============
def is_school_term(dt_series):
    md = dt_series.dt.month * 100 + dt_series.dt.day
    autumn = ((md >= 901) & (md <= 1024)) | ((md >= 1103) & (md <= 1219))
    spring = ((md >= 105) & (md <= 213)) | ((md >= 223) & (md <= 327))
    summer = ((md >= 413) & (md <= 522)) | ((md >= 601) & (md <= 720))
    return (autumn | spring | summer).astype('int8')

def is_uni_term(dt_series):
    month = dt_series.dt.month
    day = dt_series.dt.day
    michaelmas = (month == 10) | (month == 11) | ((month == 12) & (day <= 6))
    lent = ((month == 1) & (day >= 17)) | (month == 2) | ((month == 3) & (day <= 16))
    easter = ((month == 4) & (day >= 24)) | (month == 5) | ((month == 6) & (day <= 15))
    return (michaelmas | lent | easter).astype('int8')

uk_holidays = holidays.UnitedKingdom()
holiday_set = set(uk_holidays.keys())

# 基础特征
print("构建基础特征...")
base_features = pd.DataFrame({
    'totalvolume': data['Total Volume'].astype('float32'),
    'schoolterm_t': is_school_term(data['datetime']),
    'universityterm_t': is_uni_term(data['datetime']),
    'bankholiday_t': data['datetime'].dt.date.isin(holiday_set).astype('int8'),
    'event_t': ((data['AnimalPresenceObstruction'].fillna(0) > 0) |
                (data['AbnormalTraffic'].fillna(0) > 0) |
                (data['GeneralObstruction'].fillna(0) > 0) |
                (data['EnvironmentalObstruction'].fillna(0) > 0) |
                (data['VehicleObstruction'].fillna(0) > 0)).astype('int8'),
    'roadworks_t': ((data['MaintenanceWorks'].fillna(0) > 0) |
                    (data['RoadOrCarriagewayOrLaneManagement'].fillna(0) > 0)).astype('int8'),
    'accident_t': data['Accident'].fillna(0).astype('int8'),
    'temperature_t': data['air_temperature'].astype('float32'),
    'precipitation_t': data['prcp_amt'].astype('float32'),
})
log_time("基础特征完成", total_start)

# 时间虚拟变量
print("构建时间虚拟变量...")
month_dummies = pd.get_dummies(data['datetime'].dt.month, prefix='month', drop_first=True, dtype='int8')
year_dummies = pd.get_dummies(data['datetime'].dt.year, prefix='year', drop_first=True, dtype='int8')
hour_dummies = pd.get_dummies(data['datetime'].dt.hour, prefix='hour', dtype='int8')
if 'hour_13' in hour_dummies.columns:
    hour_dummies = hour_dummies.drop('hour_13', axis=1)

dow_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
dow = data['datetime'].dt.dayofweek.map(dow_map)
dow_dummies = pd.get_dummies(dow, prefix='dow', dtype='int8')
for col in ['dow_Wed', 'dow_Sat', 'dow_Sun']:
    if col in dow_dummies.columns:
        dow_dummies = dow_dummies.drop(col, axis=1)
log_time("时间虚拟变量完成", total_start)

# Link 虚拟变量（使用稀疏矩阵）
print("构建 Link 虚拟变量...")
link_cat = data['link name'].astype('category')
link_codes = link_cat.cat.codes.values
n_samples = len(data)
n_links = len(link_cat.cat.categories)

# 创建稀疏的 one-hot 编码
link_sparse = sparse.csr_matrix(
    (np.ones(n_samples, dtype='float32'), (np.arange(n_samples), link_codes)),
    shape=(n_samples, n_links)
)
# 移除第一列（drop_first）
link_sparse = link_sparse[:, 1:]
link_names = [f'link_{cat}' for cat in link_cat.cat.categories[1:]]
log_time(f"Link 虚拟变量完成 ({n_links-1} 个)", total_start)

# 交互项
print("构建交互项...")
precip = data['prcp_amt'].fillna(0).values.astype('float32')
link_precip_sparse = link_sparse.multiply(precip.reshape(-1, 1))
link_precip_names = [f'{name}_precip' for name in link_names]
log_time("交互项完成", total_start)

# ============ Step 7: 合并特征 ============
print("合并所有特征...")
X_dense = pd.concat([base_features, month_dummies, year_dummies, hour_dummies, dow_dummies], axis=1)
X_dense = X_dense.astype('float32')

# 添加截距
X_dense.insert(0, 'const', 1.0)

# 转换为稀疏矩阵并合并
X_dense_sparse = sparse.csr_matrix(X_dense.values)
X_sparse = sparse.hstack([X_dense_sparse, link_sparse, link_precip_sparse], format='csr')

feature_names = ['const'] + list(X_dense.columns[1:]) + link_names + link_precip_names
log_time(f"特征合并完成 (共 {X_sparse.shape[1]} 个特征)", total_start)

y = data['Avg mph'].values.astype('float32')

# ============ Step 8: 运行回归 ============
print("\n" + "="*50)
print("开始运行 GLM Gamma 回归...")
print(f"样本量: {len(y):,}, 特征数: {X_sparse.shape[1]}")
print("="*50 + "\n")

# 转换为 dense（statsmodels 需要）
X_array = X_sparse.toarray().astype('float32')

gamma_model = sm.GLM(
    y,
    X_array,
    family=sm.families.Gamma(link=sm.families.links.Log())
)

result = gamma_model.fit(maxiter=100, method='lbfgs', disp=True)

log_time("回归完成!", total_start)
print("\n" + "="*50)
print(f"总用时: {timedelta(seconds=int(time.time() - total_start))}")
print("="*50 + "\n")

print(result.summary())

# 保存结果
result.save("gamma_glm_result.pkl")
print("\n结果已保存到 gamma_glm_result.pkl")
