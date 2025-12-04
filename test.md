______________________________________________________________________

abstract: |

# Objective

The study aimed to determine if and how environmental factors correlated with
asthma admission rates in geographically different parts of Guangxi province in
China.

# Setting

Guangxi, China.

# Participants

This study was done among 7804 asthma patients.

# Primary and secondary outcome measures

Spearman correlation coefficient was used to estimate correlation between
environmental factors and asthma hospitalisation rates in multiple regions.
Generalised additive model (GAM) with Poisson regression was used to estimate
effects of environmental factors on asthma hospitalisation rates in 14 regions
of Guangxi.

# Results

The strongest effect of carbon monoxide (CO) was found on lag1 in Hechi, and
every 10 µg/m^3^ increase of CO caused an increase of 25.6% in asthma
hospitalisation rate (RR 1.26, 95% CI 1.02 to 1.55). According to the
correlation analysis, asthma hospitalisations were related to the daily
temperature, daily range of temperature, CO, nitrogen dioxide (NO~2~) and
particulate matter (PM~2.5~) in multiple regions. According to the result of
GAM, the adjusted R^2^ was high in Beihai and Nanning, with values of 0.29 and
0.21, which means that environmental factors are powerful in explaining changes
of asthma hospitalisation rates in Beihai and Nanning.

# Conclusion

Asthma hospitalisation rate was significantly and more strongly associated with
CO than with NO~2~, SO~2~ or PM~2.5~ in Guangxi. The risk factors of asthma
exacerbations were not consistent in different regions, indicating that targeted
measures should differ between regions. author:

- Rui Ma
- Lizhong Liang
- Yunfeng Kong
- Mingyang Chen
- Shiyan Zhai
- Hongquan Song
- Yane Hou
- Guangli ZhangCorrespondence to Dr Yunfeng Kong; <yfkong@henu.edu.cn>
  copyright: statement: © Author(s) (or their employer(s)) 2020. Re-use
  permitted under CC BY-NC. No commercial re-use. See rights and permissions.
  Published by BMJ. year: 2020 date: 2020-10 institute:
- 1Key Laboratory of Geospatial Technology for the Middle and Lower Yellow River
  Regions, Henan University, Kaifeng, China
- 2The Affiliated Hospital, Guangdong Medical University, Zhanjiang, China
- 3College of Computer and Information Engineering, Henan University, Kaifeng,
  China license: link: "http://creativecommons.org/licenses/by-nc/4.0/" text:
  "This is an open access article distributed in accordance with the Creative
  Commons Attribution Non Commercial (CC BY-NC 4.0) license, which permits
  others to distribute, remix, adapt, build upon this work non-commercially, and
  license their derivative works on different terms, provided the original work
  is properly cited, appropriate credit is given, any changes made indicated,
  and the use is non-commercial. See: ." type: open-access references:
- id: R1
- id: R2
- id: R3
- id: R4
- id: R5
- id: R6
- id: R7
- id: R8
- id: R9
- id: R10
- id: R11
- id: R12
- id: R13
- id: R14
- id: R15
- id: R16
- id: R17
- id: R18
- id: R19
- id: R20
- id: R21
- id: R22
- id: R23
- id: R24
- id: R25
- id: R26
- id: R27
- id: R28
- id: R29
- id: R30
- id: R31
- id: R32
- id: R33
- id: R34
- id: R35
- id: R36
- id: R37
- id: R38
- id: R39
- id: R40
- id: R41
- id: R42
- id: R43
- id: R44
- id: R45
- id: R46
- id: R47
- id: R48
- id: R49
- id: R50
- id: R51 title: Spatiotemporal variations of asthma admission rates and their
  relationship with environmental factors in Guangxi, China

______________________________________________________________________

::: caption

###### Strengths and limitations of this study

:::

- The study area covered 14 regions in Guangxi, with an area of 237 600 km^2^
  and a population of 48 million people.

- We analysed temporal and spatial variations of asthma hospitalisation rates
  for 14 regions.

- Spearman correlation coefficient was used to perform correlation analysis
  between meteorological factors, air pollutants and asthma hospitalisation
  rates in 14 regions.

- Generalised additive modelGeneralised additive model was used to explore the
  associations between air pollutants, meteorological factors and asthma in 14
  regions, respectively.

- This study did not consider the effect of biological air pollutants on asthma
  due to the lack of data.

# Introduction {#s1}

