* Export full GLM results with SEs, p-values, and model statistics
* Run this in Stata after loading RoadLinkData_V3_cleaned.dta

clear all
set more off

* Load data
use "/Users/ybl/Desktop/Postdoc research/Cambridgeshire Climate Stress Test - Linear Regression/Data/Final Data/Regression/Road Climate Resilience/Road Link Level/RoadLinkData_V3_cleaned.dta", clear

* Run the GLM
glm avgmph totalvolume schoolterm_t universityterm_t bankholiday_t event_t roadworks_t accident_t temperature_t temp_below0_past6h day_mon day_tue day_thu day_fri highway_a11 highway_a14 highway_a14m highway_a1m highway_a428 highway_a47 highway_cambourne_road highway_m11 i.month i.year ib12.hour ib146.linkname_num##c.precipitation_t if avgmph != . & day_sat == 0 & day_sun == 0, family(gamma) link(log) vce(cluster linkname_num)

* Export coefficient table with SEs, z, p, CI
matrix b = e(b)
matrix V = e(V)
matrix se = vecdiag(cholesky(diag(vecdiag(V))))

* Use esttab/estout if available, otherwise manual export
capture which esttab
if _rc == 0 {
    esttab using "/Users/ybl/Desktop/Postdoc research/DARe's flex fund project/road-climate-resilience/data/example/stata_glm_results.csv", cells("b se t p ci_l ci_u") plain replace
}
else {
    * Manual export using putexcel or matrix approach
    putexcel set "/Users/ybl/Desktop/Postdoc research/DARe's flex fund project/road-climate-resilience/data/example/stata_glm_results.xlsx", replace
    putexcel A1 = matrix(r(table)'), names
}

* Export model statistics
local output_path "/Users/ybl/Desktop/Postdoc research/DARe's flex fund project/road-climate-resilience/data/example/stata_model_stats.csv"

file open stats using "`output_path'", write replace
file write stats "statistic,value" _n
file write stats "n_obs," (e(N)) _n
file write stats "n_clusters," (e(N_clust)) _n
file write stats "deviance," (e(deviance)) _n
file write stats "pearson_chi2," (e(deviance_p)) _n
file write stats "aic," (e(aic)) _n
file write stats "bic," (e(bic)) _n
file write stats "log_likelihood," (e(ll)) _n
file write stats "df_model," (e(df_m)) _n
file write stats "df_residual," (e(df)) _n
file write stats "deviance_per_df," (e(deviance)/e(df)) _n
file write stats "pearson_per_df," (e(deviance_p)/e(df)) _n
file close stats

di "Model statistics exported to: `output_path'"

* Also export using matrix list for full coefficient details
matrix results = r(table)'
svmat results, names(col)

* Simple CSV export of all coefficients
preserve
clear
matrix coefs = r(table)'
local names : rownames coefs
local k = rowsof(coefs)
set obs `k'
gen feature = ""
gen coefficient = .
gen std_err = .
gen z_value = .
gen p_value = .
gen conf_int_lower = .
gen conf_int_upper = .

forvalues i = 1/`k' {
    local name : word `i' of `names'
    replace feature = "`name'" in `i'
    replace coefficient = coefs[`i', 1] in `i'
    replace std_err = coefs[`i', 2] in `i'
    replace z_value = coefs[`i', 3] in `i'
    replace p_value = coefs[`i', 4] in `i'
    replace conf_int_lower = coefs[`i', 5] in `i'
    replace conf_int_upper = coefs[`i', 6] in `i'
}

export delimited using "/Users/ybl/Desktop/Postdoc research/DARe's flex fund project/road-climate-resilience/data/example/gamma_glm_full_results.csv", replace
restore

di "Done! Full results exported."
