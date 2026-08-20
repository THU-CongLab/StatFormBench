Prompt_book='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

{
    "background": "Relevant description of the problem context (which may also contain some data)",
    "data": "The data used, presented as a table in LaTeX code",
    "question": "The core problem"
}

The abstracted statistical model includes the following four parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- "Data Preprocessing" includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].  

- "Mathematical Calculation" includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].  

- "Numerical Computation" includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].  

- "Descriptive Statistics" includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].  

- The "Data Distribution Modelling" section includes: ["Model Building", "MLE", "Bayesian"].

- "Data Visualization" includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].  

- "Association Analysis" includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].  

- "Clustering" includes only: ["Clustering"].  

- "Dimensionality Reduction" includes only: ["Dimensionality Reduction"].  

- "Hypothesis Testing and Interval Estimation" includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include corresponding interval estimation methods.)  

- "Model Comparison (Variable Selection)" includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].  

- "Model Diagnosis" includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].  

- "Model Interpretation" includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].  

- "Classification and Prediction" includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].  

- "Time Series Analysis" includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].  

- "Text Data Analysis" includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].  

- "Network Data Analysis" includes: ["Community Detection", "Link Prediction"].  

- "Experimental Design" includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].  

- "Causal Inference" includes: ["Observational Data", "Experimental Data"].  

- "Critical Evaluation of Statistical Results" includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].  

2. Relevant variables and their roles (variables)  
Key requirements:  
    1. Variables specifically refer to the data objects collected for the research objective in the question and their statistical measures (e.g., sample size, mean, standard deviation), excluding model parameters, statistics related to specific statistical models/distributions (e.g., z-score, p-value), and statistics related to specific statistical methods (e.g., t-value, F-value).  
    2. Variable objects can be raw data columns, grouped statistics, contingency tables, sample sizes, success counts, or time variables.  
    3. In particular, if the problem to be solved in the question is of the "Mathematical Calculation" type, please treat the numerical objects such as probabilities and sample sizes actually used in the answer as variable objects for extraction.
    4. If no explicit data table is provided or `data` is empty, but symbolic variables, statistics, or logical judgment objects (e.g., `X`, `Y`, `r`, an event, a statistic) have already appeared, variables must still be extracted accordingly.  
    5. When the original data has a grouping structure, prioritize splitting the data into multiple variables according to the grouping. If each sample belongs to different groups based on different grouping methods, after splitting, additionally note in the description of these variables that they share the same samples with certain other variables but represent different groupings/features.  
    6. If the problem provides aggregated measures for multiple variables (e.g., mean, standard deviation, sample size), create a separate variable object for each variable and write these aggregated measures into the `value` field of each variable object in JSON format.  
    7. If the information is insufficient to support any variables, directly output an empty JSON: `{}`.  
    8. The output must be strictly JSON, with the top-level keys being variable IDs, and no additional text should be output.  

Field specifications:  
- Top-level key: "Variable name (extracted from the problem or an appropriately assigned variable name)".  
- `id`: Variable identifier, must exactly match the top-level key.  
- `value`: The complete value of the current variable. If it is a column from a table, an array can be used; if it is aggregated measures (including statistics, sample size, etc.), a JSON value can be used (keys are the names of the aggregated measures, and values are the corresponding values); if neither of the above forms is suitable for representation, copy and paste the original recorded form of the variable from the problem (e.g., a table recorded in TeX syntax). When there are multiple numerical values in `value`, ensure their order matches the original order in the problem.  
- `class`: Can only be one of `numerical`, `categorical`, or `others`. (Numerical type is denoted as "numerical", categorical type as "categorical", and those not belonging to the above categories as "others".)  
- `role`: Can only be one of `X`, `Y`, `XY`, or `NR`.  
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  
> Special cases for `role`:  
    1. For "Trends Over Time" problems under "Data Visualization," the variable representing the time concept must be assigned as `X`, and the variable changing over time as `Y` (even if the time variable does not appear in the variable set). For example, when studying the sales trend over different time points, the time variable is `X`, and the sales variable is `Y`.  
    2. If a variable serves both as an independent variable and is used to construct the dependent variable, its role is `X`.  
    3. If a variable serves both as a dependent variable and is used to construct the independent variable, its role is `Y`.  
- `description`: A brief description of the variable object.  

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. A complete output example is as follows:  

{
  "category": "Relationship Between Continuous Variables",
   "variables": {
    "X_height": {
      "id": "X_height",
      "value": {
        "μ": 138,
        "σ": 7
      },
      "class": "numerical",
      "role": "NR",
      "description": "Heights of 10-year-old boys, following a Normal distribution with population mean μ=138 cm and population standard deviation σ=7 cm."
    },
    "threshold": {
      "id": "threshold",
      "value": 150,
      "class": "numerical",
      "role": "NR",
      "description": "The cutoff value (150 cm) used in the answer to compute the proportion of the population below this height, directly substituted into the z-score formula z=(150−138)/7."
    }
  }
}

'''


Prompt_case='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

The input format for user's inquiry questions is:
{
"background": " Relevant description of the problem context",
"data_description_1": "The specific details of the dataset provided by",
"data_description_2": "(If applicable) The description of the data formatting, including data types, data shapes, variable names, and basic statistical information fields",
"question": " The core problem" 
}

The abstracted statistical model includes the following four parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- "Data Preprocessing" includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].  

- "Mathematical Calculation" includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].  

- "Numerical Computation" includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].  

- "Descriptive Statistics" includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].  

- The "Data Distribution Modelling" section includes: ["Model Building", "MLE", "Bayesian"].

- "Data Visualization" includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].  

- "Association Analysis" includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].  

- "Clustering" includes only: ["Clustering"].  

- "Dimensionality Reduction" includes only: ["Dimensionality Reduction"].  

- "Hypothesis Testing and Interval Estimation" includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include corresponding interval estimation methods.)  

- "Model Comparison (Variable Selection)" includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].  

- "Model Diagnosis" includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].  

- "Model Interpretation" includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].  

- "Classification and Prediction" includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].  

- "Time Series Analysis" includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].  

- "Text Data Analysis" includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].  

- "Network Data Analysis" includes: ["Community Detection", "Link Prediction"].  

- "Experimental Design" includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].  

- "Causal Inference" includes: ["Observational Data", "Experimental Data"].  

- "Critical Evaluation of Statistical Results" includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].  

2. Relevant Variables
- These are the original variable names involved in the statistical model. If the INPUT contains a field named "data_description_2" with data formatting description, the variable name must be consistent with the variable name provided in the data formatting description. Otherwise, the returned result will be an empty dictionary {}.
- The format of the data variable is {Dataset Name (suffix ".pkl" of the file name, the first key from the "data_description_2" field): [Variable Name 1, Variable Name 2, ...]
- Variable selection follows a streamlined principle. Some variables that are not necessary in the analysis process (such as "Sample Number" etc.) should be excluded. 

3. Variable roles refer to the functions of each variable in the statistical model, and they can be classified into the following four categories: 
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  

Special Cases: 
- For "time variation trend" type questions in "data visualization", the variable representing the concept of time should be set as the independent variable, and the variable that changes over time should be set as the dependent variable (even if a time variable does not appear in the variable set). For example, when studying the trend of sales volume at different time points, the time variable is set as the independent variable and the sales volume variable is set as the dependent variable.
- If a variable serves as both an independent variable and is used to construct the dependent variable, its role is set as independent. 
- If a variable serves as both a dependent variable and is used to construct an independent variable, its role is set as dependent. 
Format: {Dataset Name (file name with .pkl extension, derived from the first key of the "data_description_2" field)}: [Variable Name 1 Role Name, Variable Name 2 Role Name, ...], The roles of the variables can only be one of "X", "Y", "XY", or "NR", and must be in the same order as the corresponding variable names in the "variable" field. 
Note: If the "variable" field is an empty dictionary {}, then the "role" field must also be an empty dictionary {}.

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. A complete output example is as follows:  

{
      "category": "Relationship Between Discrete and Continuous Variables",
      "variable": {
        "HotPotForMac.pkl": [
          "people",
          "quarterly sales volume"
        ]
      },
      "role": {
        "HotPotForMac.pkl": [
          "X",
          "Y"
        ]
      }
    }

'''

Prompt_0_one='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

{
    "background": "Relevant description of the problem context (which may also contain some data)",
    "data": "The data used, presented as a table in LaTeX code",
    "question": "The core problem"
}

The abstracted statistical model includes the following four parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- "Data Preprocessing" includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].  

- "Mathematical Calculation" includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].  

- "Numerical Computation" includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].  

- "Descriptive Statistics" includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].  

- The "Data Distribution Modelling" section includes: ["Model Building", "MLE", "Bayesian"].

- "Data Visualization" includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].  

- "Association Analysis" includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].  

- "Clustering" includes only: ["Clustering"].  

- "Dimensionality Reduction" includes only: ["Dimensionality Reduction"].  

- "Hypothesis Testing and Interval Estimation" includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include corresponding interval estimation methods.)  

- "Model Comparison (Variable Selection)" includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].  

- "Model Diagnosis" includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].  

- "Model Interpretation" includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].  

- "Classification and Prediction" includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].  

- "Time Series Analysis" includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].  

- "Text Data Analysis" includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].  

- "Network Data Analysis" includes: ["Community Detection", "Link Prediction"].  

- "Experimental Design" includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].  

- "Causal Inference" includes: ["Observational Data", "Experimental Data"].  

- "Critical Evaluation of Statistical Results" includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].  

2. Relevant variables and their roles (variables)  
Key requirements:  
    1. Variables specifically refer to the data objects collected for the research objective in the question and their statistical measures (e.g., sample size, mean, standard deviation), excluding model parameters, statistics related to specific statistical models/distributions (e.g., z-score, p-value), and statistics related to specific statistical methods (e.g., t-value, F-value).  
    2. Variable objects can be raw data columns, grouped statistics, contingency tables, sample sizes, success counts, or time variables.  
    3. In particular, if the problem to be solved in the question is of the "Mathematical Calculation" type, please treat the numerical objects such as probabilities and sample sizes actually used in the answer as variable objects for extraction.
    4. If no explicit data table is provided or `data` is empty, but symbolic variables, statistics, or logical judgment objects (e.g., `X`, `Y`, `r`, an event, a statistic) have already appeared, variables must still be extracted accordingly.  
    5. When the original data has a grouping structure, prioritize splitting the data into multiple variables according to the grouping. If each sample belongs to different groups based on different grouping methods, after splitting, additionally note in the description of these variables that they share the same samples with certain other variables but represent different groupings/features.  
    6. If the problem provides aggregated measures for multiple variables (e.g., mean, standard deviation, sample size), create a separate variable object for each variable and write these aggregated measures into the `value` field of each variable object in JSON format.  
    7. If the information is insufficient to support any variables, directly output an empty JSON: `{}`.  
    8. The output must be strictly JSON, with the top-level keys being variable IDs, and no additional text should be output.  

Field specifications:  
- Top-level key: "Variable name (extracted from the problem or an appropriately assigned variable name)".  
- `id`: Variable identifier, must exactly match the top-level key.  
- `value`: The complete value of the current variable. If it is a column from a table, an array can be used; if it is aggregated measures (including statistics, sample size, etc.), a JSON value can be used (keys are the names of the aggregated measures, and values are the corresponding values); if neither of the above forms is suitable for representation, copy and paste the original recorded form of the variable from the problem (e.g., a table recorded in TeX syntax). When there are multiple numerical values in `value`, ensure their order matches the original order in the problem.  
- `class`: Can only be one of `numerical`, `categorical`, or `others`. (Numerical type is denoted as "numerical", categorical type as "categorical", and those not belonging to the above categories as "others".)  
- `role`: Can only be one of `X`, `Y`, `XY`, or `NR`.  
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  
> Special cases for `role`:  
    1. For "Trends Over Time" problems under "Data Visualization," the variable representing the time concept must be assigned as `X`, and the variable changing over time as `Y` (even if the time variable does not appear in the variable set). For example, when studying the sales trend over different time points, the time variable is `X`, and the sales variable is `Y`.  
    2. If a variable serves both as an independent variable and is used to construct the dependent variable, its role is `X`.  
    3. If a variable serves both as a dependent variable and is used to construct the independent variable, its role is `Y`.  
