# Conforma Insights Dashboard changes

## Overall

* Try your best to implement the changes such that it doesn’t become too congested on the table or the chart or the dashboard page or any other specific interaction for user to perform 

## Definitions and explanations

* Actionable exceptions  
  * Actionable exceptions should be those which are expiring within 1 week after GA  
  * These only need to be handled for the latest release, which is yet to be shipped, not for all the shipped releases  
  * We should be able to identify if there is already a jira issue open to extend the exception, the jira issue can be identified using following criteria:  
    * Should have been cloned from https://redhat.atlassian.net/browse/RHOAIENG-62569
    * Should have a label “Exception: \<full-exception-name\>”  
    * Full exception name is defined as “\<rule-value\>:\<image\>” if image is not empty else just the “\<rule-value\>”

## Help text changes

* Improve help-text and intuitiveness for all the graphs, for people to understand what’s good, what’s bad  and what needs action, specially for “Volatile Exception Expiry Timeline” chart

## Actionable exceptions changes

* Actionable exceptions changes, should be shown only for the latest release, which is yet to be shipped, not for all the shipped releases  
  * Table changes  
    * update the table in such a way that it is intuitive for users to know which exceptions require their attention and immediate action to extend the exceptions in order to be able to successfully ship the release  
    * Provide an intuitive filter which filters all the actionable exceptions  
    * The filter should be explicitly placed in front to be easily able to draw attention of users rather than hidden behind any dropdown option  
    * The filter should also automatically sort the exceptions on “days after GA” in ascending order  
    * Also provide an action link \- a hyperlink or button or image or any other control in the detailed table for all the actionable exceptions  
    * the action link should be intuitively placed such that it is clearly visible and draws attention of user to take action  
      * The action link should be shown against the qualifying exceptions irrespective of whether action filter is applied or not  
      * If there is already a jira issue opened to extend the exception, then then action link should just show the jira issue id with hyperlink on it, else it should point to following URL \- https://redhat.atlassian.net/browse/RHOAIENG-62569 from where users can clone the jira template to open jira issues to extend any exception  
      * If the jira issue has already been opened then show it somehow intuitively through some marker to differentiate from other actionable exceptions for which jira is yet to be created   
  * “Volatile Exception Expiry Timeline” chart changes  
    * Update the chart in such a way that it is intuitive for users to know which exceptions require their attention and immediate action to extend the exceptions in order to be able to successfully ship the release  
    * Provide an intuitive filter which filters all the actionable exceptions  
    * The filter should be explicitly placed in front to be easily able to draw attention of users  
    * Applying the filter should automatically zoom-in on the timeline to only show the actionable exceptions timeline  
    * The chart should provide a way to take action on the actionable exceptions  
    * How to enable users to take action is upto you how innovatively and intuitively you can embed this in the chart, one way could be to use tooltip to show the action links, but feel free to adopt other better ways  
      * Action links could be a hyperlink or button or image or any other control in the chart for all the actionable exceptions, the action mechanism should be intuitively imbibed in the chart such that it is clearly visible and draws attention of user to take action  
        * The action mechanism should be shown irrespective of whether action filter is applied or not against the qualifying exceptions  
        * If there is already a jira issue opened to extend the exception, then then action mechanism should just show the jira issue id with a way to navigate to it, else it should take user to following URL \- https://redhat.atlassian.net/browse/RHOAIENG-62569 from where users can clone the jira template to open jira issues to extend any exception  
        * If the jira issue has already been opened then show it somehow intuitively through some marker to differentiate from other actionable exceptions for which jira is yet to be created

## AI enabled analysis+categorization of exceptions 

* This should be done only for the exception of the latest release which is not shipped yet, not for all the releases  
* We should be able to analyze and categorize all the exceptions using AI in following categories:  
  * Exception is always expected and no possible way to resolve it for us  
    * Most probably all the permanent exceptions which don’t have any jira reference would automatically fall into this category, but you should analyze more before concluding this along with checking what all other exception can fall in this category  
  * Exception has any long term known resolutions which we can implement to get rid of the exception  
    * You will need to analyze the related jira issues, PRs, related repos, github issues and some docs like conforma along with your knowledge and internet knowledge to come to this conclusion  
  * Exception has any quick easy fix which can easily help us get rid of the exception  
    * You will need to analyze the related jira issues, PRs, related repos, github issues and some docs like conforma along with your knowledge and internet knowledge to come to this conclusion  
  * Cause of requiring exception is already fixed and exception is not required anymore  
    * You will need to analyze the related jira issues, PRs, related repos, github issues and some docs like conforma along with your knowledge and internet knowledge to come to this conclusion  
* You will need to use claude-code cli to perform this analysis  
* The resulting data should be shown (only for latest release which is not shipped yet)  
  * In the details table with the correct category identified, along with a short description of why the specific category was concluded for any given exception  
    * Probably we can add some filter on the top for users to be able filter based on the categories  
  * Create a new full-width chart to draw the exceptions by category  
    * Be innovative about which charts to be chosen and how to show the exceptions in most intuitive and user-friendly way  
    * Probably add an ability to filter on categories  
    * Show a short description (probably in tooltip) of why the specific category was concluded for any given exception

## Data ingestion pipeline changes

* Make sure to make all the changes which are required to support the actionable exceptions change  
* Make sure to make all the changes required for AI enabled categorization of the exceptions  
  * Look at how grand-child pipelines spawned by “trigger-onboarding-pipelines” job in the “pipeline/.gitlab-ci.yml” are deploying and utilizing claude-code cli for onboarding purpose, you can similarly deploy and run your AI prompts required to categorize the exceptions data  
  * Please make sure that claude-code is used only for this specific purpose, and does not keep running longer than this  
  * Prompt should be able to enforce the correct data structure required from the claude-code output, which can easily amalgamate with the data prepared by rest of the data-ingestion pipeline