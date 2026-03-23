import pandas as pd
import numpy as np
import statsmodels.api as sm
import holidays
import time
from datetime import timedelta
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

print("="*60)
print("GLM Gamma 回归 - statsmodels 版本（含显著性检验）")
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

# ============ Step 2.5: 采样 ============
SAMPLE_FRAC = 0.2  # 采样比例，可以调整
print(f"\nStep 2.5: 随机采样 {SAMPLE_FRAC*100:.0f}% 数据...")
data = data.sample(frac=SAMPLE_FRAC, random_state=42).reset_index(drop=True)
log_time(f"采样完成 ({len(data):,} 行)", total_start)

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

# Link 虚拟变量
print("\nStep 5/8: 构建 Link 虚拟变量...")
link_dummies = pd.get_dummies(data['link name'], prefix='link', drop_first=True, dtype='float32')
log_time(f"Link 虚拟变量完成 ({len(link_dummies.columns)} 个)", total_start)

# 交互项
print("\nStep 6/8: 构建交互项...")
precip = data['prcp_amt'].fillna(0).values.astype('float32')
link_precip = link_dummies.multiply(precip, axis=0)
link_precip.columns = [f'{col}_precip' for col in link_dummies.columns]
log_time("交互项完成", total_start)

# ============ Step 7: 合并特征 ============
print("\nStep 7/8: 合并所有特征...")
X = pd.concat([base_features, month_dummies, year_dummies, hour_dummies, dow_dummies,
               link_dummies, link_precip], axis=1)
X = X.astype('float32')
log_time(f"特征合并完成 (共 {X.shape[1]} 个特征)", total_start)

y = data['Avg mph'].values.astype('float32')

# 释放内存
del data, base_features, month_dummies, year_dummies, hour_dummies, dow_dummies
del link_dummies, link_precip
import gc
gc.collect()

# 添加截距
X_with_const = sm.add_constant(X, has_constant='add')
log_time("截距添加完成", total_start)

# ============ Step 8: 运行 GLM ============
print("\n" + "="*60)
print("Step 8/8: 开始运行 GLM Gamma 回归 (statsmodels)")
print(f"样本量: {len(y):,}")
print(f"特征数: {X_with_const.shape[1]}")
print("="*60 + "\n")

model_start = time.time()

gamma_model = sm.GLM(
    y,
    X_with_const,
    family=sm.families.Gamma(link=sm.families.links.Log())
)

print("正在拟合模型，请稍候...")
result = gamma_model.fit(maxiter=100, method='lbfgs', disp=True)

model_time = time.time() - model_start
log_time(f"模型拟合完成! (模型训练用时: {timedelta(seconds=int(model_time))})", total_start)

# 输出结果
print("\n" + "="*60)
print("完整回归结果")
print("="*60)
print(result.summary())

# 保存结果
# 1. 保存 summary 到文本文件
with open('gamma_glm_summary.txt', 'w') as f:
    f.write(str(result.summary()))
print("\n✓ 完整 summary 已保存到 gamma_glm_summary.txt")

# 2. 保存系数表到 CSV（含标准误、z值、p值、置信区间）
summary_df = pd.DataFrame({
    'feature': result.params.index,
    'coefficient': result.params.values,
    'std_err': result.bse.values,
    'z_value': result.tvalues.values,
    'p_value': result.pvalues.values,
    'conf_int_lower': result.conf_int()[0].values,
    'conf_int_upper': result.conf_int()[1].values
})
summary_df.to_csv('gamma_glm_full_results.csv', index=False)
print("✓ 系数表（含显著性）已保存到 gamma_glm_full_results.csv")

# 3. 模型拟合指标
print("\n【模型拟合指标】")
print(f"AIC: {result.aic:.2f}")
print(f"BIC: {result.bic:.2f}")
print(f"Deviance: {result.deviance:.2f}")
print(f"Pearson Chi2: {result.pearson_chi2:.2f}")
print(f"Log-Likelihood: {result.llf:.2f}")

# 总结
print("\n" + "="*60)
print("运行完成!")
print(f"总用时: {timedelta(seconds=int(time.time() - total_start))}")
print("="*60)
