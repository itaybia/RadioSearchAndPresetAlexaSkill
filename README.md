## RadioSearchAndPresetAlexaSkill

VERSION v1.0 11/01/2018

***********************************

This is the code for an Alexa skill that allows you to search through TuneIn radio for radio stations based on artist (stations that are related to him), genre or a general query.
The skill also allows the user to save radio station presets and call them with the preset number instead of the full name.
This skill requires no third party devices to run a server. everything runs on AWS using lambda.

## Getting Started with RadioSearchAndPresetAlexaSkill

The guide below was mostly copied from this link https://developer.amazon.com/alexa-skills-kit/alexa-skill-quick-start-tutorial. I recommend using both, Amazon's has screen shots.

## Step 1 (Create the IAM policy and role for the save preset feature access permissions)

#### Creating the IAM policies for the Lambda function:

1. Navigate to IAM in your management console: https://console.aws.amazon.com/iam/home#/roles
2. Select "Policies" in the sidebar.
3. Click "Create Policy".
4. Select "Create Your Own Policy".
5. Enter an appropriate policy name and description like "update_env_variables".
    * The code uses lambda's environment variables to store the presets and to change them. This is not ideal, but is easier to implement.
6. Paste the contents of [\AlexaSkillKit_Code\policy.txt](https://github.com/itaybia/RadioSearchAndPresetAlexaSkill/blob/master/AlexaSkillKit_Code/policy.txt)
7. Click "Create Policy".
8. Select "Create Your Own Policy".
9. Enter policy name "lambda_logging"
10. Paste the contents of [\AlexaSkillKit_Code\logs_policy.txt](https://github.com/itaybia/RadioSearchAndPresetAlexaSkill/blob/master/AlexaSkillKit_Code/logs_policy.txt)

#### Creating the IAM role for the Lambda function:
1. Select "Role" in the sidebar.
2. Click "Create New Role".
3. Enter an appropriate role name ("radiosearch_presets") and click "Next Step".
4. Select "AWS Lambda" within the AWS Service Roles.
5. Change the filter to "Customer Managed", check the box of the 2 policies you created above, and click "Next Step".
6. Click "Create Role".


## Step 2 (Create your AWS Lambda function that your skill will use)

1. Download or clone my RadioSearchAndPresetAlexaSkill github project https://github.com/itaybia/RadioSearchAndPresetAlexaSkill
2. If you do not already have an account on AWS, go to Amazon Web Services and create an account.
3. Log in to the AWS Management Console and navigate to AWS Lambda.
4. Click the region drop-down in the upper-right corner of the console and select either **US East (N. Virginia)** or **EU (Ireland)**.
Lambda functions for Alexa skills must be hosted in either the **US East (N. Virginia)** or **EU (Ireland)** region.
5. If you have no Lambda functions yet, click **Get Started Now**. Otherwise, click **Create a Lambda Function**.
6. Enter a name for the lambda function. "radiosearch" or "radiopresets" for example.
7. Under Runtime, select **Python 2.7**.
8. Select "choose an existing role", and below that select the role you created in Step 1.
9. Add an "Alexa skills kit" trigger.
10. Notice the ARN written on the top right of the page. We'll call it **LAMBDA_ARN**. It should be something like: arn:aws:lambda:<zone>-1:#:function:wiwo.
11. Click the name of your lambda function (from step 2.6 above). Under the **Lambda function** code section (leave as **Edit code inline** and then copy in my code.
The code can be found under [\AlexaSkillKit_Code\lambda_function.py](https://github.com/itaybia/RadioSearchAndPresetAlexaSkill/blob/master/AlexaSkillKit_Code/lambda_function.py)
You will need to edit some variables in the code.
    * **CHECK_APP_ID**: true if you want to add security and allow the function to be used only from your alexa skill, according to the ALEXA_SKILL_APP_ID below.
    * **ALEXA_SKILL_APP_ID**: if CHECK_APP_ID is true, then this ID will be matched against intent for this lambda function. You will be able to fill it after we create the skill in step 3.
    * **RADIO_SEARCH_LAMBDA_ID**: fill this with the LAMBDA_ARN mentioned in step 2.10
12. Right-click on the left side just below "lambda_function.py" and add a new file. Call it: "tunein.py". then copy in my code from
 [\AlexaSkillKit_Code\tunein.py](https://github.com/itaybia/RadioSearchAndPresetAlexaSkill/blob/master/AlexaSkillKit_Code/tunein.py)
13. Right-click on the left side just below "lambda_function.py" and add a new file. Call it: "radiosearch_tunein.py". then copy in my code from
 [\AlexaSkillKit_Code\radiosearch_tunein.py](https://github.com/itaybia/RadioSearchAndPresetAlexaSkill/blob/master/AlexaSkillKit_Code/radiosearch_tunein.py)
14. You can test your function by using the **Configure test event**. Change the name of **Hello World** as needed and paste the contents of any of the relevant xml files found in [\AlexaSkillKit_Code](https://github.com/itaybia/RadioSearchAndPresetAlexaSkill/blob/master/AlexaSkillKit_Code) and then **Save** and **Test**.
    * You should probably set **CHECK_APP_ID** in the lambda function to **False** to test this. At least until you create the Alexa skill and have the actual App ID.
15. If you'd like, you can set the preset stations directly yourself by editing the **Environment variables**. Two entries should be added per preset station:
    1. URL:
        * **Key** = PresetX_URL
        * **Value** = \<URL of stream. Notice it has to be in a secure HTTPS form\>.
    2. Name:
        * **Key** = PresetX_Station_Name
        * **Value** = \<Station name as you'd like it to be spoken by Alexa\>.
    * example:
        * URL:
            * **Key** = Preset2_URL
            * **Value** = https://opml.radiotime.com/Tune.ashx?id=s234168
        * Name:
            * **Key** = Preset2_Station_Name
            * **Value** = Indie experience


## Step 3 (Create your Alexa Skill and link your Lambda function)

1. Sign in to the **Amazon developer portal**. If you haven't done so already, you'll need to create a free account. https://developer.amazon.com/edw/home.html#/
2. From the top navigation bar, select **Alexa**.
3. Under **Alexa Skills Kit**, choose **Get Started >**.
4. Choose **Add a New Skill**.
5. Name your skill. This is the name displayed to users in the Alexa app. RadioSearch, Radio Presets, are all good choices.
6. Create an invocation name. This is the word or phrase that users will speak to activate the skill. Something like my radio, preset radio, presets.
7. Set **Audio Player** under the global fields to **Yes**.
8. Click **Save**.
9. Choose **Next** to continue to development of the new skill.
10. In the **Intent Schema** box, paste the JSON code from [\AlexaSkillKit_Code\IntentSchema.txt](https://github.com/itaybia/RadioSearchAndPresetAlexaSkill/blob/master/AlexaSkillKit_Code/IntentSchema.txt)
11. Skip over the **Custom Slot Types** section.
12. Under **Sample Utterances** paste in contents of [\AlexaSkillKit_Code\Utterances.txt](https://github.com/itaybia/RadioSearchAndPresetAlexaSkill/blob/master/AlexaSkillKit_Code/Utterances.txt)
13. Choose **Next** and wait until the interaction model finishes loading, in no more than a few seconds
14. Select the Endpoint AWS Lambda ARN then paste your LAMBDA_ARN code from step 2.10. Then choose Next.
15. Under **Service Simulator** you can test the skill.  Write what you would have said to alexa to operate the skill. Logs can be found here https://console.aws.amazon.com/cloudwatch
16. There is no need to Publish the skill.


************
#### Examples:

* "Alexa, Tell INVOCATION_NAME to search artist pearl jam"
* "Alexa, Tell INVOCATION_NAME to play genre jazz"
* "Alexa, Tell INVOCATION_NAME to find psytrance"
* "Alexa, Tell INVOCATION_NAME to play preset 4"
* "Alexa, Tell INVOCATION_NAME to save to preset 4"
* "Alexa, Tell INVOCATION_NAME to delete preset 4"