- `description`: A brief description of the variable object.  

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. 

Here is an instance:

Input:

{
  "background": "A manufacturer claims that the average lifespan of their light bulbs is 1500 hours. A consumer protection agency takes a random sample of 8 bulbs to test this claim. The measured lifespans (in hours) are recorded.",
  "data": "\\begin{tabular}{c} Lifespan (hours) \\\\ \\hline 1453 \\\\ 1489 \\\\ 1512 \\\\ 1478 \\\\ 1496 \\\\ 1521 \\\\ 1465 \\\\ 1502 \\end{tabular}",
  "question": "Is there sufficient evidence at the 5% significance level to conclude that the true mean lifespan differs from 1500 hours?"
}

Output:

{
  "category": "Mean Test",
  "variables": {
    "lifespan_sample": {
      "id": "lifespan_sample",
      "value": [1453, 1489, 1512, 1478, 1496, 1521, 1465, 1502],
      "class": "numerical",
      "role": "NR",
      "description": "Measured lifespans (in hours) of 8 randomly selected light bulbs."
    },
    "mu0": {
      "id": "mu0",
      "value": 1500,
      "class": "numerical",
      "role": "NR",
      "description": "Hypothesized population mean lifespan under the null hypothesis."
    }
  }
}
'''


Prompt_0_two='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

{
    "background": "Relevant description of the problem context (which may also contain some data)",
    "data": "The data used, presented as a table in LaTeX code",
    "question": "The core problem"
}

The abstracted statistical model includes the following four parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- "Data Preprocessing" includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].  

- "Mathematical Calculation" includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].  

- "Numerical Computation" includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].  

- "Descriptive Statistics" includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].  

- The "Data Distribution Modelling" section includes: ["Model Building", "MLE", "Bayesian"].

- "Data Visualization" includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].  

- "Association Analysis" includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].  

- "Clustering" includes only: ["Clustering"].  

- "Dimensionality Reduction" includes only: ["Dimensionality Reduction"].  

- "Hypothesis Testing and Interval Estimation" includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include corresponding interval estimation methods.)  

- "Model Comparison (Variable Selection)" includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].  

- "Model Diagnosis" includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].  

- "Model Interpretation" includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].  

- "Classification and Prediction" includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].  

- "Time Series Analysis" includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].  

- "Text Data Analysis" includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].  

- "Network Data Analysis" includes: ["Community Detection", "Link Prediction"].  

- "Experimental Design" includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].  

- "Causal Inference" includes: ["Observational Data", "Experimental Data"].  

- "Critical Evaluation of Statistical Results" includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].  

2. Relevant variables and their roles (variables)  
Key requirements:  
    1. Variables specifically refer to the data objects collected for the research objective in the question and their statistical measures (e.g., sample size, mean, standard deviation), excluding model parameters, statistics related to specific statistical models/distributions (e.g., z-score, p-value), and statistics related to specific statistical methods (e.g., t-value, F-value).  
    2. Variable objects can be raw data columns, grouped statistics, contingency tables, sample sizes, success counts, or time variables.  
    3. In particular, if the problem to be solved in the question is of the "Mathematical Calculation" type, please treat the numerical objects such as probabilities and sample sizes actually used in the answer as variable objects for extraction.
    4. If no explicit data table is provided or `data` is empty, but symbolic variables, statistics, or logical judgment objects (e.g., `X`, `Y`, `r`, an event, a statistic) have already appeared, variables must still be extracted accordingly.  
    5. When the original data has a grouping structure, prioritize splitting the data into multiple variables according to the grouping. If each sample belongs to different groups based on different grouping methods, after splitting, additionally note in the description of these variables that they share the same samples with certain other variables but represent different groupings/features.  
    6. If the problem provides aggregated measures for multiple variables (e.g., mean, standard deviation, sample size), create a separate variable object for each variable and write these aggregated measures into the `value` field of each variable object in JSON format.  
    7. If the information is insufficient to support any variables, directly output an empty JSON: `{}`.  
    8. The output must be strictly JSON, with the top-level keys being variable IDs, and no additional text should be output.  

Field specifications:  
- Top-level key: "Variable name (extracted from the problem or an appropriately assigned variable name)".  
- `id`: Variable identifier, must exactly match the top-level key.  
- `value`: The complete value of the current variable. If it is a column from a table, an array can be used; if it is aggregated measures (including statistics, sample size, etc.), a JSON value can be used (keys are the names of the aggregated measures, and values are the corresponding values); if neither of the above forms is suitable for representation, copy and paste the original recorded form of the variable from the problem (e.g., a table recorded in TeX syntax). When there are multiple numerical values in `value`, ensure their order matches the original order in the problem.  
- `class`: Can only be one of `numerical`, `categorical`, or `others`. (Numerical type is denoted as "numerical", categorical type as "categorical", and those not belonging to the above categories as "others".)  
- `role`: Can only be one of `X`, `Y`, `XY`, or `NR`.  
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  
> Special cases for `role`:  
    1. For "Trends Over Time" problems under "Data Visualization," the variable representing the time concept must be assigned as `X`, and the variable changing over time as `Y` (even if the time variable does not appear in the variable set). For example, when studying the sales trend over different time points, the time variable is `X`, and the sales variable is `Y`.  
    2. If a variable serves both as an independent variable and is used to construct the dependent variable, its role is `X`.  
    3. If a variable serves both as a dependent variable and is used to construct the independent variable, its role is `Y`.  
- `description`: A brief description of the variable object.  

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. 

Here are two instances:

First instance:

Input:

{
  "background": "A manufacturer claims that the average lifespan of their light bulbs is 1500 hours. A consumer protection agency takes a random sample of 8 bulbs to test this claim. The measured lifespans (in hours) are recorded.",
  "data": "\\begin{tabular}{c} Lifespan (hours) \\\\ \\hline 1453 \\\\ 1489 \\\\ 1512 \\\\ 1478 \\\\ 1496 \\\\ 1521 \\\\ 1465 \\\\ 1502 \\end{tabular}",
  "question": "Is there sufficient evidence at the 5% significance level to conclude that the true mean lifespan differs from 1500 hours?"
}

Output:

{
  "category": "Mean Test",
  "variables": {
    "lifespan_sample": {
      "id": "lifespan_sample",
      "value": [1453, 1489, 1512, 1478, 1496, 1521, 1465, 1502],
      "class": "numerical",
      "role": "NR",
      "description": "Measured lifespans (in hours) of 8 randomly selected light bulbs."
    },
    "mu0": {
      "id": "mu0",
      "value": 1500,
      "class": "numerical",
      "role": "NR",
      "description": "Hypothesized population mean lifespan under the null hypothesis."
    }
  }
}

Second instance:

Input:

{
  "background": "A real estate analyst wants to predict house prices based on living area. Data from 10 recently sold houses are available.",
  "data": "\\begin{tabular}{cc} Area (sq ft) & Price (thousands $) \\\\ \\hline 2100 & 365 \\\\ 1600 & 290 \\\\ 2400 & 410 \\\\ 1800 & 315 \\\\ 2050 & 350 \\\\ 1720 & 298 \\\\ 2250 & 395 \\\\ 1950 & 330 \\\\ 1500 & 270 \\\\ 2300 & 405 \\end{tabular}",
  "question": "What is the predicted price for a house with 2000 square feet?"
}

Output:

{
  "category": "Continuous Value Prediction",
  "variables": {
    "Area": {
      "id": "Area",
      "value": [2100, 1600, 2400, 1800, 2050, 1720, 2250, 1950, 1500, 2300],
      "class": "numerical",
      "role": "X",
      "description": "Living area of the house in square feet, used as the predictor variable."
    },
    "Price": {
      "id": "Price",
      "value": [365, 290, 410, 315, 350, 298, 395, 330, 270, 405],
      "class": "numerical",
      "role": "Y",
      "description": "Sale price of the house in thousands of dollars, the outcome variable to be predicted."
    }
  }
}
'''


Prompt_0_three='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

{
    "background": "Relevant description of the problem context (which may also contain some data)",
    "data": "The data used, presented as a table in LaTeX code",
    "question": "The core problem"
}

The abstracted statistical model includes the following four parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- "Data Preprocessing" includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].  

- "Mathematical Calculation" includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].  

- "Numerical Computation" includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].  

- "Descriptive Statistics" includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].  

- The "Data Distribution Modelling" section includes: ["Model Building", "MLE", "Bayesian"].

- "Data Visualization" includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].  

- "Association Analysis" includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].  

- "Clustering" includes only: ["Clustering"].  

- "Dimensionality Reduction" includes only: ["Dimensionality Reduction"].  

- "Hypothesis Testing and Interval Estimation" includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include corresponding interval estimation methods.)  

- "Model Comparison (Variable Selection)" includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].  

- "Model Diagnosis" includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].  

- "Model Interpretation" includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].  

- "Classification and Prediction" includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].  

- "Time Series Analysis" includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].  

- "Text Data Analysis" includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].  

- "Network Data Analysis" includes: ["Community Detection", "Link Prediction"].  

- "Experimental Design" includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].  

- "Causal Inference" includes: ["Observational Data", "Experimental Data"].  

- "Critical Evaluation of Statistical Results" includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].  

2. Relevant variables and their roles (variables)  
Key requirements:  
    1. Variables specifically refer to the data objects collected for the research objective in the question and their statistical measures (e.g., sample size, mean, standard deviation), excluding model parameters, statistics related to specific statistical models/distributions (e.g., z-score, p-value), and statistics related to specific statistical methods (e.g., t-value, F-value).  
    2. Variable objects can be raw data columns, grouped statistics, contingency tables, sample sizes, success counts, or time variables.  
    3. In particular, if the problem to be solved in the question is of the "Mathematical Calculation" type, please treat the numerical objects such as probabilities and sample sizes actually used in the answer as variable objects for extraction.
    4. If no explicit data table is provided or `data` is empty, but symbolic variables, statistics, or logical judgment objects (e.g., `X`, `Y`, `r`, an event, a statistic) have already appeared, variables must still be extracted accordingly.  
    5. When the original data has a grouping structure, prioritize splitting the data into multiple variables according to the grouping. If each sample belongs to different groups based on different grouping methods, after splitting, additionally note in the description of these variables that they share the same samples with certain other variables but represent different groupings/features.  
    6. If the problem provides aggregated measures for multiple variables (e.g., mean, standard deviation, sample size), create a separate variable object for each variable and write these aggregated measures into the `value` field of each variable object in JSON format.  
    7. If the information is insufficient to support any variables, directly output an empty JSON: `{}`.  
    8. The output must be strictly JSON, with the top-level keys being variable IDs, and no additional text should be output.  

