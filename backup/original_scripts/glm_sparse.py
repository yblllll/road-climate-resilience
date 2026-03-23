import pandas as pd
import numpy as np
import holidays
import time
from datetime import timedelta
from scipy import sparse
import os
import sys

# ============ 并行计算设置 ============
os.environ["OMP_NUM_THREADS"] = "8"
os.environ["OPENBLAS_NUM_THREADS"] = "8"

total_start = time.time()

def log_time(msg, start_time):
    elapsed = time.time() - start_time
    print(f"[{timedelta(seconds=int(elapsed))}] {msg}")
    sys.stdout.flush()

def progress_bar(current, total, bar_length=40, prefix="Progress"):
    percent = current / total
    filled = int(bar_length * percent)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r{prefix}: [{bar}] {percent*100:.1f}% ({current}/{total})", end="")
    sys.stdout.flush()
    if current == total:
        print()

print("="*60)
print("GLM Gamma 回归 - 稀疏矩阵优化版")
print("="*60 + "\n")

# ============ Step 1: 读取数据 ============
print("Step 1/8: 读取数据...")
data = pd.read_csv("RoadLinkData_V1.csv", low_memory=False,
                   dtype={'Avg mph': 'float32', 'Total Volume': 'float32',
                          'air_temperature': 'float32', 'prcp_amt': 'float32'})
data['datetime'] = pd.to_datetime(data['time'])
log_time(f"数据读取完成 ({len(data):,} 行)", total_start)

# ============ Step 2: 清理数据 ============
print("\nStep 2/8: 清理数据...")
mask = (~data['Avg mph'].isna()) & (data['Avg mph'] > 0) & (~data['prcp_amt'].isna()) & (~data['air_temperature'].isna())
data = data[mask].reset_index(drop=True)
log_time(f"数据清理完成 ({len(data):,} 行)", total_start)

# ============ Step 3: 构建特征 ============
def is_school_term(dt_series):
    md = dt_series.dt.month * 100 + dt_series.dt.day
    autumn = ((md >= 901) & (md <= 1024)) | ((md >= 1103) & (md <= 1219))
    spring = ((md >= 105) & (md <= 213)) | ((md >= 223) & (md <= 327))
    summer = ((md >= 413) & (md <= 522)) | ((md >= 601) & (md <= 720))
    return (autumn | spring | summer).astype('float32')

def is_uni_term(dt_series):
    month = dt_series.dt.month
    day = dt_series.dt.day
    michaelmas = (month == 10) | (month == 11) | ((month == 12) & (day <= 6))
    lent = ((month == 1) & (day >= 17)) | (month == 2) | ((month == 3) & (day <= 16))
    easter = ((month == 4) & (day >= 24)) | (month == 5) | ((month == 6) & (day <= 15))
    return (michaelmas | lent | easter).astype('float32')

uk_holidays = holidays.UnitedKingdom()
holiday_set = set(uk_holidays.keys())

print("\nStep 3/8: 构建基础特征...")
base_features = pd.DataFrame({
    'totalvolume': data['Total Volume'].astype('float32'),
    'schoolterm_t': is_school_term(data['datetime']),
    'universityterm_t': is_uni_term(data['datetime']),
    'bankholiday_t': data['datetime'].dt.date.isin(holiday_set).astype('float32'),
    'event_t': ((data['AnimalPresenceObstruction'].fillna(0) > 0) |
                (data['AbnormalTraffic'].fillna(0) > 0) |
                (data['GeneralObstruction'].fillna(0) > 0) |
                (data['EnvironmentalObstruction'].fillna(0) > 0) |
                (data['VehicleObstruction'].fillna(0) > 0)).astype('float32'),
    'roadworks_t': ((data['MaintenanceWorks'].fillna(0) > 0) |
                    (data['RoadOrCarriagewayOrLaneManagement'].fillna(0) > 0)).astype('float32'),
    'accident_t': data['Accident'].fillna(0).astype('float32'),
    'temperature_t': data['air_temperature'].astype('float32'),
    'precipitation_t': data['prcp_amt'].astype('float32'),
})
log_time("基础特征完成", total_start)

# 时间虚拟变量
print("\nStep 4/8: 构建时间虚拟变量...")
month_dummies = pd.get_dummies(data['datetime'].dt.month, prefix='month', drop_first=True, dtype='float32')
year_dummies = pd.get_dummies(data['datetime'].dt.year, prefix='year', drop_first=True, dtype='float32')
hour_dummies = pd.get_dummies(data['datetime'].dt.hour, prefix='hour', dtype='float32')
if 'hour_13' in hour_dummies.columns:
    hour_dummies = hour_dummies.drop('hour_13', axis=1)

dow_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
dow = data['datetime'].dt.dayofweek.map(dow_map)
dow_dummies = pd.get_dummies(dow, prefix='dow', dtype='float32')
for col in ['dow_Wed', 'dow_Sat', 'dow_Sun']:
    if col in dow_dummies.columns:
        dow_dummies = dow_dummies.drop(col, axis=1)
