# PV bidding optimization - Replicating Visser et al. (2024)

**Authors:** Daniel Guivernau, Evgenia Tsoni  
**Course:** Optimization for Energy Markets and Systems  
**Reference Paper:** *Probabilistic solar power forecasting: An economic and technical evaluation of an optimal market bidding strategy* (Visser et al., 2024)

In this repo we make available all the code developed during our project.

An overview on its structure:
1. `getting_DAM_prices.py` and `preprocessing_data.py` are the functions we used to prepare the data needed for the rest of the project. These however don't need to be run again, as the resulting `preprocessed_data.csv` is made available inside the `datasets` folder.
2. The folder `models` includes the .mod files defining the optimization models used to calculate DAM prices.
3. `functions.py` includes the most important functions defined for the core of the project.
4. `yearly_evaluation.py` is the year-long backtesting script used to generate the final results in the interim project.
5. The Jupyter Notebook `testing.ipynb` includes a series of plots, and analysis developed as ways of testing the functions referenced above.