Asthma is a common chronic inflammatory respiratory disease. Among susceptible
individuals, asthma can cause wheezing, dyspnoea, chest tightness and coughing,
especially at night or early in the morning.[@R1] It seriously threatens public
health. In 2004, approximately 300 million people suffered from asthma
worldwide[@R2; @R3]; in 2008, about 30 million people suffered from asthma in
China; both figures have been steadily increasing.[@R4; @R5] The risk factors
for asthma include genetics, gender and the environment, while environmental
risk factors include meteorological conditions, allergens in the air, viral
respiratory infections, smoke, air pollution, occupation and diet.\[@R6; @R7;
@R8\]

Air pollutants and meteorological factors related to asthma have been reported
worldwide.\[@R9; @R10; @R11; @R12; @R13; @R14; @R15; @R16; @R17; @R18; @R19;
@R20; @R21; @R22; @R23; @R24; @R25; @R26\] Some studies found that climatic
differences had a significant influence on asthma.[@R19; @R20; @R21; @R22; @R23]
Several prior studies have shown that temperature influences asthma
exacerbations.[@R11; @R20; @R21; @R22; @R23] Some studies showed evidence of an
association between air pollutants and asthma.\[@R14; @R15; @R16; @R17; @R18;
@R19; @R24\] Tian *et al* found a significant association between particulate
matter (PM~2.5~) and daily exacerbations of asthma.[@R9] Nitrogen dioxide
(NO~2~) and carbon monoxide (CO) were found to have the greatest impact on
asthma.[@R11; @R15] Numerous studies have been done on the associations between
air pollutants, meteorological factors and asthma, but the conclusions are
inconsistent.[@R10; @R11; @R13; @R14; @R21; @R26]

The relationship between asthma and environmental factors varies from region to
region, and spatial difference in asthma should be taken into account.\[@R23;
@R25\] The prevalence of asthma may vary with location,[@R27] and changes in
environmental factors in different seasons greatly influence respiratory
diseases.[@R28] For instance, the correlation between asthma and O~3~ varies
with seasons, and there are regional differences in sulfur dioxide (SO~2~)
levels.[@R29] The associations between air pollutant concentrations and asthma
hospitalisation differ from region to region,[@R30] and most studies have only
assessed the effects of environmental factors on asthma hospitalisation in
single region. Chang *et al* considered the influence of geographical factors on
asthma and analysed the relationship between food, dog ownership, housing area
and disposable income from the perspective of community variables and found that
asthma incidence differed by region,[@R31] but did not consider the effects of
meteorological factors and air pollution on asthma. There are significant
regional changes in some environmental factors that affect asthma, but these are
often ignored. It is necessary to explore the relationship between environmental
factors of asthma hospitalisation in multiple regions. In addition, there were
lots of studies exploring association between air pollution and asthma in China.
However, to our knowledge, regions of studies were often concentrated on areas
with high level of air pollution in the north and central China, such as
Beijing, Shanghai, Jinan and Hefei.[@R9; @R11; @R18; @R20; @R32] Considering
geographical disparities and air pollution characteristics, it is essential to
explore the impacts of air pollution on asthma in areas with low level of air
pollution in southern China.

Guangxi is located in southern China with low level of air pollution. The
prevalence of asthma has been reported to be at a moderate level in Guangxi,
China.[@R32; @R33] In this study, we used the 14 regions (cities) in Guangxi as
a study area; these regions include both coastal and inland areas with different
geographical and climatic characteristics. This study attempted to explore the
spatiotemporal patterns of asthma hospitalisations and its relationship with
environmental factors in 14 regions in Guangxi. The conclusions may be useful
for public health departments to provide targeted preventive measures.

# Methods {#s2}

## Study design {#s2-1}

In this study, daily data were used to explore the relationship between air
pollutants, meteorological factors and asthma hospitalisation rates in 2015.
First, Spearman correlation coefficient was applied to evaluate the correlations
between meteorological factors, air pollutants and asthma hospitalisation rates
in 14 regions, respectively. Second, we combined generalised additive model
(GAM) with Poisson regression to quantify the degree of interaction between
environmental factors responsible for the variation in asthma hospitalisation
rate. Finally, we estimated the relative risk (RR) between exposure to air
pollutants and hospitalisation for asthma and explored the lagging effects of
environmental factors on asthma.

## Research location and data source {#s2-2}

