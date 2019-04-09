## "Mega-constellation analysis: reliability strategies and insurance policies"

> The core project aim is creating and running the model of orbital processes in terms of huge amount of satellite and estimate its weak points and bottle-necks and influence of the stellite failure on the telecomm service in particular. Most of the modelling is made for the SpaceX constellation. The final aim of the project is the determination of the best ADR and insurance strategy for mega-constellations.

![Space debris pic from phys.org](https://3c1703fe8d.site.internapcdn.net/newman/gfx/news/hires/2018/whyspacedebr.jpg)

### Brief

The project has started its development in early 2018 and has been developed during that time. In September 2018 the modelling process has benn initiated and migrated to the diploma thesis. The programming language -- **Python 3.6**. Additioonaly some matlab scripting, GMAT modelling, [CDP4-IME](https://github.com/RHEAGROUP/CDP4-IME-Community-Edition) modelling and external APIs (such as Google Maps Geocoding) were used locally.

The script has some external libraries dependencies but has no version conflicts:
1. Numpy;
2. [Aeronet lib](https://github.com/aeronetlab/aeronetlib);
3. CSV;
4. Shapely.

The project is missing several important parts:
1. The Population data .asc - too large to be uploaded;
2. References;
3. Outputs.

### Project hierarchy
The project composed to be splitted by **preprocessing** part, **core** and **postprocessing**. 

The **preprocessing** part is based on the *raw data* and preparing the data for processing and simulation part. Results obtaines by the **preprocessing** part are stored in the *PP_Data* folder.

The **core** is composed to run all the main methods and initiate all the main classes of the model to simulate orbital, marketing and financial processes. Thus, this part has several most important classes:
* Maths - contains all the mathematical methods, not available in numpy for celestrial mechanics and other applications;
* Strategy/ Company - classes to set up relative parameters of insurance strategy and company CAPEX and OPEX metrics;
* Satellite - sets up all the satellite data and metrics;
* Simulation - the instance of that class contains main information regarding the simulation process.

The main file has several conditional lines and sets up the *Simulation* class, then runs the simulation.
Finally, the postprocessing part supposed to be a visualisation of the results.

### Additionals
Additionally the project has (or supposed to have):
* LATEX diploma work;
* Unused files (non-git iterations, just in case)
* Raw-stats except population.
