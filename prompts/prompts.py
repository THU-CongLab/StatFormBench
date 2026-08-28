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