This study was performed in 14 regions in Guangxi
([figure 1](#F1){ref-type="fig"}), China, with an area of 237 600 km^2^. Guangxi
has a subtropical monsoon climate.[@R34] Geographically, the land slopes from
northwest to southeast. The topography and related climatic characteristics vary
greatly in different regions of Guangxi. The air pollution in Guangxi is mainly
generated locally, and not blown in from other areas.[@R35] Guangxi has four
seasons: spring (March--May), summer (June--August), autumn
(September--November) and winter (December--February).

<figure id="F1">
F1
<p><span class="image placeholder"
data-original-image-src="bmjopen-2020-038117f01"
data-original-image-title=""></span></p>
<figcaption>Geographic location of Guangxi in China, and asthma
hospitalisations in 14 regions in Guangxi (2015).</figcaption>
</figure>

Daily hospitalisation cases for asthma were originally collected from all
county-level and city-level hospitals in 14 regions in Guangxi, China. None of
the asthma data we obtained contained personal information. We have obtained
ethics approval for our study, and this study was approved by the biomedical
research ethical subcommittee of Henan University (China). These hospitals were
almost evenly distributed in 14 regions of Guangxi, with each region containing
at least two hospitals. Asthma data were collected from hospital records dated 1
January--31 December 2015, based on the disease codes defined by the 10th
Revision of the International Classification of Diseases. Diagnostic coding of
'J45.xxx', such as 'J45.900', 'J45.901' and 'J45.902', returned 7804 hospital
admissions in 2015 due to asthma. The contents of records were diagnostic
information, admission date, duration of hospital stay, age, sex and residence
address. In this study, we aggregated the asthma cases at the city level
according to the patient's residence address. Patients with residence address
outside Guangxi were excluded.

Daily data of environmental factors were collected, including air pollution
concentration, and meteorological data from 1 January to 31 December 2015. Daily
air pollutant data aggregated data for the 14 regions, directly collected from
China's air quality online platform of monitoring and analysis
(<https://www.aqistudy.cn/historydata>). The data included: average daily level
of SO~2~, NO~2~, PM~2.5~ and CO. Daily meteorological factors were obtained from
600 monitoring stations as found on the National Meteorological Information
Center website (<http://data.cma.cn/>), including daily average temperature (T),
daily maximum temperature, daily minimum temperature, average relative humidity
percentage (RHU) and average wind speed (WIN). Daily meteorological factors for
the 14 regions were interpolated from data based on 600 monitoring sites in
China. Moreover, this study introduced daily range of temperature (TDIFF),
referring to the difference between the maximum and minimum temperatures on the
same day, as an influencing factor. Demographic characteristics for the 14
regions were obtained from 2015 Guangxi Statistical Yearbook[@R36] and the Sixth
National Census in 2010.[@R37] The populations of the 14 regions in 2015 were
available from the Guangxi Statistical Yearbook; populations of specific age
groups were modelled weights based on the Sixth National Census in 2010.[@R37]

## Patient and public involvement {#s2-3}

Patients and the public were not involved in the design or planning of the
study.

## Analysis model {#s2-4}

In this study, Spearman correlation coefficient was used to study the
correlation of air pollutant, and meteorological factors with daily hospital
admission rates due to asthma for 14 regions in 2015, respectively. In this
study, we used two-sided test, and p values smaller than 0.05 were considered
statistically significant. Spearman correlation coefficient was performed in IBM
SPSS Statistics (V.21).

We analysed the effect of the interaction between meteorological factors and air
pollutants on asthma, using Poisson regression in a GAM.[@R38; @R39] The
relationship between explanatory variables and dependent variables was
established by using smoothing function, which is linear or non-linear.[@R40] A
non-parametric GAM was established to quantify the effect of the interaction
between environmental factors on asthma hospitalisation. To explore the effects
of long-term trends and weeks on the results, we introduced week variables and
date sequence variables. The model is described as follows:

$$\\begin{matrix} {Log(E\\lbrack Admissions\\rbrack)} & {= s(T) + s(TDIFF) +
s(RHCU) + s(WIN)} \\ & {+ s(PM2.5) + s(SO2) + s(CO)} \\ & {+ s(NO2) + te(DOY) +
te(DOW)} \\end{matrix}$$

where Y represents daily asthma hospitalisation rate, and T, TDIFF, RHU, WIN,
PM~2.5~, SO~2~, CO and NO~2~ were explanatory variables. T is the daily average
temperature; TDIFF is the daily range of temperature; RHU is the average
relative humidity percentage and WIN is the average wind speed. DOY is the day
of the year, and DOW is the day of the week. s(.) is the thin plate regression
spline smooth function and te(.) is the tensor product smooth function. The
outcome variables were adjusted R^2^ and deviance explained. Adjusted R^2^
measures the degree to which the response variable is related to all explanatory
variables. In GAM, the 'deviance' is similar to likelihood-ratio statistic,
which is widely used in generalised linear models. Here, the variable deviance
explained the ability of explanatory variables to explain the variation in
hospitalisation rates.

Then, a semiparametric GAM with Poisson link was used to estimate the
exposure--response relationships between air pollutants and asthma while
adjusting for confounding variables, including week effect and meteorological
factors. The effects of exposure to meteorological factors and air pollutants
may lead to asthma hospitalisation on the same day or later. In this study, we
performed GAMs both on the same day with hospitalisation (lag 0) and on the 5
following days (lag 1 to lag 5). The model is described as follows:

$$\\begin{matrix} {Log(E\\lbrack Y\\rbrack) =} & {\\beta Xi + s(T) + s(TDIFF) +
s(RHU)} \\ & {+ s(WIN) + te(DOY) + te(DOW)} \\end{matrix}$$

where Y is the daily number of asthma admissions, and X~i~ are the daily
concentrations of CO, NO~2~, SO~2~ and PM~2.5~, respectively. β is the
coefficient of X~i~ in the model. The estimated effects were RR with 95% CI,
corresponding to an increment of 10 µg/m³ in the levels of CO, NO~2~, SO~2~ and
PM~2.5~.

RR was calculated by the following equation:

RR=e^β×k^, (3) where k is the unit of increase for X~i~, and CI is
(exp[(β−1.96×Se)×k], exp\[(β+1.96×Se)×*k*\]). Se is the SE of the model in Eq
(2).

We checked the robustness of models to: (1) determine the smoothing parameters
and (2) df selection. Tests were conducted with different df for each variable.
In GAM, df in this model were selected by the lowest Akaike information
criterion. This study used Generalized cross validation criteria (GCV) as the
estimation method to select smoothing parameters.

# Results {#s3}

## General descriptive statistics {#s3-1}

According to the statistics, the ratios of males and females admitted for asthma
were 52.1% and 47.9%, respectively. The patients were grouped by age, with 25.9%
of patients 0--14 years old, 4.7% of patients 15--29 years old, 11.6% of
patients 30--44 years old, 22.4% of patients 45--59 years old, 23.4% of patients
60--75 years old and 12.0% of patients over 75 years old.
[Table 1](#T1){ref-type="table"} shows the daily average environmental factors
for 14 regions in Guangxi in 2015. The annual average temperature in Guangxi was
between 20.9°C and 25.2°C, with the temperature in the south higher than in the
north. The range of daily temperature was largest in Baise. The average daily
WIN was higher in coastal regions. In several regions, PM~2.5~ concentration was
higher than the Chinese national standard (35 µg/m^3^) for ambient air
quality.[@R41] The concentrations of CO, NO~2~ and SO~2~ in all 14 regions were
lower than the Chinese national standard for ambient air quality.[@R41]

:::: {#T1 .table-wrap} T1

::: caption Statistics for air pollutants and meteorological factors for 14
regions in Guangxi in 2015 :::

+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Regions | T | TDIFF | RHU | WIN | PM~2.5~ | SO~2~ | CO | NO~2~ | |
+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| | Mean+SD | Mean+SD | Mean+SD | Mean+SD | Mean+SD | Mean+SD | Mean+SD |
Mean+SD |
+===============+============+============+=============+============+============+============+===========+=============+
| Baise | 23.71+0.56 | 8.62+8.27 | 77.81+24.13 | 1.52+9.03 | 43.78+6.27 |
16.43+3.64 | 1.06+0.56 | 17.11+10.59 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Beihai | 25.19+0.25 | 6.70+3.74 | 80.93+23.52 | 2.45+5.76 | 29.45+5.93 |
9.05+2.44 | 1.06+0.87 | 13.98+8.61 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Chongzuo | 24.53+0.19 | 7.32+7.07 | 74.85+28.40 | 1.23+8.13 | 38.23+6.41 |
10.30+3.11 | 0.88+0.37 | 17.65+9.66 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Fangchenggang | 24.96+0.30 | 6.57+3.19 | 77.80+21.55 | 2.01+5.81 | 30.75+6.33
| 5.74+2.55 | 0.82+0.69 | 12.19+11.42 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Guigang | 23.50+0.28 | 7.12+8.63 | 82.23+28.04 | 1.13+9.09 | 41.42+6.38 |
21.73+3.12 | 1.04+0.41 | 20.13+9.14 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Guilin | 20.88+0.33 | 6.57+10.63 | 76.52+32.25 | 1.81+11.10 | 49.06+7.62 |
20.41+3.25 | 1.06+0.79 | 24.01+13.52 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Hechi | 21.87+0.40 | 7.09+19.53 | 82.22+25.49 | 1.51+9.19 | 43.92+6.76 |
23.16+3.37 | 1.30+0.58 | 20.77+11.06 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Hezhou | 21.22+0.49 | 7.83+7.19 | 82.07+26.81 | 2.31+8.94 | 39.92+7.46 |
16.11+3.63 | 1.00+0.89 | 14.86+9.96 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Laibin | 23.18+0.30 | 7.07+16.34 | 75.91+29.68 | 1.27+12.78 | 43.17+7.19 |
20.81+3.07 | 1.00+0.47 | 23.96+10.73 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Liuzhou | 22.58+0.28 | 6.77+10.92 | 76.23+32.80 | 1.44+10.7 | 49.10+7.36 |
24.20+3.00 | 1.08+0.65 | 23.43+11.1 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Nanning | 23.27+0.22 | 8.10+4.87 | 83.12+27.57 | 1.55+13.25 | 40.96+6.51 |
12.67+3.70 | 0.94+0.62 | 31.94+7.90 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Qinzhou | 23.81+0.44 | 7.63+8.03 | 83.19+25.20 | 2.06+7.68 | 35.91+6.50 |
17.21+3.36 | 1.24+0.81 | 19.38+8.42 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Wuzhou | 22.98+0.74 | 8.27+6.62 | 81.11+21.30 | 1.96+9.09 | 35.82+6.72 |
16.66+3.10 | 1.23+0.56 | 21.16+9.75 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+
| Yulin | 23.80+0.45 | 7.43+25.44 | 84.51+27.02 | 2.25+8.68 | 39.17+6.25 |
27.94+2.90 | 1.20+0.97 | 21.16+10.31 |
+---------------+------------+------------+-------------+------------+------------+------------+-----------+-------------+

CO, carbon monoxide (mg/m^3^); NO~2~, nitrogen dioxide (μg/m^3^); PM~2.5~,
particulate matter (μg/m^3^); RHU, average relative humidity percentage (%);
SO~2~, sulfur dioxide (μg/m^3^); T, daily average temperature (°C); TDIFF, daily
range of temperature (°C); WIN, average wind speed (m/s). ::::

[Figure 1](#F1){ref-type="fig"} shows the time trends of asthma hospitalisation
rates adjusted for different regions. The peak asthma hospitalisation rates
occurred in March--May and September--November, with troughs in February, July
and August ([figure 1](#F1){ref-type="fig"}). Baise, Liuzhou, Nanning and Wuzhou
had peaks in spring and autumn, while in Guilin, asthma admission rates peaked
in spring and winter. The hospital admission rates in Baise, Hechi, Liuzhou and
Fangchenggang were relatively high compared with other regions. The admission
rates in Qinzhou, Yulin and Beihai were low and their trends were similar.
Spatial heterogeneity was found in the distribution of asthma hospital
admissions. [Figure 2](#F2){ref-type="fig"} shows the time distribution of
asthma hospital admissions by age groups. The time trends of asthma in different
age groups were not consistent in different regions. The number of asthma
hospitalisations was highest in the 0--14 age group.

<figure id="F2">
F2
<p><span class="image placeholder"
data-original-image-src="bmjopen-2020-038117f02"
data-original-image-title=""></span></p>
<figcaption>Time distribution of asthma hospital admissions by age
groups in 2015.</figcaption>
</figure>

## Air pollutants and meteorological factors impact on asthma {#s3-2}

### Correlation analysis {#s3-2-1}

The correlation between air pollutants, meteorological factors and asthma
admission rates in 14 regions in Guangxi, according to the result of Spearman,
is shown in [figure 3](#F3){ref-type="fig"}. As shown, not all correlations were
statistically significant. T, TDIFF, CO and NO~2~ were correlated with asthma
admission rates in multiple regions. T was positively correlated with asthma in
Baise, Laibin and Yulin, and T was negatively correlated with asthma in Liuzhou,
Nanning, Qinzhou and Beihai. Asthma was positively correlated with TDIFF in four
regions. CO was positively correlated with asthma in four regions, and
negatively correlated with asthma in two regions. Relationship between CO and
asthma was more pronounced in central Guangxi. NO~2~ was related to asthma
admission rate in regions of eastern Guangxi. PM~2.5~ had strongly positive
correlation with asthma hospitalisation in Hechi, Qinzhou and Beihai. SO~2~ was
positively correlated with asthma admission rate only in Beihai. Average WIN was
only found to correlate with the asthma admission rate in Yulin. There did not
appear to be any correlation between the asthma admission rate and environmental
factors in Chongzuo or Hezhou.

<figure id="F3">
F3
<p><span class="image placeholder"
data-original-image-src="bmjopen-2020-038117f03"
data-original-image-title=""></span></p>
<figcaption>Correlation analysis between environmental factors and
asthma hospitalisation rates in Guangxi (2015). Environmental factors
are (A) T: daily average temperature, (B) Tdiff: daily range of
temperature, (C) RHU: daily average relative humidity percentage, (D)
WIN: daily average wind speed, (E) PM<sub>2.5</sub>: fine particles 2.5
microns or less in diameter, (F) SO<sub>2</sub>: sulfur dioxide, (G) CO:
carbon monoxide, (H) NO<sub>2</sub>: nitrogen dioxide.</figcaption>
</figure>

### Interaction analysis {#s3-2-2}

The fitting effects between air pollutants, meteorological factors and the
asthma hospitalisation rates in Guangxi are shown in
[table 2](#T2){ref-type="table"}, and the results are all statistically
significant. In 2015, the fitting effects of multiple factors on asthma
hospitalisation rates were good in Beihai, Naning, Laibin and Liuzhou, with
adjusted R^2^ values of 0.29, 0.21, 0.19 and 0.18, respectively, which meant
that environmental factors were powerful in explaining changes in asthma
hospitalisation rates in Beihai, Naning, Laibin and Liuzhou. The value of
deviance explained was 40.5% in Beihai, which indicated that the interaction
between air pollutants and meteorological factors explained 40.5% of the
variation of asthma hospitalisation in Beihai. The combined effects of
environmental factors on asthma were low in Chongzuo and Hezhou. The fitting
effects between meteorological factors, air pollutant concentrations and asthma
hospitalisation rates are shown in [figure 4](#F4){ref-type="fig"}. There were
non-linear relationships between all risk factors and asthma hospitalisation
rates, and the relationships differed from region to region. Although the
overall relationship between environmental factors and hospitalisation rates was
non-linear, some factors showed a linear relationship in certain intervals. When
PM~2.5~ concentration was high, PM~2.5~ concentration was associated with
increased risks of hospitalisation in Guilin, Liuzhou, Guigang, Yulin, Hezhou
and Laibin ([figure 4](#F4){ref-type="fig"}). When NO~2~ concentration exceeded
70 µg/m^3^, the hospitalisation rate of asthma was positively correlated with
NO~2~ in Nanning, Guilin, Liuzhou and Guigang ([figure 4](#F4){ref-type="fig"}).

<figure id="F4">
F4
<p><span class="image placeholder"
data-original-image-src="bmjopen-2020-038117f04"
data-original-image-title=""></span></p>
<figcaption>Generalised additive model for the relationships between air
pollutants, meteorological factors and asthma hospitalisation rates in
14 regions (2015). CO, carbon monoxide; DOW, day of the week; DOY, day
of the year; NO<sub>2</sub>, nitrogen dioxide; PM<sub>2.5</sub>, fine
particles 2.5 microns or less in diameter; RHU, average relative
humidity percentage; SO<sub>2</sub>, sulfur dioxide; T, daily average
temperature; TDIFF, daily range of temperature; WIN, average wind
speed.</figcaption>
</figure>

:::: {#T2 .table-wrap} T2

::: caption Interaction between air pollutants and meteorological factors on
asthma hospitalisations in 14 regions in Guangxi (2015) :::

Regions R^2^ (adj) Deviance explained (%) Regions R^2^ (adj) Deviance explained
(%)

______________________________________________________________________

Baise 0.13 29.5 Hezhou 0.03 20.4 Beihai 0.29 40.5 Laibin 0.19 26.1 Nanning 0.21
34.3 Liuzhou 0.18 31.8 Fangchenggang 0.06 21.2 Chongzuo 0.03 17.7 Guigang 0.10
23.4 Qinzhou 0.16 26.2 Guilin 0.12 27.0 Wuzhou 0.16 25.6 Hechi 0.08 21.1 Yulin
0.12 26.0

All results are significant at p\<0.01. ::::

The fitting effects between multiple environmental factors and asthma admission
rates, adjusted for age, are shown in [table 3](#T3){ref-type="table"}. The
value of deviance explained for 0--14 age group was 37.2%, which indicated that
the interaction between air pollutants and meteorological factors explained
37.2% of the variation of asthma hospitalisation. The deviance explained for the
60--74 age group was second only to 0--14 age group, with a value of 25.9%. The
fitting effects between multiple environmental factors and asthma were
relatively low for the 15--29, 30--44 and 45--59 age groups, with R^2^ values of
0.12, 0.15 and 0.14. Residents aged 0--14 with asthma may be more affected by
environmental factors than other age groups.

:::: {#T3 .table-wrap} T3

::: caption Interaction between air pollutants and meteorological factors on
asthma hospitalisations for different age groups in 2015 :::

Age groups R^2^ (adj) Deviance explained (%)

______________________________________________________________________

0--14 0.33 37.2 15--29 0.12 16.9 30--44 0.15 22.4 45--59 0.14 23.2 60--74 0.19
25.9 ≥75 0.16 21.5

All results are significant at p\<0.01. ::::

### Air pollutant exposure assessment {#s3-2-3}

[Table 4](#T4){ref-type="table"} shows the statistically significant percentage
increases of asthma hospitalisation rate for different regions with 10 µg/m^3^
increases in CO, PM~2.5~, SO~2~ and NO~2~ concentrations. In Hechi, CO had a
notable effect on asthma hospitalisation from lag0 to lag5. The strongest effect
of CO was found on lag1 in Hechi, and every 10 µg/m^3^ increase of CO caused an
increase of 25.6% in asthma hospitalisation rate (RR 1.26, 95% CI 1.02 to 1.55).
In Baise, the statistically significant effects of CO were found on lag2--lag4
and of SO~2~ were only found on lag2.

:::: {#T4 .table-wrap} T4

::: caption Percentage increases of asthma hospitalisation rate for different
regions with 10 µg/m^3^ increases in concentration of each air pollutant :::

Variables Region Lags RR (95% CI) P value

______________________________________________________________________

CO Baise lag2 1.18 (1.03 to 1.35) \<0.05 CO Baise lag3 1.17 (1.02 to 1.35)
\<0.05 CO Baise lag4 1.19 (1.04 to 1.37) \<0.05 CO Hechi lag0 1.25 (1.02 to
1.54) \<0.05 CO Hechi lag1 1.26 (1.02 to 1.55) \<0.05 CO Hechi lag2 1.25 (1.02
to 1.54) \<0.05 CO Hechi lag3 1.26 (1.02 to 1.55) \<0.05 CO Hechi lag4 1.27
(1.03 to 1.57) \<0.05 CO Hechi lag5 1.25 (1.01 to 1.54) \<0.05 SO~2~ Baise lag2
1.10 (1.00 to 1.20) \<0.05

CO, carbon monoxide; SO~2~, sulfur dioxide. ::::

# Discussion {#s4}

This study showed that there were seasonal and regional differences for asthma
admission rates in the 14 regions in Guangxi. We found evidence of spatial
heterogeneity in asthma admission rates and their relationship with
environmental factors. The hospital admission rates of asthma in the northwest
and west of Guangxi were higher than those in the east and south. The
correlation between air pollutants, meteorological factors and asthma admission
rates also differed in the 14 regions. In our study, although the overall
relationships between environmental factors and hospitalisation rates were
non-linear, some factors showed linear relationships in certain intervals. We
also found that residents between 0--14 years were particularly susceptible to
air pollutants and meteorological factors, which was consistent with previous
studies.[@R42; @R43]

There were seasonal characteristics for asthma hospitalisation rates. In the 14
regions, there were often two peaks of hospital admissions in 1 year, with the
peak hospitalisation rates occurring in spring (March--May) and autumn
(September--November), and being typically highest in spring. This is similar to
the findings of other domestic and foreign studies. Dust mites and allergens are
important factors in the induction of respiratory diseases such as
asthma.\[@R44; @R45\] More pollen and a suitable temperature for dust mites
might be the risk factors of high prevalence of asthma in spring. Based on the
result of GAM, it was found that the sensitivity of residents between 0 and 14
years old and over 60 years old to environmental factors was stronger than that
of residents 15--59 years old. The age group of 0--14 years old was most
sensitive to environmental factors, which might due to the incomplete
development of physiological structures and imperfect immune system in patients
under 14.[@R16] The sensitivity of patients over 60 years old to environmental
factors was also relatively higher than other age groups, which has been shown
in other studies, and this may be attributed to an overall decline of
physiological function.[@R16; @R17]

According to the correlation analysis, the dominant environmental factors that
affected asthma admissions were not consistent for the 14 regions. Among the
meteorological factors, temperature and daily range of temperature were highly
correlated with asthma, and the daily range of temperature was positively
correlated with asthma in Nanning, Qinzhou, Chongzuo and Wuzhou. Among the air
pollutants, PM~2.5~, NO~2~ and CO were positively correlated with asthma in
multiple regions. To our knowledge, there is no consensus among various studies
on the air pollutants that affect the onset of asthma.\[@R11; @R15; @R18; @R46;
@R47; @R48; @R49; @R50\] However, we found some similarities in the correlation
between air pollutants and asthma across different regions. In our study, CO was
positively correlated with asthma in Guigang, Hechi, Liuzhou and Nanning. In
these four regions, the daily average WIN was below 1.60 m/s and the daily
average PM~2.5~ concentration was higher than 40 µg/m^3^. In Guigang, Hechi and
Liuzhou, the daily average concentrations of CO, SO~2~ and NO~2~ were high. In
addition, PM~2.5~ was positively correlated with asthma in Hechi and Guigang.
There were some similarities in the environmental factors for Hechi and Guigang.
For both Hechi and Guigang, the daily average PM~2.5~ concentration was higher
than 40 µg/m^3^, the daily average WIN was low and the daily average RHU was
higher than 82%. Possible reasons for these findings were that specific
meteorological conditions modified the effect of air pollutants on asthma
hospitalisations.[@R12; @R13] The effect of the interaction between
meteorological factors and air pollution on asthma deserves further study.
Uniform policy interventions may not work uniformly due to regional difference
in environmental factors[@R48] ; it is essential for governments or regulatory
agencies to formulate different prevention policies for different regions,
according to specific environmental, geographical and meteorological conditions.

In our study, although the overall relationships between environmental factors
and hospitalisation rates were non-linear, some factors showed linear
relationships in certain intervals. When PM~2.5~ concentration was high, PM~2.5~
concentration was positively correlated with asthma in multiple regions. In
Nanning, Guilin, Liuzhou and Guigang, the hospitalisation rates were positively
correlated with NO~2~ when NO~2~ concentration exceeded 70 µg/m^3^. Research on
the relationship between asthma and temperature has shown that both high and low
temperatures impact the onset of asthma.[@R20; @R21; @R22; @R23; @R51] Lam *et
al* suggested that the incidence of asthma increases when the maximum
temperature is between 27°C and 30°C.[@R21] Currently, there is no consensus on
the overall relationship between environmental factors and asthma. Each factor
may be subdivided if we are to understand the details of the relationship
between these factors and asthma.

We found that CO had the greatest impact on asthma. Ho *et al* suggested that CO
is significantly related to asthma,[@R14] which is similar to our results. In
our air pollutant exposure assessment, we found that CO had a notable effect on
asthma hospitalisation from lag0 to lag5 in Hechi. The statistically significant
effects of CO were also found on lag2-- lag4 in Baise. Combining the results of
Spearman, we found that the asthma hospitalisation rate associated with CO was
significantly greater than that of NO~2~, SO~2~ and PM~2.5~ in Guangxi.

In this study, we introduced daily range of temperature as a risk factor, which
proved to be positively correlated with asthma in several regions. Dividing
factors into several intervals may help in quantifying each risk factor's impact
on asthma, and which points to the future work that needs to be done. Findings
in our study also provided evidence of air pollutants, which implied that
reducing residents from exposing to high concentrations of air pollution may
reduce risk of asthma. Limitations of this study should be acknowledged. First,
due to lack of data, we did not consider biological air pollutants in our study;
dust mites and pollen may both induce severe asthmatic responses. Second, this
study did not take into account the effects of indoor pollution and economic
factors on asthma.

# Conclusions {#s5}

The findings for this study have enhanced our understanding of the spatial
heterogeneity of asthma in terms of environmental factors. First, increased CO
concentrations exacerbate asthma. Second, correlations between environmental
factors differ significantly between regions, indicating that regulatory
measures, should also differ between regions. Third, our results suggest that,
to improve future studies, risk factors should be divided into intervals.

# References