Field specifications:  
- Top-level key: "Variable name (extracted from the problem or an appropriately assigned variable name)".  
- `id`: Variable identifier, must exactly match the top-level key.  
- `value`: The complete value of the current variable. If it is a column from a table, an array can be used; if it is aggregated measures (including statistics, sample size, etc.), a JSON value can be used (keys are the names of the aggregated measures, and values are the corresponding values); if neither of the above forms is suitable for representation, copy and paste the original recorded form of the variable from the problem (e.g., a table recorded in TeX syntax). When there are multiple numerical values in `value`, ensure their order matches the original order in the problem.  
- `class`: Can only be one of `numerical`, `categorical`, or `others`. (Numerical type is denoted as "numerical", categorical type as "categorical", and those not belonging to the above categories as "others".)  
- `role`: Can only be one of `X`, `Y`, `XY`, or `NR`.  
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  
> Special cases for `role`:  
    1. For "Trends Over Time" problems under "Data Visualization," the variable representing the time concept must be assigned as `X`, and the variable changing over time as `Y` (even if the time variable does not appear in the variable set). For example, when studying the sales trend over different time points, the time variable is `X`, and the sales variable is `Y`.  
    2. If a variable serves both as an independent variable and is used to construct the dependent variable, its role is `X`.  
    3. If a variable serves both as a dependent variable and is used to construct the independent variable, its role is `Y`.  
- `description`: A brief description of the variable object.  

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. 

Here are three instances:

First instance:

Input:

{
  "background": "A manufacturer claims that the average lifespan of their light bulbs is 1500 hours. A consumer protection agency takes a random sample of 8 bulbs to test this claim. The measured lifespans (in hours) are recorded.",
  "data": "\\begin{tabular}{c} Lifespan (hours) \\\\ \\hline 1453 \\\\ 1489 \\\\ 1512 \\\\ 1478 \\\\ 1496 \\\\ 1521 \\\\ 1465 \\\\ 1502 \\end{tabular}",
  "question": "Is there sufficient evidence at the 5% significance level to conclude that the true mean lifespan differs from 1500 hours?"
}

Output:

{
  "category": "Mean Test",
  "variables": {
    "lifespan_sample": {
      "id": "lifespan_sample",
      "value": [1453, 1489, 1512, 1478, 1496, 1521, 1465, 1502],
      "class": "numerical",
      "role": "NR",
      "description": "Measured lifespans (in hours) of 8 randomly selected light bulbs."
    },
    "mu0": {
      "id": "mu0",
      "value": 1500,
      "class": "numerical",
      "role": "NR",
      "description": "Hypothesized population mean lifespan under the null hypothesis."
    }
  }
}

Second instance:

Input:

{
  "background": "A real estate analyst wants to predict house prices based on living area. Data from 10 recently sold houses are available.",
  "data": "\\begin{tabular}{cc} Area (sq ft) & Price (thousands $) \\\\ \\hline 2100 & 365 \\\\ 1600 & 290 \\\\ 2400 & 410 \\\\ 1800 & 315 \\\\ 2050 & 350 \\\\ 1720 & 298 \\\\ 2250 & 395 \\\\ 1950 & 330 \\\\ 1500 & 270 \\\\ 2300 & 405 \\end{tabular}",
  "question": "What is the predicted price for a house with 2000 square feet?"
}

Output:

{
  "category": "Continuous Value Prediction",
  "variables": {
    "Area": {
      "id": "Area",
      "value": [2100, 1600, 2400, 1800, 2050, 1720, 2250, 1950, 1500, 2300],
      "class": "numerical",
      "role": "X",
      "description": "Living area of the house in square feet, used as the predictor variable."
    },
    "Price": {
      "id": "Price",
      "value": [365, 290, 410, 315, 350, 298, 395, 330, 270, 405],
      "class": "numerical",
      "role": "Y",
      "description": "Sale price of the house in thousands of dollars, the outcome variable to be predicted."
    }
  }
}

Third instance

Input: 

{
  "background": "An ecologist studies the relationship between the depth of a lake and the concentration of dissolved oxygen. Measurements were taken at 12 different locations.",
  "data": "\\begin{tabular}{cc} Depth (m) & Oxygen (mg/L) \\\\ \\hline 2.0 & 9.2 \\\\ 4.5 & 8.1 \\\\ 6.0 & 7.4 \\\\ 8.2 & 6.3 \\\\ 10.5 & 5.5 \\\\ 12.0 & 5.0 \\\\ 14.3 & 4.2 \\\\ 16.1 & 3.8 \\\\ 18.0 & 3.3 \\\\ 20.5 & 2.9 \\\\ 22.4 & 2.5 \\\\ 25.0 & 2.1 \\end{tabular}",
  "question": "Create an appropriate graph to explore the association between water depth and dissolved oxygen concentration."
}

Output:

{
  "category": "Relationship Between Continuous Variables",
  "variables": {
    "Depth": {
      "id": "Depth",
      "value": [2.0, 4.5, 6.0, 8.2, 10.5, 12.0, 14.3, 16.1, 18.0, 20.5, 22.4, 25.0],
      "class": "numerical",
      "role": "XY",
      "description": "Water depth in meters at each sampling location."
    },
    "Oxygen": {
      "id": "Oxygen",
      "value": [9.2, 8.1, 7.4, 6.3, 5.5, 5.0, 4.2, 3.8, 3.3, 2.9, 2.5, 2.1],
      "class": "numerical",
      "role": "XY",
      "description": "Dissolved oxygen concentration in mg/L measured at the corresponding depth."
    }
  }
}
'''

Prompt_b_one='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

The input format for user's inquiry questions is:
{
"background": " Relevant description of the problem context",
"data_description_1": "The specific details of the dataset provided by",
"data_description_2": "(If applicable) The description of the data formatting, including data types, data shapes, variable names, and basic statistical information fields",
"question": " The core problem" 
}

The abstracted statistical model includes the following four parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- "Data Preprocessing" includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].  

- "Mathematical Calculation" includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].  

- "Numerical Computation" includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].  

- "Descriptive Statistics" includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].  

- The "Data Distribution Modelling" section includes: ["Model Building", "MLE", "Bayesian"].

- "Data Visualization" includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].  

- "Association Analysis" includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].  

- "Clustering" includes only: ["Clustering"].  

- "Dimensionality Reduction" includes only: ["Dimensionality Reduction"].  

- "Hypothesis Testing and Interval Estimation" includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include corresponding interval estimation methods.)  

- "Model Comparison (Variable Selection)" includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].  

- "Model Diagnosis" includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].  

- "Model Interpretation" includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].  

- "Classification and Prediction" includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].  

- "Time Series Analysis" includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].  

- "Text Data Analysis" includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].  

- "Network Data Analysis" includes: ["Community Detection", "Link Prediction"].  

- "Experimental Design" includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].  

- "Causal Inference" includes: ["Observational Data", "Experimental Data"].  

- "Critical Evaluation of Statistical Results" includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].  

2. Relevant Variables
- These are the original variable names involved in the statistical model. If the INPUT contains a field named "data_description_2" with data formatting description, the variable name must be consistent with the variable name provided in the data formatting description. Otherwise, the returned result will be an empty dictionary {}.
- The format of the data variable is {Dataset Name (suffix ".pkl" of the file name, the first key from the "data_description_2" field): [Variable Name 1, Variable Name 2, ...]
- Variable selection follows a streamlined principle. Some variables that are not necessary in the analysis process (such as "Sample Number" etc.) should be excluded. 

3. Variable roles refer to the functions of each variable in the statistical model, and they can be classified into the following four categories: 
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  

Special Cases: 
- For "time variation trend" type questions in "data visualization", the variable representing the concept of time should be set as the independent variable, and the variable that changes over time should be set as the dependent variable (even if a time variable does not appear in the variable set). For example, when studying the trend of sales volume at different time points, the time variable is set as the independent variable and the sales volume variable is set as the dependent variable.
- If a variable serves as both an independent variable and is used to construct the dependent variable, its role is set as independent. 
- If a variable serves as both a dependent variable and is used to construct an independent variable, its role is set as dependent. 
Format: {Dataset Name (file name with .pkl extension, derived from the first key of the "data_description_2" field)}: [Variable Name 1 Role Name, Variable Name 2 Role Name, ...], The roles of the variables can only be one of "X", "Y", "XY", or "NR", and must be in the same order as the corresponding variable names in the "variable" field. 
Note: If the "variable" field is an empty dictionary {}, then the "role" field must also be an empty dictionary {}.

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. A complete output example is as follows:  

{
      "category": "Relationship Between Discrete and Continuous Variables",
      "variable": {
        "HotPotForMac.pkl": [
          "people",
          "quarterly sales volume"
        ]
      },
      "role": {
        "HotPotForMac.pkl": [
          "X",
          "Y"
        ]
      }
    }

Here is an instance:

input:
{"background": "A real estate company wants to predict house sale prices based on property characteristics. They have collected recent transaction records for model building.",
"data_description_1": "The dataset consists of 1000 house sale records. Each record contains attributes such as living area (square feet), number of bedrooms, and the final sale price.",
    "data_description_2": {
      "house_sales.pkl": {
        "data_type": "DataFrame",
        "variables": ["sqft_living", "bedrooms", "price"],
        "head_5": {
          "sqft_living": {"0": 1180, "1": 2570, "2": 770, "3": 1960, "4": 1680},
          "bedrooms": {"0": 3, "1": 4, "2": 2, "3": 3, "4": 3},
          "price": {"0": 221900, "1": 538000, "2": 180000, "3": 604000, "4": 510000}
        },
        "basic_info": {
          "sqft_living": {
            "count": 1000, "mean": 2079.9, "std": 918.1, "min": 290,
            "25%": 1427, "50%": 1910, "75%": 2550, "max": 13540, "missing": 0, "type": "int64"
          }
        }
      }
    },
    "question": "Build a model to predict house price using living area."}

output:
{
      "category": "Continuous Value Prediction",
      "variable": {
        "house_sales.pkl": ["sqft_living", "price"]
      },
      "role": {
        "house_sales.pkl": ["X", "Y"]
      }
    }
'''

Prompt_b_two='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

The input format for user's inquiry questions is:
{
"background": " Relevant description of the problem context",
"data_description_1": "The specific details of the dataset provided by",
"data_description_2": "(If applicable) The description of the data formatting, including data types, data shapes, variable names, and basic statistical information fields",
"question": " The core problem" 
}

The abstracted statistical model includes the following four parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- "Data Preprocessing" includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].  

- "Mathematical Calculation" includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].  

- "Numerical Computation" includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].  

- "Descriptive Statistics" includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].  

- The "Data Distribution Modelling" section includes: ["Model Building", "MLE", "Bayesian"].

- "Data Visualization" includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].  

- "Association Analysis" includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].  

- "Clustering" includes only: ["Clustering"].  

- "Dimensionality Reduction" includes only: ["Dimensionality Reduction"].  

- "Hypothesis Testing and Interval Estimation" includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include corresponding interval estimation methods.)  

- "Model Comparison (Variable Selection)" includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].  

- "Model Diagnosis" includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].  

- "Model Interpretation" includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].  

- "Classification and Prediction" includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].  

- "Time Series Analysis" includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].  

- "Text Data Analysis" includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].  

- "Network Data Analysis" includes: ["Community Detection", "Link Prediction"].  

- "Experimental Design" includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].  

- "Causal Inference" includes: ["Observational Data", "Experimental Data"].  

- "Critical Evaluation of Statistical Results" includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].  

