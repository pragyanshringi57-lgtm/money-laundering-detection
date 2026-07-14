Data Source
Due to GitHub's file size limits and standard data privacy practices, the raw transaction dataset is not uploaded to this repository. 
This project uses the **Anti Money Laundering Transaction Data** (`SAML-D.csv`) from Kaggle.
**To run this pipeline locally:**
1. Visit the [Kaggle AML Prediction Data Page](https://www.kaggle.com/code/gbiamgaurav/aml-prediction/input).
2. Download the `SAML-D.csv` file (approx. 996 MB).
3. Create a folder named `data/` in the root directory of this project.
4. Place the downloaded `SAML-D.csv` file inside the `data/` folder.
5. the intial rule based filltering genrate it's own synthetic data
6. 
info about data "The dataset incorporates 12 features and 28 typologies (split between 11 normal and 17 suspicious). These were selected based on existing datasets, the academic literature, and interviews with AML specialists. The dataset comprises 9,504,852 transactions, of which 0.1039% are suspicious. It also includes 15 graphical network structures to represent the transaction flow within these typologies. The structures, while sometimes shared among typologies, vary significantly in parameters to increase complexities and challenge detection efforts. More details about these typologies are available in the paper above. The dataset is an updated version compared to the paper."
