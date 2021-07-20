# brazil-discharge
Python scripts for downloading and processing daily river discharge (or flow) data from Brazil's Hidroweb site, https://www.snirh.gov.br/hidroweb/apresentacao.

Created by Matthew Heberger in July 2021, as part of my PhD research in global hydrology and remote sensing. 

It took me a while to figure out how to aquire this data, and how to get the data into a useful format, so hopefully this can save others some time and effort. 

Brazil is of great interest to hydrologists and is extraordinarily well-monitored. There are hundreds of gages (or stations) where river flow (or discharge) is measured, or has been measured in the past. There are so many things that one could do with this data: trend detection, time series analyses, regression against other environmental variables, calibration and validation of hydrologic models, etc...

The list of stations here is taken from the CABra dataset, created by Almagro et al. (2021). The authors compiled daily flow data and a lot of related information for 735 gages from 1980 to 2010 (30 years in total). All the datasets are at least 90% complete. Note that there is another, similar journal article that came out the year before and has open data for 897 gages (Chagas et al. 2020).

The purpose of these Python scripts was to extend these records to include daily flow data from 2010 to present. 

Thank you to Ayan Santos Fleischmann and Jessica Fontoura at the Instituto de Pesquisas Hidráulicas (IPH/UFRGS) for help in understanding these data and files. 

## References:

Almagro, André, Paulo Tarso S. Oliveira, Antônio Alves Meira Neto, Tirthankar Roy, and Peter Troch. 2021. “CABra: A Novel Large-Sample Dataset for Brazilian Catchments.” Hydrology and Earth System Sciences 25 (6): 3105–35. https://doi.org/10.5194/hess-25-3105-2021.

Chagas, Vinícius B. P., Pedro L. B. Chaffe, Nans Addor, Fernando M. Fan, Ayan S. Fleischmann, Rodrigo C. D. Paiva, and Vinícius A. Siqueira. 2020. “CAMELS-BR: Hydrometeorological Time Series and Landscape Attributes for 897 Catchments in Brazil.” Earth System Science Data 12 (3): 2075–96. https://doi.org/10.5194/essd-12-2075-2020.