2. Relevant Variables
- These are the original variable names involved in the statistical model. If the INPUT contains a field named "data_description_2" with data formatting description, the variable name must be consistent with the variable name provided in the data formatting description. Otherwise, the returned result will be an empty dictionary {}.
- The format of the data variable is {Dataset Name (suffix ".pkl" of the file name, the first key from the "data_description_2" field): [Variable Name 1, Variable Name 2, ...]
- Variable selection follows a streamlined principle. Some variables that are not necessary in the analysis process (such as "Sample Number" etc.) should be excluded. 

3. Variable roles refer to the functions of each variable in the statistical model, and they can be classified into the following four categories: 
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  

Special Cases: 
- For "time variation trend" type questions in "data visualization", the variable representing the concept of time should be set as the independent variable, and the variable that changes over time should be set as the dependent variable (even if a time variable does not appear in the variable set). For example, when studying the trend of sales volume at different time points, the time variable is set as the independent variable and the sales volume variable is set as the dependent variable.
- If a variable serves as both an independent variable and is used to construct the dependent variable, its role is set as independent. 
- If a variable serves as both a dependent variable and is used to construct an independent variable, its role is set as dependent. 
Format: {Dataset Name (file name with .pkl extension, derived from the first key of the "data_description_2" field)}: [Variable Name 1 Role Name, Variable Name 2 Role Name, ...], The roles of the variables can only be one of "X", "Y", "XY", or "NR", and must be in the same order as the corresponding variable names in the "variable" field. 
Note: If the "variable" field is an empty dictionary {}, then the "role" field must also be an empty dictionary {}.

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. A complete output example is as follows:  

{
      "category": "Relationship Between Discrete and Continuous Variables",
      "variable": {
        "HotPotForMac.pkl": [
          "people",
          "quarterly sales volume"
        ]
      },
      "role": {
        "HotPotForMac.pkl": [
          "X",
          "Y"
        ]
      }
    }

Here are two instances:

First instance:

input:
{"background": "A real estate company wants to predict house sale prices based on property characteristics. They have collected recent transaction records for model building.",
"data_description_1": "The dataset consists of 1000 house sale records. Each record contains attributes such as living area (square feet), number of bedrooms, and the final sale price.",
    "data_description_2": {
      "house_sales.pkl": {
        "data_type": "DataFrame",
        "variables": ["sqft_living", "bedrooms", "price"],
        "head_5": {
          "sqft_living": {"0": 1180, "1": 2570, "2": 770, "3": 1960, "4": 1680},
          "bedrooms": {"0": 3, "1": 4, "2": 2, "3": 3, "4": 3},
          "price": {"0": 221900, "1": 538000, "2": 180000, "3": 604000, "4": 510000}
        },
        "basic_info": {
          "sqft_living": {
            "count": 1000, "mean": 2079.9, "std": 918.1, "min": 290,
            "25%": 1427, "50%": 1910, "75%": 2550, "max": 13540, "missing": 0, "type": "int64"
          }
        }
      }
    },
    "question": "Build a model to predict house price using living area."}

output:
{
      "category": "Continuous Value Prediction",
      "variable": {
        "house_sales.pkl": ["sqft_living", "price"]
      },
      "role": {
        "house_sales.pkl": ["X", "Y"]
      }
    }

Second instance:

Input:

 {
      "background": "A bioinformatician is analyzing a gene expression dataset from cancer patients. The data contains expression levels of thousands of genes, and the goal is to reduce the dimensionality to visualize sample groupings and identify underlying patterns.",
      "data_description_1": "The dataset consists of 150 patient samples, each measured for 5000 genes. Only a subset of the most variable genes is included for analysis.",
      "data_description_2": {
        "gene_expression.pkl": {
          "data_type": "DataFrame",
          "variables": ["sample_id", "gene_TP53", "gene_BRCA1", "gene_EGFR", "gene_MYC", "gene_KRAS"],
          "head_5": {
            "sample_id": {"0": "S001", "1": "S002", "2": "S003", "3": "S004", "4": "S005"},
            "gene_TP53": {"0": 2.34, "1": 1.87, "2": 3.12, "3": 2.01, "4": 2.55},
            "gene_BRCA1": {"0": 1.20, "1": 0.98, "2": 1.45, "3": 1.33, "4": 1.08},
            "gene_EGFR": {"0": 3.56, "1": 4.01, "2": 3.22, "3": 3.89, "4": 3.67},
            "gene_MYC": {"0": 5.10, "1": 4.78, "2": 5.34, "3": 4.92, "4": 5.05},
            "gene_KRAS": {"0": 1.88, "1": 2.11, "2": 1.95, "3": 2.30, "4": 1.72}
          },
          "basic_info": {
            "gene_TP53": {
              "count": 150, "mean": 2.45, "std": 0.87, "min": 0.95,
              "25%": 1.82, "50%": 2.38, "75%": 3.01, "max": 4.89, "missing": 0, "type": "float64"
            }
          }
        }
      },
      "question": "How can we reduce the dimensionality of the selected gene expression data to visualize potential patient clusters in a two-dimensional space?"
    }

Output:

{
      "category": "Dimensionality Reduction",
      "variable": {
        "gene_expression.pkl": ["gene_TP53", "gene_BRCA1", "gene_EGFR", "gene_MYC", "gene_KRAS"]
      },
      "role": {
        "gene_expression.pkl": ["NR", "NR", "NR", "NR", "NR"]
      }
    }
'''

Prompt_b_three='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

The input format for user's inquiry questions is:
{
"background": " Relevant description of the problem context",
"data_description_1": "The specific details of the dataset provided by",
"data_description_2": "(If applicable) The description of the data formatting, including data types, data shapes, variable names, and basic statistical information fields",
"question": " The core problem" 
}

The abstracted statistical model includes the following four parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- "Data Preprocessing" includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].  

- "Mathematical Calculation" includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].  

- "Numerical Computation" includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].  

- "Descriptive Statistics" includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].  

- The "Data Distribution Modelling" section includes: ["Model Building", "MLE", "Bayesian"].

- "Data Visualization" includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].  

- "Association Analysis" includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].  

- "Clustering" includes only: ["Clustering"].  

- "Dimensionality Reduction" includes only: ["Dimensionality Reduction"].  

- "Hypothesis Testing and Interval Estimation" includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include corresponding interval estimation methods.)  

- "Model Comparison (Variable Selection)" includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].  

- "Model Diagnosis" includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].  

- "Model Interpretation" includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].  

- "Classification and Prediction" includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].  

- "Time Series Analysis" includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].  

- "Text Data Analysis" includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].  

- "Network Data Analysis" includes: ["Community Detection", "Link Prediction"].  

- "Experimental Design" includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].  

- "Causal Inference" includes: ["Observational Data", "Experimental Data"].  

- "Critical Evaluation of Statistical Results" includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].  

2. Relevant Variables
- These are the original variable names involved in the statistical model. If the INPUT contains a field named "data_description_2" with data formatting description, the variable name must be consistent with the variable name provided in the data formatting description. Otherwise, the returned result will be an empty dictionary {}.
- The format of the data variable is {Dataset Name (suffix ".pkl" of the file name, the first key from the "data_description_2" field): [Variable Name 1, Variable Name 2, ...]
- Variable selection follows a streamlined principle. Some variables that are not necessary in the analysis process (such as "Sample Number" etc.) should be excluded. 

3. Variable roles refer to the functions of each variable in the statistical model, and they can be classified into the following four categories: 
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  

Special Cases: 
- For "time variation trend" type questions in "data visualization", the variable representing the concept of time should be set as the independent variable, and the variable that changes over time should be set as the dependent variable (even if a time variable does not appear in the variable set). For example, when studying the trend of sales volume at different time points, the time variable is set as the independent variable and the sales volume variable is set as the dependent variable.
- If a variable serves as both an independent variable and is used to construct the dependent variable, its role is set as independent. 
- If a variable serves as both a dependent variable and is used to construct an independent variable, its role is set as dependent. 
Format: {Dataset Name (file name with .pkl extension, derived from the first key of the "data_description_2" field)}: [Variable Name 1 Role Name, Variable Name 2 Role Name, ...], The roles of the variables can only be one of "X", "Y", "XY", or "NR", and must be in the same order as the corresponding variable names in the "variable" field. 
Note: If the "variable" field is an empty dictionary {}, then the "role" field must also be an empty dictionary {}.

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. A complete output example is as follows:  

{
      "category": "Relationship Between Discrete and Continuous Variables",
      "variable": {
        "HotPotForMac.pkl": [
          "people",
          "quarterly sales volume"
        ]
      },
      "role": {
        "HotPotForMac.pkl": [
          "X",
          "Y"
        ]
      }
    }

Here are three instances:

First instance:

input:
{"background": "A real estate company wants to predict house sale prices based on property characteristics. They have collected recent transaction records for model building.",
"data_description_1": "The dataset consists of 1000 house sale records. Each record contains attributes such as living area (square feet), number of bedrooms, and the final sale price.",
    "data_description_2": {
      "house_sales.pkl": {
        "data_type": "DataFrame",
        "variables": ["sqft_living", "bedrooms", "price"],
        "head_5": {
          "sqft_living": {"0": 1180, "1": 2570, "2": 770, "3": 1960, "4": 1680},
          "bedrooms": {"0": 3, "1": 4, "2": 2, "3": 3, "4": 3},
          "price": {"0": 221900, "1": 538000, "2": 180000, "3": 604000, "4": 510000}
        },
        "basic_info": {
          "sqft_living": {
            "count": 1000, "mean": 2079.9, "std": 918.1, "min": 290,
            "25%": 1427, "50%": 1910, "75%": 2550, "max": 13540, "missing": 0, "type": "int64"
          }
        }
      }
    },
    "question": "Build a model to predict house price using living area."}

output:
{
      "category": "Continuous Value Prediction",
      "variable": {
        "house_sales.pkl": ["sqft_living", "price"]
      },
      "role": {
        "house_sales.pkl": ["X", "Y"]
      }
    }

Second instance:

Input:

 {
      "background": "A bioinformatician is analyzing a gene expression dataset from cancer patients. The data contains expression levels of thousands of genes, and the goal is to reduce the dimensionality to visualize sample groupings and identify underlying patterns.",
      "data_description_1": "The dataset consists of 150 patient samples, each measured for 5000 genes. Only a subset of the most variable genes is included for analysis.",
      "data_description_2": {
        "gene_expression.pkl": {
          "data_type": "DataFrame",
          "variables": ["sample_id", "gene_TP53", "gene_BRCA1", "gene_EGFR", "gene_MYC", "gene_KRAS"],
          "head_5": {
            "sample_id": {"0": "S001", "1": "S002", "2": "S003", "3": "S004", "4": "S005"},
            "gene_TP53": {"0": 2.34, "1": 1.87, "2": 3.12, "3": 2.01, "4": 2.55},
            "gene_BRCA1": {"0": 1.20, "1": 0.98, "2": 1.45, "3": 1.33, "4": 1.08},
            "gene_EGFR": {"0": 3.56, "1": 4.01, "2": 3.22, "3": 3.89, "4": 3.67},
            "gene_MYC": {"0": 5.10, "1": 4.78, "2": 5.34, "3": 4.92, "4": 5.05},
            "gene_KRAS": {"0": 1.88, "1": 2.11, "2": 1.95, "3": 2.30, "4": 1.72}
          },
          "basic_info": {
            "gene_TP53": {
              "count": 150, "mean": 2.45, "std": 0.87, "min": 0.95,
              "25%": 1.82, "50%": 2.38, "75%": 3.01, "max": 4.89, "missing": 0, "type": "float64"
            }
          }
        }
      },
      "question": "How can we reduce the dimensionality of the selected gene expression data to visualize potential patient clusters in a two-dimensional space?"
    }

Output:

{
      "category": "Dimensionality Reduction",
      "variable": {
        "gene_expression.pkl": ["gene_TP53", "gene_BRCA1", "gene_EGFR", "gene_MYC", "gene_KRAS"]
      },
      "role": {
        "gene_expression.pkl": ["NR", "NR", "NR", "NR", "NR"]
      }
    }

Third instance:

Input:

{
      "background": "The human resources department of a large corporation is conducting an internal review of compensation. They want to understand the overall shape and spread of current employee salaries before making adjustments to the pay structure.",
      "data_description_1": "The dataset contains records for 500 employees, with fields for a unique employee identifier, their current annual salary, and their department.",
      "data_description_2": {
        "employee_salary.pkl": {
          "data_type": "DataFrame",
          "variables": ["employee_id", "salary", "department"],
          "head_5": {
            "employee_id": {"0": 1001, "1": 1002, "2": 1003, "3": 1004, "4": 1005},
            "salary": {"0": 52000, "1": 78500, "2": 43000, "3": 95000, "4": 61500},
            "department": {"0": "Sales", "1": "Engineering", "2": "Marketing", "3": "Engineering", "4": "Sales"}
          },
          "basic_info": {
            "salary": {
              "count": 500, "mean": 68750, "std": 18200, "min": 32000,
              "25%": 54000, "50%": 67200, "75%": 81500, "max": 135000, "missing": 0, "type": "int64"
            }
          }
        }
      },
      "question": "What is the distribution of employee salaries, and how can we visualize its shape and dispersion?"
    }

Output:

{
      "category": "Distribution of Continuous Variables",
      "variable": {
        "employee_salary.pkl": ["salary"]
      },
      "role": {
        "employee_salary.pkl": ["NR"]
      }
    }
'''



Prompt_b_ca='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

The input format for user's inquiry questions is:
{
"background": " Relevant description of the problem context",
"data_description_1": "The specific details of the dataset provided by",
"data_description_2": "(If applicable) The description of the data formatting, including data types, data shapes, variable names, and basic statistical information fields",
"question": " The core problem" 
}

The abstracted statistical model includes the following three parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- **"Data Preprocessing"** includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].
    - *“Missing Value Handling”* refers to “the problem of identifying, deleting, or imputing missing data during the data preprocessing stage, with the goal of handling missing observations in samples or variables before subsequent analysis. Includes mean/median imputation, multiple imputation, missing indicator variables, etc.”
    - *“Outlier Handling”* refers to “the problem of identifying, correcting, truncating, or deleting abnormal observations during the data preprocessing stage. Includes boxplot rules, z-score, etc.”
    - *“Standardization”* refers to “the problem of scaling or shifting variables to make them comparable across different units or magnitudes. Includes z-score standardization, min-max normalization, unit variance scaling, etc.”
    - *“Binning”* refers to “the problem of dividing a continuous variable into several intervals and converting them into interval categories. Includes equal-width binning, equal-frequency binning, business-rule-based segmentation, etc.”
    - *“Transformation”* refers to “the problem of changing the representation of a variable through functions or unit conversions to improve distribution shape, interpretability, or modelability. Includes log transformation, square-root transformation, Box-Cox transformation, Celsius/Fahrenheit conversion, unit unification, etc.”

