import csv
import subprocess
import time

class ZoweCLI:
    """
    A class used to encapsulate the functionality of the Zowe CLI.

    ...

    Attributes
    ----------
    host : str
        the hostname of the z/OS system
    port : str
        the port number of the z/OS system
    user : str
        the username for the z/OS system
    password : str
        the password for the z/OS system

    Methods
    -------
    run_command(command)
        Runs a Zowe CLI command with the connection parameters.
    submit_jcl(jcl_name)
        Submits a JCL and returns the job ID.
    get_job_status(job_id)
        Returns the status of a job.
    get_output_code(job_id)
        Returns the output code of a job.
    get_job_logs(job_id)
        Returns the logs of a job.
    send_email(email, subject, body)
        Sends an email with a subject and a body.
    """

    def __init__(self, host="default_host", port="default_port", user="default_user", password="default_password"):
        """
        Constructs all the necessary attributes for the ZoweCLI object.

        Parameters
        ----------
            host : str
                the hostname of the z/OS system
            port : str
                the port number of the z/OS system
            user : str
                the username for the z/OS system
            password : str
                the password for the z/OS system
        """

        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def run_command(self, command):
        """
        Runs a Zowe CLI command with the connection parameters.

        Parameters
        ----------
            command : str
                the Zowe CLI command to run

        Returns
        -------
            result : CompletedProcess
                the result of the command
        """

        full_command = f"{command} --host {self.host} --port {self.port} --user {self.user} --password {self.password} --reject-unauthorized false"
        result = subprocess.run(full_command.split(), capture_output=True, text=True)
        return result

    def submit_jcl(self, jcl_name):
        """
        Submits a JCL and returns the job ID.

        Parameters
        ----------
            jcl_name : str
                the name of the JCL to submit

        Returns
        -------
            job_id : str
                the job ID, or None if the JCL does not exist
        """

        result = self.run_command(f"zowe jobs submit data-set {jcl_name}")
        if "DATA_SET_NOT_FOUND" in result.stderr:
            return None
        job_id = result.stdout.strip()
        return job_id

    def get_job_status(self, job_id):
        """
        Returns the status of a job.

        Parameters
        ----------
            job_id : str
                the job ID

        Returns
        -------
            status : bool
                True if the job is complete, False otherwise
        """

        result = self.run_command(f"zowe jobs view job-status-by-jobid {job_id}")
        return "STATUS: OUTPUT" in result.stdout

    def get_output_code(self, job_id):
        """
        Returns the output code of a job.

        Parameters
        ----------
            job_id : str
                the job ID

        Returns
        -------
            output_code : str
                the output code
        """

        result = self.run_command(f"zowe jobs view rc-for-jobid {job_id}")
        output_code = result.stdout.split(" ")[-1].strip()
        return output_code

    def get_job_logs(self, job_id):
        """
        Returns the logs of a job.

        Parameters
        ----------
            job_id : str
                the job ID

        Returns
        -------
            logs : str
                the logs
        """

        result = self.run_command(f"zowe jobs view sfbi {job_id} 103")
        return result.stdout

    def send_email(self, email, subject, body):
        """
        Sends an email with a subject and a body.

        Parameters
        ----------
            email : str
                the email address to send the email to
            subject : str
                the subject of the email
            body : str
                the body of the email
        """

        email_command = f"echo '{body}' | mail -s '{subject}' {email}"
        subprocess.run(email_command, shell=True)

def main():
    zowe_cli = ZoweCLI()

    with open('input.csv', 'r') as file:
        reader = csv.reader(file)
        jcls = list(reader)

    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["JCL Name", "Output Code", "JCL Pass/Fail", "Email Sent"])

        for jcl in jcls:
            jcl_name = jcl[0]
            email = jcl[1]

            job_id = zowe_cli.submit_jcl(jcl_name)
            if job_id is None:
                writer.writerow([jcl_name, "N/A", "Fail", "No"])
                continue

            while not zowe_cli.get_job_status(job_id):
                time.sleep(5)

            output_code = zowe_cli.get_output_code(job_id)
            logs = zowe_cli.get_job_logs(job_id)
            zowe_cli.send_email(email, "JCL Execution Logs", logs)

            writer.writerow([jcl_name, output_code, "Pass" if output_code == "0000" else "Fail", "Yes"])

if __name__ == "__main__":
    main()
