import json
import re
from datetime import datetime


def parse_teams_alert(teams_alert):
    """
    Parses a Microsoft Teams alert to extract Lambda failure details.
    Assumes alert format from AWS SNS -> Teams webhook.
    """
    try:
        # Case 1: Alert is JSON (structured payload)
        if isinstance(teams_alert, dict):
            alert_data = teams_alert
        else:
            alert_data = json.loads(teams_alert)

        # Extract from AWS SNS -> Teams format
        sns_message = json.loads(alert_data['text'])
        lambda_name = sns_message.get('Trigger', {}).get('Dimensions', [{}])[0].get('value')
        error_time = sns_message.get('StateChangeTime')
        error_msg = sns_message.get('AlarmDescription', 'No error message')

        # Case 2: Fallback to regex if unstructured text
        if not lambda_name:
            matches = re.search(
                r'Lambda function (.+?) failed at (.+?)\. Error: (.+)',
                teams_alert
            )
            if matches:
                lambda_name, error_time, error_msg = matches.groups()

        return {
            'lambda_function_name': lambda_name,
            'error_time': datetime.strptime(error_time, '%Y-%m-%dT%H:%M:%S.%fZ'),
            'error_message': error_msg
        }

    except Exception as e:
        raise ValueError(f"Alert parsing failed: {str(e)}")

if __name__ == "__main__":
    # Example Teams alert payload
    teams_alert = {
        "text": '{"AlarmName":"LambdaFailure","AlarmDescription":"TimeoutError","StateChangeTime":"2024-05-20T14:30:00.000Z","Trigger":{"Dimensions":[{"name":"FunctionName","value":"my-lambda-function"}]}}'
    }

    # Parse the alert
    parsed_alert = parse_teams_alert(teams_alert)
    print(parsed_alert)