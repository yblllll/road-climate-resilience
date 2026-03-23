# Interaction Terms Analysis Report
## Road Climate Resilience Regression Models

**Generated:** 2026-01-31
**Analysis Type:** Extraction of interaction terms from linear regression results
**Models Analyzed:** 2 (Negative Binomial Volume + Gamma Speed)

---

## Executive Summary

Total interaction terms extracted: **32**
- Temperature interactions: 16
- Precipitation interactions: 16
- Highways included: 8 roads
- Statistically significant interactions (p < 0.05): 20

### Key Findings:

**Traffic Volume (Negative Binomial Model):**
- 7 significant interactions identified
- Highway A428 & Temperature: strongest positive effect (coef = 0.0087)
- Highway A14M & Temperature: strongest negative effect (coef = -0.0068)

**Average Speed (Gamma GLM Model):**
- 13 significant interactions identified
- Highway A47 & Temperature: strongest negative effect (coef = -0.0046)
- Highway A14 & Temperature: significant negative effect (coef = -0.0010)

---

## Model 1: Negative Binomial Regression (Traffic Volume)

**Dependent Variable:** Total Volume (number of vehicles)
**Model Type:** Negative Binomial with log link
**Observations:** 7,090,984
**Number of Features:** 72

### Interaction Terms (16 total)

#### Temperature Interactions (Highway_X_Temp)

| Highway | Coefficient | Std. Error | z-value | p-value | Significant | Effect |
|---------|-------------|-----------|---------|---------|-------------|--------|
| A11 | 0.0065 | 0.0000 | 22.170 | 0.000 | **YES** | Positive |
| A14 | -0.0002 | 0.0000 | -1.081 | 0.280 | NO | Neutral |
| A14M | -0.0068 | 0.0000 | -21.319 | 0.000 | **YES** | Negative |
| A1M | -0.0012 | 0.0000 | -6.302 | 0.000 | **YES** | Negative |
| A428 | 0.0087 | 0.0000 | 36.419 | 0.000 | **YES** | Positive |
| A47 | 0.0048 | 0.0000 | 14.307 | 0.000 | **YES** | Positive |
| Cambourne Road | -0.0121 | 0.001 | -11.551 | 0.000 | **YES** | Negative |
| M11 | -0.0004 | 0.0000 | -2.037 | 0.042 | **YES** | Negative |

**Interpretation:**
- Higher temperatures increase volume on A11, A428, A47
- Higher temperatures decrease volume on A14M, A1M, Cambourne Road, M11

#### Precipitation Interactions (Highway_X_Precip)

| Highway | Coefficient | Std. Error | z-value | p-value | Significant | Effect |
|---------|-------------|-----------|---------|---------|-------------|--------|
| A11 | 0.0005 | 0.004 | 0.124 | 0.901 | NO | Neutral |
| A14 | 0.0032 | 0.002 | 1.801 | 0.072 | NO | Neutral |
| A14M | 0.0012 | 0.004 | 0.303 | 0.762 | NO | Neutral |
| A1M | -0.0012 | 0.002 | -0.486 | 0.627 | NO | Neutral |
| A428 | -0.0011 | 0.003 | -0.374 | 0.708 | NO | Neutral |
| A47 | -0.0107 | 0.004 | -2.422 | 0.015 | **YES** | Negative |
| Cambourne Road | -0.0369 | 0.013 | -2.914 | 0.004 | **YES** | Negative |
| M11 | 0.0009 | 0.003 | 0.367 | 0.714 | NO | Neutral |

**Interpretation:**
- Precipitation has minimal impact on most highways
- A47 and Cambourne Road show significant negative precipitation effects
- Most precipitation effects are not statistically significant

---

## Model 2: Gamma GLM Regression (Average Speed)

**Dependent Variable:** Avg mph (average speed in miles per hour)
**Model Type:** Gamma with log link
**Observations:** 7,071,231
**Number of Features:** 72

### Interaction Terms (16 total)

#### Temperature Interactions (Highway_X_Temp)