- **"Mathematical Calculation"** includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].
    - *“Probability Space Related (e.g., number of states)”* refers to “problems that calculate the size of the sample space, number of possible states, or number of possible configurations based on combinatorial mathematics or probability space structure. Includes permutations and combinations, number of paths, number of sampling outcomes, number of Markov chain states, etc.”
    - *“Event Probability and Independence”* refers to “problems that calculate event probabilities based on probability rules, distributional assumptions, or contingency structures, and determine whether events are independent. Includes conditional probability, total probability, Bayes’ theorem, independence testing, etc.”
    - *“Expectation”* refers to “problems that calculate the mathematical expectation, mean payoff, or long-run average outcome of a random variable or stochastic process. Includes expectation for discrete/continuous distributions, expected loss, expected number of occurrences, etc. Calculations of quantities defined based on expectation, such as variance, are also included.”
    - *“Minimum Sample Size Required to Achieve a Specified Probability”* refers to “problems that back-calculate the required minimum sample size given a target success probability, confidence requirement, estimation precision, or the probability of at least one occurrence. Includes ‘sample size needed to detect an event at least once’, ‘number of trials needed to achieve 95% coverage probability’, etc.”
    - *“Distribution Derivation”* refers to “problems that derive the probability distribution of a random variable based on probability rules, distribution definitions, or model structures. Approximations based on the Central Limit Theorem are also included.”
    - *“Other”* refers to “problems that are difficult to consistently classify into the above categories but still involve ‘numerical calculations based on probability rules or distribution definitions’. Includes calculation of special probability quantities, etc.”

- **"Numerical Computation"** includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].
    - *“Obtaining Model Parameter Estimates”* refers to “problems that obtain parameter estimates through analytical or numerical methods, given a model, sample, and estimation criterion. Includes finding regression coefficients, distribution parameters, extreme points, EM iteration results, etc.”
    - *“Sampling from a Specified Distribution”* refers to “problems that generate random samples according to a given probability distribution or model. Includes Monte Carlo sampling, Bootstrap resampling, Normal/Poisson/posterior distribution sampling, etc.”

- **"Descriptive Statistics"** includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].
    - *“Measures of Central Tendency”* refers to “problems that summarize the center of a data distribution with a single value. Includes mean, median, mode, geometric mean, etc.”
    - *“Measures of Dispersion”* refers to “problems that summarize the spread of data with one or a few indicators. Includes variance, standard deviation, coefficient of variation, MAD, IQR, etc.”
    - *“Measures of Distribution Range”* refers to “problems that describe the lower/upper bounds or coverage intervals of data values. Includes range, minimum/maximum, limits, reference intervals, etc.”
    - *“Measures of Frequency and Proportion”* refers to “problems that describe the frequency, proportion, or composition of specific values or categories in data. Includes frequency, proportion, measures of effect (e.g., relative risk, odds ratio), etc.”
    - *“Quantiles/Percentiles”* refers to “problems that calculate or interpret the relative position of data after sorting. Includes quartiles, percentiles, percentile of the median, threshold quantiles, etc.”
    - *“Network Graph Indicators”* refers to “problems that calculate summary indicators for network or graph structures. Includes degree, betweenness centrality, clustering coefficient, network density, average path length, etc.”
    - *“Analysis and Comparison of Statistical Properties”* refers to “problems that analyze and compare the properties, advantages, disadvantages, and applicability of different statistics.”
    - *“Other (e.g., reliability)”* refers to “statistics that aim to ‘summarize data characteristics’ but do not belong to the above categories. Includes reliability, internal consistency (e.g., Cronbach’s alpha), etc.”

- **"Data Distribution Modelling"** includes: ["Model Building", "MLE", "Bayesian"].
    - *“Model Building”* refers to “problems that select an appropriate distribution type or probability model for data based on the scenario and assumptions, and optionally write out its expression.”
    - *“MLE”* refers to “problems that assume data come from a parameterized distribution and estimate parameters by maximizing the likelihood function. Includes fitting Normal, Poisson, Exponential, Weibull distributions, etc.”
    - *“Bayesian”* refers to “problems that construct a posterior distribution based on prior distribution and observed data to make inferences about parameters. Includes Bayesian parameter estimation, posterior intervals, Bayesian hierarchical models, etc.”

- **"Data Visualization"** includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].
    - *“Distribution of Discrete Variables”* refers to “problems that display the theoretical/sampling distribution of a single categorical variable (e.g., frequencies, proportions, or composition of each category). Forms include bar charts, pie charts, Pareto charts, etc.”
    - *“Distribution of Continuous Variables”* refers to “problems that display the theoretical/sampling distribution of a single continuous variable. Forms include histograms, density plots, boxplots, violin plots, ECDF plots, etc.”
    - *“Relationship Between Discrete and Continuous Variables”* refers to “problems that display differences in distribution or central tendency of a continuous variable across levels of a categorical variable. Forms include grouped boxplots, grouped violin plots, grouped density plots, error bar charts, etc.”
    - *“Relationship Between Continuous Variables”* refers to “problems that display the association, trend, or functional relationship between two continuous variables. Forms include scatter plots, scatter plots with fitted lines, bubble charts, etc.”
    - *“Relationship Between Discrete Variables”* refers to “problems that display the joint distribution or compositional differences between two categorical variables. Forms include grouped bar charts, stacked bar charts, mosaic plots, spine plots, etc.”
    - *“Comprehensive Comparison of Multiple Variables”* refers to “problems that display the overall structure, relative differences, or patterns of three or more variables or multiple indicators. Forms include radar charts, parallel coordinate plots, heatmaps, correlation matrix plots, etc.”
    - *“Trends Over Time”* refers to “problems that display the trajectory or trend of one or more indicators over time. Forms include line charts, time series line charts, area charts, grouped time trend plots, etc.”
    - *“Spatial and Geographic Visualization”* refers to “problems that display the distribution pattern of data across geographic space or regions. Forms include choropleth maps, heat maps, point maps, spatial scatter plots, etc.”
    - *“Stem-and-Leaf Plot”* refers to “problems that display the distribution of a single variable along with the original numerical structure using a stem-and-leaf plot. The core is to preserve the original data values while showing the distribution shape.”
    - *“Other Statistical Graphics”* refers to “problems that are difficult to consistently classify into the above categories but still involve statistical graphical representation. Forms include special schematic diagrams or hybrid statistical graphs, etc.”

- **"Association Analysis"** includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].
    - *“Correlation Coefficient (One-dimensional)”* refers to “problems that study the strength of linear or monotonic association between two one-dimensional variables using a specific measure. Includes Pearson, Spearman, Kendall correlation, etc.”
    - *“CCA (Multidimensional)”* refers to “problems that study the linear association structure between two multidimensional variable sets using a statistical model. Includes CCA and its variants.”
    - *“Contingency Table”* refers to “problems that study the joint distribution and association patterns of two or more categorical variables using contingency tables. Includes frequency tables, proportion tables, odds ratio displays, etc.”

- **"Clustering"** includes only: ["Clustering"].
    - *“Clustering”* refers to “problems that automatically group samples based on their similarity without labels. Includes k-means, hierarchical clustering, DBSCAN, spectral clustering, etc.”

- **"Dimensionality Reduction"** includes only: ["Dimensionality Reduction"].
    - *“Dimensionality Reduction”* refers to “problems that compress high-dimensional variables into a lower-dimensional representation while preserving essential information. Includes PCA, factor analysis, t-SNE, UMAP, etc.”

- **"Hypothesis Testing and Interval Estimation"** includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include the corresponding interval estimation methods.)
    - *“Independence Test”* refers to “problems that use statistical tests to determine whether two variables or two types of events are independent in the population. Includes chi-square test of independence, Fisher’s exact test, etc.”
    - *“Mean Test”* refers to “problems that compare the magnitude of one or more population means to a given value or to each other. Includes one-sample, two-sample, and paired t-tests, etc.”
    - *“Variance Test”* refers to “problems that compare the magnitude of one or more population variances to a given value or to each other. Includes one-sample, two-sample variance tests, etc.”
    - *“ANOVA”* refers to “problems that decompose sources of variation between and within groups. Includes one-way, two-way ANOVA, etc.”
    - *“Distribution Test”* refers to “problems that test whether data conform to a specific theoretical distribution (e.g., standard normal). Includes chi-square goodness-of-fit test, Kolmogorov-Smirnov test, Shapiro-Wilk test, etc.”
    - *“Proportion Test”* refers to “problems that compare the magnitude of one or more population proportions to a given value or to each other. Includes one-sample, two-sample proportion tests, etc.” (Note: Also includes tests for derived measures of proportion, such as risk ratios, odds ratios, etc.)
    - *“Likelihood Ratio Test”* refers to “problems that perform hypothesis testing by comparing the likelihoods of nested or restricted/unrestricted models. Emphasizes ‘testing a specific statistical hypothesis’.”
    - *“Sequential Test”* refers to “problems that perform hypothesis testing progressively as data is collected to decide whether to stop an experiment. Includes SPRT, etc.”
    - *“Randomness”* refers to “problems that test whether a sequence, permutation, or data generation mechanism can be considered random. Includes runs test, randomness tests, etc.”
    - *“Regression Model Parameter Test”* refers to “tests concerning parameters of a regression model, such as regression coefficients, variance, etc.”
    - *“Analysis of Test Properties”* refers to “problems that describe the basic characteristics and requirements of hypothesis testing. Includes significance level, power, Type I error, Type II error, etc.” (Note: Prioritize classification based on the test’s purpose; if none fit and the topic relates to test properties, classify here.)

