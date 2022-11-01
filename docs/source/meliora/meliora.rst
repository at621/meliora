The aim of the validation tools is to monitor the performance of models in
the following areas:


Discrimination tests
--------------------
.. toctree::
   :maxdepth: 4
   :hidden:

   meliora.Accuracy_Ratio
   meliora.Bayesian_Error_Rate
   meliora.Bucket_Test
   meliora.CIER
   meliora.CLAR
   meliora.Information_Value
   meliora.Kendall_tau
   meliora.Kolmogorov_Smirnov_test
   meliora.Loss_Capture_Ratio
   meliora.Receiver_Operating_Characteristic
   meliora.Somers_D
   meliora.Spearman_Rank_Correlation


The analysis of discriminatory power is aimed at ensuring that the ranking of
customers that results from the rating process appropriately separates riskier and
less risky customers.


Calibration
--------------------
.. toctree::
   :maxdepth: 4
   :hidden:

   meliora.Binomial_test
   meliora.ELBE_t_test
   meliora.Hoshmer_Lemeshow_Test
   meliora.Jeffreys_Test
   meliora.Normal_Test
   meliora.LGD_t_test
   meliora.Loss_Shortfall
   meliora.Mean_Absolute_Deviation
   meliora.Spiegelhalter_Test
   meliora.Traffic_Lights_Approach

The analysis of predictive ability (or calibration) is aimed at ensuring that the PD
parameter adequately predicts the occurrence of defaults – i.e. that PD estimates
constitute reliable forecasts of default rates.


Stability
--------------------
.. toctree::
   :maxdepth: 4
   :hidden:

   meliora.Concentration_of_Rating_Grades
   meliora.Population_Stability_Index
   meliora.Herfhindahl_Index
   meliora.Grade_Migrations

The analyses provide insight with regard to the stability of rating model
outputs over the observation period. The stability of risk estimates is 
assessed using customer migrations, stability of the migration matrix 
and concentration in rating grades.