| Highway | Coefficient | Std. Error | z-value | p-value | Significant | Effect |
|---------|-------------|-----------|---------|---------|-------------|--------|
| A11 | -0.0018 | 0.0000687 | -26.465 | 0.000 | **YES** | Negative |
| A14 | -0.0010 | 0.000033 | -30.203 | 0.000 | **YES** | Negative |
| A14M | -0.0017 | 0.0000746 | -22.830 | 0.000 | **YES** | Negative |
| A1M | -0.0008 | 0.0000461 | -16.720 | 0.000 | **YES** | Negative |
| A428 | -0.0002 | 0.0000564 | -3.031 | 0.002 | **YES** | Negative |
| A47 | -0.0046 | 0.0000803 | -57.441 | 0.000 | **YES** | Negative |
| Cambourne Road | -0.0009 | 0.0000 | -3.740 | 0.000 | **YES** | Negative |
| M11 | -0.0011 | 0.0000461 | -23.905 | 0.000 | **YES** | Negative |

**Interpretation:**
- ALL temperature interactions are significant and NEGATIVE
- Higher temperatures consistently decrease speeds on all highways
- Strongest effect on A47 (coef = -0.0046)
- Weakest effect on A428 (coef = -0.0002)

#### Precipitation Interactions (Highway_X_Precip)

| Highway | Coefficient | Std. Error | z-value | p-value | Significant | Effect |
|---------|-------------|-----------|---------|---------|-------------|--------|
| A11 | -0.0041 | 0.001 | -4.622 | 0.000 | **YES** | Negative |
| A14 | -0.0004 | 0.0000 | -0.928 | 0.353 | NO | Neutral |
| A14M | -0.0049 | 0.001 | -5.362 | 0.000 | **YES** | Negative |
| A1M | -0.0020 | 0.001 | -3.377 | 0.001 | **YES** | Negative |
| A428 | -0.0086 | 0.001 | -12.030 | 0.000 | **YES** | Negative |
| A47 | -0.0019 | 0.001 | -1.763 | 0.078 | NO | Neutral |
| Cambourne Road | -0.0043 | 0.003 | -1.506 | 0.132 | NO | Neutral |
| M11 | -0.0060 | 0.001 | -10.185 | 0.000 | **YES** | Negative |

**Interpretation:**
- Precipitation generally reduces speeds
- 5 out of 8 precipitation interactions are statistically significant
- Strongest negative effect: A428 (coef = -0.0086)
- No positive precipitation effects on any highway

---

## Comparative Analysis

### By Highway

#### A11 (London-North Road)
| Interaction | Model | Coefficient | p-value | Significant |
|-------------|-------|-------------|---------|-------------|
| Temperature | Volume | 0.0065 | 0.000 | YES - increases volume |
| Precipitation | Volume | 0.0005 | 0.901 | NO |
| Temperature | Speed | -0.0018 | 0.000 | YES - decreases speed |
| Precipitation | Speed | -0.0041 | 0.000 | YES - decreases speed |

#### A14 (Cambridge-Huntingdon)
| Interaction | Model | Coefficient | p-value | Significant |
|-------------|-------|-------------|---------|-------------|
| Temperature | Volume | -0.0002 | 0.280 | NO |
| Precipitation | Volume | 0.0032 | 0.072 | NO |
| Temperature | Speed | -0.0010 | 0.000 | YES - decreases speed |
| Precipitation | Speed | -0.0004 | 0.353 | NO |

#### A14M (A14 Motorway)
| Interaction | Model | Coefficient | p-value | Significant |
|-------------|-------|-------------|---------|-------------|
| Temperature | Volume | -0.0068 | 0.000 | YES - decreases volume |
| Precipitation | Volume | 0.0012 | 0.762 | NO |
| Temperature | Speed | -0.0017 | 0.000 | YES - decreases speed |
| Precipitation | Speed | -0.0049 | 0.000 | YES - decreases speed |

#### A1M (A1 Motorway)
| Interaction | Model | Coefficient | p-value | Significant |
|-------------|-------|-------------|---------|-------------|
| Temperature | Volume | -0.0012 | 0.000 | YES - decreases volume |
| Precipitation | Volume | -0.0012 | 0.627 | NO |
| Temperature | Speed | -0.0008 | 0.000 | YES - decreases speed |
| Precipitation | Speed | -0.0020 | 0.001 | YES - decreases speed |

#### A428 (Cambridge-Oxford)
| Interaction | Model | Coefficient | p-value | Significant |
|-------------|-------|-------------|---------|-------------|
| Temperature | Volume | 0.0087 | 0.000 | YES - increases volume |
| Precipitation | Volume | -0.0011 | 0.708 | NO |
| Temperature | Speed | -0.0002 | 0.002 | YES - decreases speed |
| Precipitation | Speed | -0.0086 | 0.000 | YES - decreases speed |