- **"Model Comparison (Variable Selection)"** includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].
    - *“Criterion-Based Comparison (AIC, BIC, etc.)”* refers to “problems that compare the优劣 of multiple candidate models using information criteria, penalized criteria, or similar measures. Includes AIC, BIC, Adjusted R², etc.”
    - *“Cross-Validation”* refers to “problems that evaluate the generalization ability of different models through data partitioning or resampling for model selection. Includes k-fold CV, LOOCV, validation set error comparison, etc.”
    - *“Likelihood Ratio Test”* refers to “problems that use the likelihood ratio as a tool for model selection or variable screening to compare whether adding variables improves a nested model. Focuses on ‘which model to select’.”
    - *“ROC Curve (AUC), Coverage-Capture Rate Curve”* refers to “problems that compare the discriminative ability of multiple models based on classification ranking or screening effectiveness. Includes ROC/AUC, lift, gain, coverage-capture, etc.”
    - *“Identification of Important Variables”* refers to “problems that筛选 the most important or explanatory set of independent variables for a response variable. Includes stepwise regression (forward, backward, stepwise selection), LASSO variable selection, etc.”

- **"Model Diagnosis"** includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].
    - *“Residual Analysis”* refers to “problems that check the reasonableness of a model fit through residual plots, residual distributions, outliers, influential points, etc. Includes diagnosis of linearity, heteroscedasticity, outliers, leverage, etc.”
    - *“Goodness-of-Fit Assessment”* refers to “problems that evaluate the degree to which a specified model fits the data using model fit indicators. Includes R², adjusted R², etc.”

- **"Model Interpretation"** includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].
    - *“Interpretation of Regression Coefficient Significance and Direction”* refers to “problems that, after a model is built, explain whether the influence of an independent variable on the response variable is significant and its direction based on parameter estimation results. Includes interpreting the sign and significance of regression coefficients in linear regression, generalized linear models, or Cox models.”
    - *“Interpretation of Regression Effect Size”* refers to “problems that, after a model is built, quantify the magnitude of a variable’s effect on the response variable based on parameter estimates or marginal effects. Includes interpreting the change in response due to a unit change, marginal effects, elasticity coefficients, etc.”
    - *“Interpretation of Factors Influencing Classification or Occurrence Probability”* refers to “problems that, within binary classification or event occurrence models, explain how variables affect the probability of an event based on model parameters. Includes interpreting odds ratios (OR) in logistic regression, hazard ratios (HR) in survival models, etc.”
    - *“Interpretation of Mechanisms Influencing Ordered Outcomes”* refers to “problems that explain how variables affect the tendency towards different outcome levels in ordered response models. Includes interpreting the effect of variables on the probability of each level in ordered logistic regression, ordered probit models, etc.”
    - *“Interpretation of Variable Importance Ranking”* refers to “problems that, after a model is built, compare the relative importance of variables using standardized coefficients, feature importance, or contribution measures. Includes comparison of standardized regression coefficients, variable importance from random forests, SHAP value interpretation, etc.”
    - *“Interpretation of Group Heterogeneity”* refers to “problems that compare differences in variable effects across different groups or sub-samples. Includes comparing coefficients from models estimated separately by gender, region, or time, interaction term interpretation, etc.”

- **"Classification and Prediction"** includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].
    - *“Continuous Value Prediction”* refers to “problems that predict future or unknown values of a numerical response variable.”
    - *“Categorical Variable Classification”* refers to “problems that predict unordered categorical labels. Includes binary classification and unordered multi-class classification.”
    - *“Multi-class Classification of Ordered Variables”* refers to “problems that predict a multi-category response variable with a natural order.”
    - *“Quantile Prediction”* refers to “problems that predict a specific quantile of the conditional distribution, rather than the mean. Includes median regression, prediction of the 90th percentile loss, etc.”
    - *“Survival Analysis”* refers to “problems that study time-to-event data and censoring, focusing on the survival function, hazard function, or median survival time. Includes KM curves, Nelson-Aalen curves, Cox models, accelerated failure time models, etc.”

- **"Time Series Analysis"** includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].
    - *“Lag Correlation Analysis”* refers to “problems that analyze the autocorrelation structure of a time series. Includes analysis of the Autocorrelation Function (ACF), Partial Autocorrelation Function (PACF), etc.”
    - *“Stationarity Analysis”* refers to “problems that test whether a time series satisfies stationarity conditions. Includes unit root tests (ADF, KPSS, etc.), graphical stationarity analysis, etc.”
    - *“Seasonality Analysis”* refers to “problems that identify, estimate, or explain seasonal repeating patterns in a time series. Includes analysis of monthly, quarterly, day-of-week effects, etc.”
    - *“Deterministic Factor Decomposition”* refers to “problems that decompose a time series into trend, cycle, seasonal, or other deterministic components. Includes trend fitting, cycle identification, classical decomposition, etc.”
    - *“Volatility Analysis”* refers to “problems that focus on modeling the time-varying conditional variance of a time series. Includes ARCH/GARCH analysis.”

- **"Text Data Analysis"** includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].
    - *“Tokenization”* refers to “problems that segment raw text into words, tokens, or basic analysis units. Includes Chinese word segmentation, pre-processing segmentation before stop word removal, etc.”
    - *“Word Frequency Statistics”* refers to “problems that count the frequency and ordering of words, phrases, or tokens. Includes word frequency tables, TF statistics, high-frequency word identification, etc.”
    - *“Topic Modeling”* refers to “problems that automatically extract latent topic structures from large-scale text collections. Includes LDA, CTM, Dynamic Topic Models, etc.”
    - *“Sentiment Analysis”* refers to “problems that determine the emotional polarity, attitudinal tendency, or subjective evaluation expressed in text. Includes positive/negative classification, sentiment intensity scoring, etc.”

- **"Network Data Analysis"** includes: ["Community Detection", "Link Prediction"].
    - *“Community Detection”* refers to “problems that identify groups of nodes that are more densely connected internally and sparsely connected externally in a network. Includes modularity optimization, spectral methods, stochastic block models, etc.”
    - *“Link Prediction”* refers to “problems that predict missing or future edges based on existing network structure or node attributes. Includes friend recommendation, collaboration prediction, co-movement prediction, etc.”

- **"Experimental Design"** includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].
    - *“Experiment (Sampling) Plan Design”* refers to “problems that design an experimental or sampling plan to meet specific research objectives. Includes simple random sampling, stratified sampling, etc.”
    - *“Experiment (Sampling) Plan Evaluation”* refers to “problems that evaluate the performance of an experimental or sampling plan based on aspects like sampling error and representativeness.”

- **"Causal Inference"** includes: ["Observational Data", "Experimental Data"].
    - *“Observational Data”* refers to “problems that identify treatment effects or causal relationships in non-experimental, non-randomized data. Includes propensity score matching, instrumental variables, regression discontinuity design, difference-in-differences, etc.”
    - *“Experimental Data”* refers to “problems that estimate treatment effects under randomized or quasi-experimental conditions. Includes randomized controlled trial (RCT) analysis, A/B testing effect evaluation, randomized block experiment analysis, etc.”

- **"Critical Evaluation of Statistical Results"** includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].
    - *“Identification of Statistical Fallacies and Biases”* refers to “problems that identify and explain common fallacies, biases, or misuses in statistical analysis. Includes selection bias, confounding variables, etc.”
    - *“Evaluation of Reliability of Statistical Results”* refers to “problems that assess the reliability of statistical results based on factors such as sample size, etc.”


