from io import BytesIO
import os
import re
import sys
import time
import uuid
import zipfile

import github
import requests

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_USER = "XavierMilesSeequent"
GITHUB_REPO = "github-flow-work"
BUILD_SCRIPTS_WORKFLOW_NAME = "run_ui_tests.yml"

ANSI_ESCAPE_REGEX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')



def parse_log_line(line: str) -> str:
    try:
        line = ANSI_ESCAPE_REGEX.sub('', line)
        return line.split(' ', maxsplit=1)[1]
    except IndexError:
        return ''


def build_dependencies_github_workflow():
    auth = github.Auth.Token(GITHUB_TOKEN)
    gh = github.Github(auth=auth)
    org = gh.get_user(GITHUB_USER)
    build_scripts_repo = org.get_repo(GITHUB_REPO)
    build_scripts_workflow = build_scripts_repo.get_workflow(BUILD_SCRIPTS_WORKFLOW_NAME)

    triggering_branch = "main"  # os.environ["TRIGGERING_BRANCH"]
    inputs = {
        'jenkins_trigger_id': str(uuid.uuid4()),
    }
    workflow_run, workflow_job = trigger_dependencies_workflow_run(
        triggering_branch,
        inputs,
        build_scripts_workflow,
    )
    monitor_status(workflow_run, workflow_job)
    get_workflow_run_logs(workflow_run)


def trigger_dependencies_workflow_run(
    triggering_branch: str, workflow_inputs: dict, workflow: github.Workflow
) -> github.WorkflowRun:
    print("GitHub Workflow Run Initialization:")
    # Kick off a workflow run
    workflow_run_created = workflow.create_dispatch(triggering_branch, inputs=workflow_inputs)
    if not workflow_run_created:
        raise RuntimeError("Failed to create workflow run")

    # Get the workflow run we just created - not always created instantly so have a few attempts at it
    workflow_run = None
    attempts = 0
    while not workflow_run and attempts <= 20:  # 20 attempts == 5 minutes
        time.sleep(15)
        runs = workflow.get_runs()[:10]
        workflow_run = find_workflow_run(runs, workflow_inputs['jenkins_trigger_id'])
        if not workflow_run:
            attempts += 1
            print("Couldn't find the workflow run. Retrying...")
        else:
            print(f"Workflow run found. \nURL Link: {workflow_run.html_url} \nStatus: {workflow_run.status}")
            workflow_job = next(job for job in workflow_run.jobs() if job.name == "Job 1")
    return workflow_run, workflow_job


def monitor_status(workflow_run: github.Workflow, workflow_job: github.WorkflowJob):
    # Monitor the status and wait for the workflow to complete
    print("GitHub Workflow Run Monitoring:")
    poll_status_step(workflow_job)
    while workflow_run.conclusion is None:
        time.sleep(5)
        workflow_run.update()
    print(f"Status: {workflow_run.status}")
    print(f"Workflow run completed: {workflow_run.conclusion}")


def get_workflow_run_logs(workflow_run):
    # Get the raw logs from the workflow run
    print("GitHub Workflow Run Logs:")
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    resp = requests.get(workflow_run.logs_url, headers=headers)
    resp.raise_for_status()
    content = resp.content
    logs_zip = zipfile.ZipFile(BytesIO(content), 'r')
    log_file_name = next((f for f in logs_zip.namelist() if "/" not in f and "run build scripts" in f), None)
    assert log_file_name, "Log file not found"
    log_file = logs_zip.open(log_file_name)
    block_name_queue = []
    error_catcher = []
    for line in log_file.readlines():
        line = f"{parse_log_line(line.decode())}"
        if line.startswith("##[error]"):
            error_catcher.append(line.split("##[error]")[1])
            # tc_logger.error(line)
        elif line.startswith("##[group]"):
            block_name = line.split("##[group]")[1]
            block_name_queue.append(block_name)
            # tc_logger.teamcity_service_messages.blockOpened(block_name)
        elif line.startswith("##[endgroup]") and block_name_queue:
            block_name = block_name_queue.pop()
            # tc_logger.teamcity_service_messages.blockClosed(block_name)
        # elif m := re.match(r'##teamcity\[(\w+) timestamp=\'[^ ]+\'(.*)]', line):
        #     msg = ''.join(m.groups())
            # tc_logger.teamcity_service_messages.message(msg)
        # else:
            # tc_logger.info(line)
        print(line)

    if workflow_run.conclusion == "failure":
        print("Workflow run failed\nPlease check the logs for more information")
        if len(error_catcher) > 0:
            print(f"Errors: {error_catcher}\n")
        sys.exit(1)


def poll_status_step(job):
    for step_index, step in enumerate(job.steps):
        print(f"Step: {step.name}...", end=" ")
        while True:
            step = job.steps[step_index]
            if step.conclusion:
                break
            time.sleep(10)
            job.update()
        print(f"{step.conclusion}")


def find_workflow_run(runs, run_id):
    for run in runs:
        try:
            job = run.jobs()[0]  # Sometimes the run exists but the job hasn't been created yet
        except IndexError:
            continue
        for step in job.steps:
            if step.name == f"Run Identifier {run_id}":
                return run
    return None


if __name__ == "__main__":
    build_dependencies_github_workflow()