#### A47 (Cambridge-Norwich)
| Interaction | Model | Coefficient | p-value | Significant |
|-------------|-------|-------------|---------|-------------|
| Temperature | Volume | 0.0048 | 0.000 | YES - increases volume |
| Precipitation | Volume | -0.0107 | 0.015 | YES - decreases volume |
| Temperature | Speed | -0.0046 | 0.000 | YES - decreases speed |
| Precipitation | Speed | -0.0019 | 0.078 | NO |

#### Cambourne Road
| Interaction | Model | Coefficient | p-value | Significant |
|-------------|-------|-------------|---------|-------------|
| Temperature | Volume | -0.0121 | 0.000 | YES - decreases volume |
| Precipitation | Volume | -0.0369 | 0.004 | YES - decreases volume |
| Temperature | Speed | -0.0009 | 0.000 | YES - decreases speed |
| Precipitation | Speed | -0.0043 | 0.132 | NO |

#### M11 (London-Cambridge)
| Interaction | Model | Coefficient | p-value | Significant |
|-------------|-------|-------------|---------|-------------|
| Temperature | Volume | -0.0004 | 0.042 | YES - decreases volume |
| Precipitation | Volume | 0.0009 | 0.714 | NO |
| Temperature | Speed | -0.0011 | 0.000 | YES - decreases speed |
| Precipitation | Speed | -0.0060 | 0.000 | YES - decreases speed |

---

## Key Insights

### 1. Temperature Effects
- **Volume Model:** Mixed effects - temperature increases volume on some highways (A11, A428, A47) but decreases it on others (A14M, A1M, Cambourne Road, M11)
- **Speed Model:** Universally negative - higher temperatures reduce speeds on ALL highways
- **Most sensitive highway to temperature (Speed):** A47 with coefficient of -0.0046

### 2. Precipitation Effects
- **Volume Model:** Mostly non-significant, except A47 and Cambourne Road show significant decreases
- **Speed Model:** More significant effects than volume model; 5 out of 8 highways show significant negative precipitation effects
- **Most sensitive highway to precipitation (Speed):** A428 with coefficient of -0.0086

### 3. Highway-Specific Patterns

**High-Sensitivity Highways (most vulnerable to climate variables):**
1. **A428:** Strong temperature sensitivity in volume (coef = 0.0087) and precipitation sensitivity in speed (coef = -0.0086)
2. **A47:** Strong precipitation effect in volume (coef = -0.0107) and temperature effect in speed (coef = -0.0046)
3. **Cambourne Road:** Multiple significant effects in both models

**Low-Sensitivity Highways:**
1. **A14:** Minimal interaction effects in volume model
2. **A428:** Weak temperature effect in speed model (coef = -0.0002)

### 4. Resilience Implications

- **Speed is more sensitive to climate:** All temperature interactions significant in speed model vs. only 6/8 in volume model
- **Precipitation primarily affects speed, not volume:** Most precipitation effects on speed
- **Road type matters:** Motorways (A14M, A1M, M11) show consistent negative temperature effects on volume
- **Regional roads vary:** A roads (A11, A14, A47, A428) show more varied responses

---

## Statistical Quality

- **Sample Size:** 7M+ observations per model
- **Model Convergence:** Both models converged successfully
- **Confidence:** Very high due to large sample sizes and low standard errors
- **Range of p-values:** 0.000 to 0.901 (highly variable significance)
- **Effect Sizes:** Generally small coefficients (0.0001 to 0.0087 range) but significant due to large sample

---

## Data Files Generated

1. **interaction_terms_summary.csv** - CSV format with all 32 interaction terms
2. **interaction_terms_summary.json** - Comprehensive JSON structure with full statistics
3. **INTERACTION_TERMS_ANALYSIS.md** - This markdown report

---

## Notes for Further Analysis

1. Consider creating visualization comparing coefficient magnitudes across highways
2. Analyze why volume and speed respond differently to same climate variables
3. Investigate motorway vs. A-road patterns separately
4. Consider temporal variations in these effects (seasonal, time-of-day)
5. Examine whether different traffic states (congested vs. free-flow) show different patterns

---

**End of Report**
