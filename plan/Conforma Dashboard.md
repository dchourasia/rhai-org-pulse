# Conforma Dashboard

Objective:

* We need to create a dashboard with various charts showing various perspectives of the policy exceptions approved for our product shipping for various released versions  
* We also need to create a gitlab-ci pipeline which keeps pushing the data to data/ai-impact/ regularly using CRON schedule 

Overall:

* Only prepare and show the data starting 22nd May 2025, not before that, make this date configurable  
* Product name is rhoai or RHOAI  
* Make sure we adopt the existing patterns for authentication, security, deployment and technical stack used in this application

Background

* We have few policy yamls listing the exceptions approved for our product shipment   
  * https://gitlab.cee.redhat.com/releng/konflux-release-data/-/blob/main/config/stone-prod-p02.hjvn.p1/product/EnterpriseContractPolicy/fbc-rhoai-prod.yaml
  * https://gitlab.cee.redhat.com/releng/konflux-release-data/-/blob/main/config/stone-prod-p02.hjvn.p1/product/EnterpriseContractPolicy/registry-rhoai-prod.yaml
* We use conforma standards for our exception policy, more details can be found in the conforma docs https://conforma.dev/docs/policy/release_policy.html#_available_rule_collections
* Details of our shipping schedule of various releases is found in a smartsheet which needs to be scrapped for more details https://app.smartsheet.com/sheets/rRgRc8jPQpQPfJpqvJwf3M6fXJvRpFhqhWXgHpW1?view=grid

Data 

* Releases:  
  * We need to scrap the shipping schedule data from the given smartsheet using API and python library using the API token  
  * Release versions are of the format rhoai-2.y or rhoai-3.y or rhoai-2.y.z or rhoai-3.y.z or rhoai-3.y.EA1 or rhoai-3.y EA2, this can be found in the “shortname” column of the smartsheet  
  * Each version has 2 important event dates to scrap \- Code Freeze date and GA date, each specified in independent smartsheet rows for each releases separately  
    * Each event start and end date is written in corresponding rows in the “Start” and “Finish” columns, we should consider only finish date as the event date  
  *   
* Conforma exceptions  
  * We should explore history of the policy yaml files from the gitlab repo  
  * We need to find the snapshot of the policies yamls right before the GA date for a release  
  * Then analyze that snapshot and store it as a the policy exceptions used for that particular release  
  * We need to do this analysis for all the shipped versions of RHOAI based on the data received from the smartsheet  
* We need to prepare a detailed exceptions data for each shipped RHOAI version to be able to show it in various charts

Charts

* We need to create another section named “Conforma Exceptions” below the “Component Breakdown” section under the “Release Analysis” section in the leftbar  
* The objective of charts to be able to show various graphs grouped on possible categories  
* Keep a choice dropdown on the top with list of all the shipped RHOAI versions in the descending order of their GA date,   
  * all the below graphs and tables should only show the data for the selected RHOAI version in the dropdown  
* Be innovative about designing these charts and we can have number of them to be able to show the concise summary of exceptions for each release  
* You are free to devise multiple charts to show the analysis with more insights in various ways, so feel free to innovate more such charts as needed  
* Also have a detailed table at the end listing all the exceptions for each released version with all of its possible details in columns

Data ingestion:

* Make sure to have a dedicated folder in the project for all the files related to this pipeline  
* We need to create a gitlab-ci pipeline which will run externally based on a cron schedule  
* It will fetch all the required details for all the releases and exceptions  
* It will use backend APIs of the application to update the data in the data/release-analysis/ dir on the server to have the analysis of various RHOAI releases  
  * Make sure to have a clean update of the data each time, and should not result into any duplicate or missing data  
* Use the existing pattern of how release analysis data is being stored