2. Relevant Variables
- These are the original variable names involved in the statistical model. If the INPUT contains a field named "data_description_2" with data formatting description, the variable name must be consistent with the variable name provided in the data formatting description. Otherwise, the returned result will be an empty dictionary {}.
- The format of the data variable is {Dataset Name (suffix ".pkl" of the file name, the first key from the "data_description_2" field): [Variable Name 1, Variable Name 2, ...]
- Variable selection follows a streamlined principle. Some variables that are not necessary in the analysis process (such as "Sample Number" etc.) should be excluded. 

3. Variable roles refer to the functions of each variable in the statistical model, and they can be classified into the following four categories: 
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  

Special Cases: 
- For "time variation trend" type questions in "data visualization", the variable representing the concept of time should be set as the independent variable, and the variable that changes over time should be set as the dependent variable (even if a time variable does not appear in the variable set). For example, when studying the trend of sales volume at different time points, the time variable is set as the independent variable and the sales volume variable is set as the dependent variable.
- If a variable serves as both an independent variable and is used to construct the dependent variable, its role is set as independent. 
- If a variable serves as both a dependent variable and is used to construct an independent variable, its role is set as dependent. 
Format: {Dataset Name (file name with .pkl extension, derived from the first key of the "data_description_2" field)}: [Variable Name 1 Role Name, Variable Name 2 Role Name, ...], The roles of the variables can only be one of "X", "Y", "XY", or "NR", and must be in the same order as the corresponding variable names in the "variable" field. 
Note: If the "variable" field is an empty dictionary {}, then the "role" field must also be an empty dictionary {}.

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. A complete output example is as follows:  

{
      "category": "Relationship Between Discrete and Continuous Variables",
      "variable": {
        "HotPotForMac.pkl": [
          "people",
          "quarterly sales volume"
        ]
      },
      "role": {
        "HotPotForMac.pkl": [
          "X",
          "Y"
        ]
      }
    }

'''

Prompt_0_ca='''
You are a professional statistician, and you need to abstract the statistical model from the problem.  
The input format is:

{
    "background": "Relevant description of the problem context (which may also contain some data)",
    "data": "The data used, presented as a table in LaTeX code",
    "question": "The core problem"
}

The abstracted statistical model includes the following four parts:  
1. Category, which is the category of the statistical model used and must strictly come from the following framework (the result should be from the content within []):  

- **"Data Preprocessing"** includes: ["Missing Value Handling", "Outlier Handling", "Standardization", "Binning", "Transformation"].
    - *“Missing Value Handling”* refers to “the problem of identifying, deleting, or imputing missing data during the data preprocessing stage, with the goal of handling missing observations in samples or variables before subsequent analysis. Includes mean/median imputation, multiple imputation, missing indicator variables, etc.”
    - *“Outlier Handling”* refers to “the problem of identifying, correcting, truncating, or deleting abnormal observations during the data preprocessing stage. Includes boxplot rules, z-score, etc.”
    - *“Standardization”* refers to “the problem of scaling or shifting variables to make them comparable across different units or magnitudes. Includes z-score standardization, min-max normalization, unit variance scaling, etc.”
    - *“Binning”* refers to “the problem of dividing a continuous variable into several intervals and converting them into interval categories. Includes equal-width binning, equal-frequency binning, business-rule-based segmentation, etc.”
    - *“Transformation”* refers to “the problem of changing the representation of a variable through functions or unit conversions to improve distribution shape, interpretability, or modelability. Includes log transformation, square-root transformation, Box-Cox transformation, Celsius/Fahrenheit conversion, unit unification, etc.”

- **"Mathematical Calculation"** includes: ["Probability Space Related (e.g., number of states)", "Event Probability and Independence", "Expectation", "Minimum Sample Size Required to Achieve a Specified Probability", "Distribution Derivation", "Other"].
    - *“Probability Space Related (e.g., number of states)”* refers to “problems that calculate the size of the sample space, number of possible states, or number of possible configurations based on combinatorial mathematics or probability space structure. Includes permutations and combinations, number of paths, number of sampling outcomes, number of Markov chain states, etc.”
    - *“Event Probability and Independence”* refers to “problems that calculate event probabilities based on probability rules, distributional assumptions, or contingency structures, and determine whether events are independent. Includes conditional probability, total probability, Bayes’ theorem, independence testing, etc.”
    - *“Expectation”* refers to “problems that calculate the mathematical expectation, mean payoff, or long-run average outcome of a random variable or stochastic process. Includes expectation for discrete/continuous distributions, expected loss, expected number of occurrences, etc. Calculations of quantities defined based on expectation, such as variance, are also included.”
    - *“Minimum Sample Size Required to Achieve a Specified Probability”* refers to “problems that back-calculate the required minimum sample size given a target success probability, confidence requirement, estimation precision, or the probability of at least one occurrence. Includes ‘sample size needed to detect an event at least once’, ‘number of trials needed to achieve 95% coverage probability’, etc.”
    - *“Distribution Derivation”* refers to “problems that derive the probability distribution of a random variable based on probability rules, distribution definitions, or model structures. Approximations based on the Central Limit Theorem are also included.”
    - *“Other”* refers to “problems that are difficult to consistently classify into the above categories but still involve ‘numerical calculations based on probability rules or distribution definitions’. Includes calculation of special probability quantities, etc.”

- **"Numerical Computation"** includes: ["Obtaining Model Parameter Estimates", "Sampling from a Specified Distribution"].
    - *“Obtaining Model Parameter Estimates”* refers to “problems that obtain parameter estimates through analytical or numerical methods, given a model, sample, and estimation criterion. Includes finding regression coefficients, distribution parameters, extreme points, EM iteration results, etc.”
    - *“Sampling from a Specified Distribution”* refers to “problems that generate random samples according to a given probability distribution or model. Includes Monte Carlo sampling, Bootstrap resampling, Normal/Poisson/posterior distribution sampling, etc.”

- **"Descriptive Statistics"** includes: ["Measures of Central Tendency", "Measures of Dispersion", "Measures of Distribution Range", "Measures of Frequency and Proportion", "Quantiles/Percentiles", "Network Graph Indicators", "Analysis and Comparison of Statistical Properties", "Other (e.g., reliability)"].
    - *“Measures of Central Tendency”* refers to “problems that summarize the center of a data distribution with a single value. Includes mean, median, mode, geometric mean, etc.”
    - *“Measures of Dispersion”* refers to “problems that summarize the spread of data with one or a few indicators. Includes variance, standard deviation, coefficient of variation, MAD, IQR, etc.”
    - *“Measures of Distribution Range”* refers to “problems that describe the lower/upper bounds or coverage intervals of data values. Includes range, minimum/maximum, limits, reference intervals, etc.”
    - *“Measures of Frequency and Proportion”* refers to “problems that describe the frequency, proportion, or composition of specific values or categories in data. Includes frequency, proportion, measures of effect (e.g., relative risk, odds ratio), etc.”
    - *“Quantiles/Percentiles”* refers to “problems that calculate or interpret the relative position of data after sorting. Includes quartiles, percentiles, percentile of the median, threshold quantiles, etc.”
    - *“Network Graph Indicators”* refers to “problems that calculate summary indicators for network or graph structures. Includes degree, betweenness centrality, clustering coefficient, network density, average path length, etc.”
    - *“Analysis and Comparison of Statistical Properties”* refers to “problems that analyze and compare the properties, advantages, disadvantages, and applicability of different statistics.”
    - *“Other (e.g., reliability)”* refers to “statistics that aim to ‘summarize data characteristics’ but do not belong to the above categories. Includes reliability, internal consistency (e.g., Cronbach’s alpha), etc.”

- **"Data Distribution Modelling"** includes: ["Model Building", "MLE", "Bayesian"].
    - *“Model Building”* refers to “problems that select an appropriate distribution type or probability model for data based on the scenario and assumptions, and optionally write out its expression.”
    - *“MLE”* refers to “problems that assume data come from a parameterized distribution and estimate parameters by maximizing the likelihood function. Includes fitting Normal, Poisson, Exponential, Weibull distributions, etc.”
    - *“Bayesian”* refers to “problems that construct a posterior distribution based on prior distribution and observed data to make inferences about parameters. Includes Bayesian parameter estimation, posterior intervals, Bayesian hierarchical models, etc.”

- **"Data Visualization"** includes: ["Distribution of Discrete Variables", "Distribution of Continuous Variables", "Relationship Between Discrete and Continuous Variables", "Relationship Between Continuous Variables", "Relationship Between Discrete Variables", "Comprehensive Comparison of Multiple Variables", "Trends Over Time", "Spatial and Geographic Visualization", "Text and Symbolic Visualization", "Stem-and-Leaf Plot", "Other Statistical Graphics"].
    - *“Distribution of Discrete Variables”* refers to “problems that display the theoretical/sampling distribution of a single categorical variable (e.g., frequencies, proportions, or composition of each category). Forms include bar charts, pie charts, Pareto charts, etc.”
    - *“Distribution of Continuous Variables”* refers to “problems that display the theoretical/sampling distribution of a single continuous variable. Forms include histograms, density plots, boxplots, violin plots, ECDF plots, etc.”
    - *“Relationship Between Discrete and Continuous Variables”* refers to “problems that display differences in distribution or central tendency of a continuous variable across levels of a categorical variable. Forms include grouped boxplots, grouped violin plots, grouped density plots, error bar charts, etc.”
    - *“Relationship Between Continuous Variables”* refers to “problems that display the association, trend, or functional relationship between two continuous variables. Forms include scatter plots, scatter plots with fitted lines, bubble charts, etc.”
    - *“Relationship Between Discrete Variables”* refers to “problems that display the joint distribution or compositional differences between two categorical variables. Forms include grouped bar charts, stacked bar charts, mosaic plots, spine plots, etc.”
    - *“Comprehensive Comparison of Multiple Variables”* refers to “problems that display the overall structure, relative differences, or patterns of three or more variables or multiple indicators. Forms include radar charts, parallel coordinate plots, heatmaps, correlation matrix plots, etc.”
    - *“Trends Over Time”* refers to “problems that display the trajectory or trend of one or more indicators over time. Forms include line charts, time series line charts, area charts, grouped time trend plots, etc.”
    - *“Spatial and Geographic Visualization”* refers to “problems that display the distribution pattern of data across geographic space or regions. Forms include choropleth maps, heat maps, point maps, spatial scatter plots, etc.”
    - *“Stem-and-Leaf Plot”* refers to “problems that display the distribution of a single variable along with the original numerical structure using a stem-and-leaf plot. The core is to preserve the original data values while showing the distribution shape.”
    - *“Other Statistical Graphics”* refers to “problems that are difficult to consistently classify into the above categories but still involve statistical graphical representation. Forms include special schematic diagrams or hybrid statistical graphs, etc.”

- **"Association Analysis"** includes: ["Correlation Coefficient (One-dimensional)", "CCA (Multidimensional)", "Contingency Table"].
    - *“Correlation Coefficient (One-dimensional)”* refers to “problems that study the strength of linear or monotonic association between two one-dimensional variables using a specific measure. Includes Pearson, Spearman, Kendall correlation, etc.”
    - *“CCA (Multidimensional)”* refers to “problems that study the linear association structure between two multidimensional variable sets using a statistical model. Includes CCA and its variants.”
    - *“Contingency Table”* refers to “problems that study the joint distribution and association patterns of two or more categorical variables using contingency tables. Includes frequency tables, proportion tables, odds ratio displays, etc.”

- **"Clustering"** includes only: ["Clustering"].
    - *“Clustering”* refers to “problems that automatically group samples based on their similarity without labels. Includes k-means, hierarchical clustering, DBSCAN, spectral clustering, etc.”

- **"Dimensionality Reduction"** includes only: ["Dimensionality Reduction"].
    - *“Dimensionality Reduction”* refers to “problems that compress high-dimensional variables into a lower-dimensional representation while preserving essential information. Includes PCA, factor analysis, t-SNE, UMAP, etc.”

- **"Hypothesis Testing and Interval Estimation"** includes: ["Independence Test", "Mean Test", "Variance Test", "ANOVA", "Distribution Test", "Proportion Test", "Likelihood Ratio Test", "Sequential Test", "Randomness", "Regression Model Parameter Test", "Analysis of Test Properties"]. (Note: Since hypothesis testing and interval estimation are two sides of the same coin, although the secondary categories below are mostly named with "test", they also include the corresponding interval estimation methods.)
    - *“Independence Test”* refers to “problems that use statistical tests to determine whether two variables or two types of events are independent in the population. Includes chi-square test of independence, Fisher’s exact test, etc.”
    - *“Mean Test”* refers to “problems that compare the magnitude of one or more population means to a given value or to each other. Includes one-sample, two-sample, and paired t-tests, etc.”
    - *“Variance Test”* refers to “problems that compare the magnitude of one or more population variances to a given value or to each other. Includes one-sample, two-sample variance tests, etc.”
    - *“ANOVA”* refers to “problems that decompose sources of variation between and within groups. Includes one-way, two-way ANOVA, etc.”
    - *“Distribution Test”* refers to “problems that test whether data conform to a specific theoretical distribution (e.g., standard normal). Includes chi-square goodness-of-fit test, Kolmogorov-Smirnov test, Shapiro-Wilk test, etc.”
    - *“Proportion Test”* refers to “problems that compare the magnitude of one or more population proportions to a given value or to each other. Includes one-sample, two-sample proportion tests, etc.” (Note: Also includes tests for derived measures of proportion, such as risk ratios, odds ratios, etc.)
    - *“Likelihood Ratio Test”* refers to “problems that perform hypothesis testing by comparing the likelihoods of nested or restricted/unrestricted models. Emphasizes ‘testing a specific statistical hypothesis’.”
    - *“Sequential Test”* refers to “problems that perform hypothesis testing progressively as data is collected to decide whether to stop an experiment. Includes SPRT, etc.”
    - *“Randomness”* refers to “problems that test whether a sequence, permutation, or data generation mechanism can be considered random. Includes runs test, randomness tests, etc.”
    - *“Regression Model Parameter Test”* refers to “tests concerning parameters of a regression model, such as regression coefficients, variance, etc.”
    - *“Analysis of Test Properties”* refers to “problems that describe the basic characteristics and requirements of hypothesis testing. Includes significance level, power, Type I error, Type II error, etc.” (Note: Prioritize classification based on the test’s purpose; if none fit and the topic relates to test properties, classify here.)

- **"Model Comparison (Variable Selection)"** includes: ["Criterion-Based Comparison (AIC, BIC, etc.)", "Cross-Validation", "Likelihood Ratio Test", "ROC Curve (AUC), Coverage-Capture Rate Curve", "Identification of Important Variables"].
    - *“Criterion-Based Comparison (AIC, BIC, etc.)”* refers to “problems that compare the优劣 of multiple candidate models using information criteria, penalized criteria, or similar measures. Includes AIC, BIC, Adjusted R², etc.”
    - *“Cross-Validation”* refers to “problems that evaluate the generalization ability of different models through data partitioning or resampling for model selection. Includes k-fold CV, LOOCV, validation set error comparison, etc.”
    - *“Likelihood Ratio Test”* refers to “problems that use the likelihood ratio as a tool for model selection or variable screening to compare whether adding variables improves a nested model. Focuses on ‘which model to select’.”
    - *“ROC Curve (AUC), Coverage-Capture Rate Curve”* refers to “problems that compare the discriminative ability of multiple models based on classification ranking or screening effectiveness. Includes ROC/AUC, lift, gain, coverage-capture, etc.”
    - *“Identification of Important Variables”* refers to “problems that筛选 the most important or explanatory set of independent variables for a response variable. Includes stepwise regression (forward, backward, stepwise selection), LASSO variable selection, etc.”

- **"Model Diagnosis"** includes: ["Residual Analysis", "Goodness-of-Fit Assessment"].
    - *“Residual Analysis”* refers to “problems that check the reasonableness of a model fit through residual plots, residual distributions, outliers, influential points, etc. Includes diagnosis of linearity, heteroscedasticity, outliers, leverage, etc.”
    - *“Goodness-of-Fit Assessment”* refers to “problems that evaluate the degree to which a specified model fits the data using model fit indicators. Includes R², adjusted R², etc.”

- **"Model Interpretation"** includes: ["Interpretation of Regression Coefficient Significance and Direction", "Interpretation of Regression Effect Size", "Interpretation of Factors Influencing Classification or Occurrence Probability", "Interpretation of Mechanisms Influencing Ordered Outcomes", "Interpretation of Variable Importance Ranking", "Interpretation of Group Heterogeneity"].
    - *“Interpretation of Regression Coefficient Significance and Direction”* refers to “problems that, after a model is built, explain whether the influence of an independent variable on the response variable is significant and its direction based on parameter estimation results. Includes interpreting the sign and significance of regression coefficients in linear regression, generalized linear models, or Cox models.”
    - *“Interpretation of Regression Effect Size”* refers to “problems that, after a model is built, quantify the magnitude of a variable’s effect on the response variable based on parameter estimates or marginal effects. Includes interpreting the change in response due to a unit change, marginal effects, elasticity coefficients, etc.”
    - *“Interpretation of Factors Influencing Classification or Occurrence Probability”* refers to “problems that, within binary classification or event occurrence models, explain how variables affect the probability of an event based on model parameters. Includes interpreting odds ratios (OR) in logistic regression, hazard ratios (HR) in survival models, etc.”
    - *“Interpretation of Mechanisms Influencing Ordered Outcomes”* refers to “problems that explain how variables affect the tendency towards different outcome levels in ordered response models. Includes interpreting the effect of variables on the probability of each level in ordered logistic regression, ordered probit models, etc.”
    - *“Interpretation of Variable Importance Ranking”* refers to “problems that, after a model is built, compare the relative importance of variables using standardized coefficients, feature importance, or contribution measures. Includes comparison of standardized regression coefficients, variable importance from random forests, SHAP value interpretation, etc.”
    - *“Interpretation of Group Heterogeneity”* refers to “problems that compare differences in variable effects across different groups or sub-samples. Includes comparing coefficients from models estimated separately by gender, region, or time, interaction term interpretation, etc.”

- **"Classification and Prediction"** includes: ["Continuous Value Prediction", "Categorical Variable Classification", "Multi-class Classification of Ordered Variables", "Quantile Prediction", "Survival Analysis"].
    - *“Continuous Value Prediction”* refers to “problems that predict future or unknown values of a numerical response variable.”
    - *“Categorical Variable Classification”* refers to “problems that predict unordered categorical labels. Includes binary classification and unordered multi-class classification.”
    - *“Multi-class Classification of Ordered Variables”* refers to “problems that predict a multi-category response variable with a natural order.”
    - *“Quantile Prediction”* refers to “problems that predict a specific quantile of the conditional distribution, rather than the mean. Includes median regression, prediction of the 90th percentile loss, etc.”
    - *“Survival Analysis”* refers to “problems that study time-to-event data and censoring, focusing on the survival function, hazard function, or median survival time. Includes KM curves, Nelson-Aalen curves, Cox models, accelerated failure time models, etc.”

- **"Time Series Analysis"** includes: ["Lag Correlation Analysis", "Stationarity Analysis", "Seasonality Analysis", "Deterministic Factor Decomposition", "Volatility Analysis"].
    - *“Lag Correlation Analysis”* refers to “problems that analyze the autocorrelation structure of a time series. Includes analysis of the Autocorrelation Function (ACF), Partial Autocorrelation Function (PACF), etc.”
    - *“Stationarity Analysis”* refers to “problems that test whether a time series satisfies stationarity conditions. Includes unit root tests (ADF, KPSS, etc.), graphical stationarity analysis, etc.”
    - *“Seasonality Analysis”* refers to “problems that identify, estimate, or explain seasonal repeating patterns in a time series. Includes analysis of monthly, quarterly, day-of-week effects, etc.”
    - *“Deterministic Factor Decomposition”* refers to “problems that decompose a time series into trend, cycle, seasonal, or other deterministic components. Includes trend fitting, cycle identification, classical decomposition, etc.”
    - *“Volatility Analysis”* refers to “problems that focus on modeling the time-varying conditional variance of a time series. Includes ARCH/GARCH analysis.”

- **"Text Data Analysis"** includes: ["Tokenization", "Word Frequency Statistics", "Topic Modeling", "Sentiment Analysis"].
    - *“Tokenization”* refers to “problems that segment raw text into words, tokens, or basic analysis units. Includes Chinese word segmentation, pre-processing segmentation before stop word removal, etc.”
    - *“Word Frequency Statistics”* refers to “problems that count the frequency and ordering of words, phrases, or tokens. Includes word frequency tables, TF statistics, high-frequency word identification, etc.”
    - *“Topic Modeling”* refers to “problems that automatically extract latent topic structures from large-scale text collections. Includes LDA, CTM, Dynamic Topic Models, etc.”
    - *“Sentiment Analysis”* refers to “problems that determine the emotional polarity, attitudinal tendency, or subjective evaluation expressed in text. Includes positive/negative classification, sentiment intensity scoring, etc.”

- **"Network Data Analysis"** includes: ["Community Detection", "Link Prediction"].
    - *“Community Detection”* refers to “problems that identify groups of nodes that are more densely connected internally and sparsely connected externally in a network. Includes modularity optimization, spectral methods, stochastic block models, etc.”
    - *“Link Prediction”* refers to “problems that predict missing or future edges based on existing network structure or node attributes. Includes friend recommendation, collaboration prediction, co-movement prediction, etc.”

- **"Experimental Design"** includes: ["Experiment (Sampling) Plan Design", "Experiment (Sampling) Plan Evaluation"].
    - *“Experiment (Sampling) Plan Design”* refers to “problems that design an experimental or sampling plan to meet specific research objectives. Includes simple random sampling, stratified sampling, etc.”
    - *“Experiment (Sampling) Plan Evaluation”* refers to “problems that evaluate the performance of an experimental or sampling plan based on aspects like sampling error and representativeness.”

- **"Causal Inference"** includes: ["Observational Data", "Experimental Data"].
    - *“Observational Data”* refers to “problems that identify treatment effects or causal relationships in non-experimental, non-randomized data. Includes propensity score matching, instrumental variables, regression discontinuity design, difference-in-differences, etc.”
    - *“Experimental Data”* refers to “problems that estimate treatment effects under randomized or quasi-experimental conditions. Includes randomized controlled trial (RCT) analysis, A/B testing effect evaluation, randomized block experiment analysis, etc.”

- **"Critical Evaluation of Statistical Results"** includes: ["Identification of Statistical Fallacies and Biases", "Evaluation of Reliability of Statistical Results"].
    - *“Identification of Statistical Fallacies and Biases”* refers to “problems that identify and explain common fallacies, biases, or misuses in statistical analysis. Includes selection bias, confounding variables, etc.”
    - *“Evaluation of Reliability of Statistical Results”* refers to “problems that assess the reliability of statistical results based on factors such as sample size, etc.”

2. Relevant variables and their roles (variables)  
Key requirements:  
    1. Variables specifically refer to the data objects collected for the research objective in the question and their statistical measures (e.g., sample size, mean, standard deviation), excluding model parameters, statistics related to specific statistical models/distributions (e.g., z-score, p-value), and statistics related to specific statistical methods (e.g., t-value, F-value).  
    2. Variable objects can be raw data columns, grouped statistics, contingency tables, sample sizes, success counts, or time variables.  
    3. In particular, if the problem to be solved in the question is of the "Mathematical Calculation" type, please treat the numerical objects such as probabilities and sample sizes actually used in the answer as variable objects for extraction.
    4. If no explicit data table is provided or `data` is empty, but symbolic variables, statistics, or logical judgment objects (e.g., `X`, `Y`, `r`, an event, a statistic) have already appeared, variables must still be extracted accordingly.  
    5. When the original data has a grouping structure, prioritize splitting the data into multiple variables according to the grouping. If each sample belongs to different groups based on different grouping methods, after splitting, additionally note in the description of these variables that they share the same samples with certain other variables but represent different groupings/features.  
    6. If the problem provides aggregated measures for multiple variables (e.g., mean, standard deviation, sample size), create a separate variable object for each variable and write these aggregated measures into the `value` field of each variable object in JSON format.  
    7. If the information is insufficient to support any variables, directly output an empty JSON: `{}`.  
    8. The output must be strictly JSON, with the top-level keys being variable IDs, and no additional text should be output.  

Field specifications:  
- Top-level key: "Variable name (extracted from the problem or an appropriately assigned variable name)".  
- `id`: Variable identifier, must exactly match the top-level key.  
- `value`: The complete value of the current variable. If it is a column from a table, an array can be used; if it is aggregated measures (including statistics, sample size, etc.), a JSON value can be used (keys are the names of the aggregated measures, and values are the corresponding values); if neither of the above forms is suitable for representation, copy and paste the original recorded form of the variable from the problem (e.g., a table recorded in TeX syntax). When there are multiple numerical values in `value`, ensure their order matches the original order in the problem.  
- `class`: Can only be one of `numerical`, `categorical`, or `others`. (Numerical type is denoted as "numerical", categorical type as "categorical", and those not belonging to the above categories as "others".)  
- `role`: Can only be one of `X`, `Y`, `XY`, or `NR`.  
  - `X`: Independent variable. Refers to a variable actively manipulated by the researcher or naturally existing and not influenced by other variables. It is the cause or condition that induces changes in other variables. The original variables used to construct the independent variable also belong to this role.  
  - `Y`: Dependent variable or explained variable. Refers to a variable whose changes are caused by changes in the independent variable. It is the outcome observed and measured by the researcher. The original variables used to construct the dependent variable also belong to this role.  
  > Please note: The roles `X` and `Y` are distinguished only when there is a clear directional relationship between variables (they always appear together).  
  - `XY`: Refers to studying the correlation between two (or more) variables without the need to distinguish causality, or when the variable plays both causal roles.  
  - `NR`: No need to specify direction. Refers to situations where it is unnecessary to distinguish between independent and dependent variables. This generally includes the following cases:  
      - Variables used solely as sample identifiers or indices, which must be included in the variable set to match samples across multiple datasets.  
      - Variables used solely to filter a subset of samples for analysis (e.g., the "year" variable when studying data from 2020) and thus must be included in the variable set.  
      - Variables involved in unsupervised methods (clustering, dimensionality reduction).  
      - Variables involved only in describing the numerical distribution of data or the stationarity of a time series.  
> Special cases for `role`:  
    1. For "Trends Over Time" problems under "Data Visualization," the variable representing the time concept must be assigned as `X`, and the variable changing over time as `Y` (even if the time variable does not appear in the variable set). For example, when studying the sales trend over different time points, the time variable is `X`, and the sales variable is `Y`.  
    2. If a variable serves both as an independent variable and is used to construct the dependent variable, its role is `X`.  
    3. If a variable serves both as a dependent variable and is used to construct the independent variable, its role is `Y`.  
- `description`: A brief description of the variable object.  

- For relatively shallow analyses of correlations between variables, "Data Visualization" methods are generally used for intuitive presentation. For deeper analysis of the direction, magnitude, and significance of correlations, building a model and interpreting the model results is generally considered.  
- Problems involving forecasting future sequences in time series should be categorized under "Continuous Value Prediction," while "Time Series Analysis" focuses on interpreting time series models.  

The output format is JSON. A complete output example is as follows:  

{
  "category": "Relationship Between Continuous Variables",
   "variables": {
    "X_height": {
      "id": "X_height",
      "value": {
        "μ": 138,
        "σ": 7
      },
      "class": "numerical",
      "role": "NR",
      "description": "Heights of 10-year-old boys, following a Normal distribution with population mean μ=138 cm and population standard deviation σ=7 cm."
    },
    "threshold": {
      "id": "threshold",
      "value": 150,
      "class": "numerical",
      "role": "NR",
      "description": "The cutoff value (150 cm) used in the answer to compute the proportion of the population below this height, directly substituted into the z-score formula z=(150−138)/7."
    }
  }
}

'''
