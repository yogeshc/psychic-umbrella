# Zowe CLI Python Script

This Python script uses the Zowe CLI to interact with a z/OS system. It reads a CSV file with JCL names and email addresses, submits the JCLs, checks the job status, gets the output code, gets the job logs, sends the emails, and writes the results to an output CSV file.

## Requirements

- Python 3
- Zowe CLI
- mail command (for sending emails)

## Usage

1. Update the connection parameters in the ZoweCLI class constructor.
2. Update the input and output CSV file names in the main function.
3. Run the script with Python 3.

## Input CSV File Format

The input CSV file should have two columns:

- JCL Name: the name of the JCL to submit
- Email: the email address to send the job logs to

## Output CSV File Format

The output CSV file has four columns:

- JCL Name: the name of the JCL
- Output Code: the output code of the job
- JCL Pass/Fail: "Pass" if the output code is "0000", "Fail" otherwise
- Email Sent: "Yes" if the email was sent, "No" otherwise