log_time("时间虚拟变量完成", total_start)

# Link 虚拟变量（稀疏矩阵）
print("\nStep 5/8: 构建 Link 虚拟变量（稀疏）...")
link_cat = data['link name'].astype('category')
link_codes = link_cat.cat.codes.values
n_samples = len(data)
n_links = len(link_cat.cat.categories)

link_sparse = sparse.csr_matrix(
    (np.ones(n_samples, dtype='float32'), (np.arange(n_samples), link_codes)),
    shape=(n_samples, n_links)
)
link_sparse = link_sparse[:, 1:]  # drop_first
link_names = [f'link_{cat}' for cat in link_cat.cat.categories[1:]]
log_time(f"Link 虚拟变量完成 ({n_links-1} 个)", total_start)

# 交互项（稀疏）
print("\nStep 6/8: 构建交互项...")
precip = data['prcp_amt'].fillna(0).values.astype('float32')
link_precip_sparse = link_sparse.multiply(precip.reshape(-1, 1))
link_precip_names = [f'{name}_precip' for name in link_names]
log_time("交互项完成", total_start)

# ============ Step 7: 合并特征（保持稀疏）============
print("\nStep 7/8: 合并所有特征（稀疏矩阵）...")
X_dense = pd.concat([base_features, month_dummies, year_dummies, hour_dummies, dow_dummies], axis=1)
dense_names = list(X_dense.columns)

# 全部转为稀疏并合并
X_dense_sparse = sparse.csr_matrix(X_dense.values.astype('float32'))
X_sparse = sparse.hstack([X_dense_sparse, link_sparse, link_precip_sparse], format='csr')

feature_names = dense_names + link_names + link_precip_names
log_time(f"特征合并完成 (共 {X_sparse.shape[1]} 个特征)", total_start)

y = data['Avg mph'].values.astype('float32')

# 计算内存占用
sparse_memory_mb = (X_sparse.data.nbytes + X_sparse.indices.nbytes + X_sparse.indptr.nbytes) / 1024**2
print(f"稀疏矩阵内存占用: {sparse_memory_mb:.1f} MB")

# 释放内存
del data, base_features, month_dummies, year_dummies, hour_dummies, dow_dummies
del X_dense, link_sparse, link_precip_sparse
import gc
gc.collect()
log_time("内存清理完成", total_start)

# ============ Step 8: 运行 GLM ============
print("\n" + "="*60)
print("Step 8/8: 开始运行 GLM Gamma 回归")
print(f"样本量: {len(y):,}")
print(f"特征数: {X_sparse.shape[1]}")
print("="*60 + "\n")

model_start = time.time()

try:
    from glum import GeneralizedLinearRegressor

    print("使用 glum 库 (支持稀疏矩阵)...")
    print("迭代进度:")

    model = GeneralizedLinearRegressor(
        family='gamma',
        link='log',
        fit_intercept=True,
        max_iter=50,
        alpha=0.001,  # L2 正则化，解决共线性问题
        verbose=2
    )

    model.fit(X_sparse, y)

    model_time = time.time() - model_start
    log_time(f"模型拟合完成! (模型训练用时: {timedelta(seconds=int(model_time))})", total_start)

    # 输出结果
    print("\n" + "="*60)
    print("回归结果摘要")
    print("="*60)

    # 主要系数（非 link 相关）
    print("\n【主要变量系数】")
    print(f"{'变量':<25} {'系数':>15}")
    print("-"*40)
    print(f"{'Intercept':<25} {model.intercept_:>15.6f}")

    for name, coef in zip(feature_names, model.coef_):
        if not name.startswith('link_'):
            print(f"{name:<25} {coef:>15.6f}")

    # Link 系数（只显示前10个）
    print("\n【Link 变量系数 (前10个)】")
    link_coefs = [(name, coef) for name, coef in zip(feature_names, model.coef_)
                  if name.startswith('link_') and not name.endswith('_precip')]
    for name, coef in link_coefs[:10]:
        print(f"{name:<40} {coef:>15.6f}")
    print(f"... 共 {len(link_coefs)} 个 link 变量")

    # 保存完整结果
    results_df = pd.DataFrame({
        'feature': ['Intercept'] + feature_names,
        'coefficient': [model.intercept_] + list(model.coef_)
    })
    results_df.to_csv('gamma_glm_coefficients.csv', index=False)
    print(f"\n✓ 完整系数已保存到 gamma_glm_coefficients.csv")

except ImportError:
    print("\n" + "!"*60)
    print("错误: glum 库未安装")
    print("请运行: pip install glum")
    print("!"*60)

# 总结
print("\n" + "="*60)
print("运行完成!")
print(f"总用时: {timedelta(seconds=int(time.time() - total_start))}")
print("="*60)
