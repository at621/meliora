Introduction
========================================================

.. toctree::
    :hidden:
    :maxdepth: 2
    :caption: Overview

    tests
    resources
    contributing
    usage
    unit_testing
   
   
.. toctree::
    :hidden:
    :maxdepth: 2
    :caption: Validation tests

    meliora/meliora


====================
About the package
====================
meliora is a Python package that provides a set of statistical tests and tools to assess the performance of the credit risk models. All tests are covered with unit tests and algorithms have been replicated in other tools like R, MATLAB and SAS to avoid errors. Whenever possible, the definition of the test was retrieved from the authoritive source like the EBA, the ECB or the Basel Committee.

The main contributors started building their first statistical credit models back in 2003. Over the years, we have impemented similar set of tests in several different financial institutions.

This package is standing on the shoulders of giants as it makes heavy use of the Python ecosystem and especially Scikit-learn, Scipy and Statsmodels. Several functions are straightforward wrappers using these resources and are provided to the user for convenience purposes. The authors have taken great care to ensure that no part of this package contains proprietary code.

Main aim
-----------------
The aim of this package is to provide credit risk practioners with the tools to develop their credit risk models without the need to implement standard tooling. All tests should be covered with unit tests and algorithms should be replicated using other tools to avoid errors.

Main Features
-----------------
  - tests cover both IFRS 9 and IRB models as well as non-regulatory models
  - the tool contains more than 30 tests
  - all test have been covered with unit tests 
  - the tests have been documented in detail
  - commonly accepted tresholds have been provided for convenience purposes

  For the list of all tests, see Overview > List of tests
  

Full list of dependencies
---------------------------
- NumPy (https://www.numpy.org)
- Pandas (https://pandas.pydata.org/)
- Statsmodels (https://www.statsmodels.org/)
- Scikit-learn (https://scikit-learn.org/)
- Scipy (https://scipy.org/)


Getting Help
------------------

For usage questions, send an email to anton.treialt@aistat.com

License
----------------------
MIT LIcense