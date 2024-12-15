# Tools used in the project
The following lists the tools and frameworks, that are used in the project. 
- [Docker](https://docs.docker.com/get-started/overview/)    
   Docker is an open platform for developing, shipping, and running applications. Docker enables you to separate your applications from your infrastructure so you can deliver software quickly. With Docker, you can manage your infrastructure in the same ways you manage your applications. By taking advantage of Docker's methodologies for shipping, testing, and deploying code, you can significantly reduce the delay between writing code and running it in production.
- [Kubernetes](https://kubernetes.io/docs/concepts/overview/)
- [FastAPI](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [FastAPI with SQLAlchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)

# GitLab CI/CD

The following is a collection of short hints on how to do the most essential things in a GitLab CI/CD pipeline:

- How to delay a job until another job is done:

Use the "needs" keyword to specify the dependencies.
```yaml
job2:
  stage: test
  needs: ["job1"]
  script:
    - echo "Job 2 starts after Job 1"
```
- How to change the image used in a task: 

Specify the "image" keyword in the job definition.
```yaml
job_name:
  image: python:3.10
  script:
    - python --version
```   
- How do you start a task manually:

Use the when: manual configuration for the job.
```yaml
manual_job:
  stage: deploy
  script:
    - echo "Deploy manually"
  when: manual
```
- The Script part of the config file - what is it good for?

The script section contains the commands that the job will execute. These are the actual steps or instructions for the CI/CD pipeline.

- If I want a task to run for every branch I put it into the stage ??

To configure a GitLab CI/CD job that runs for every branch, you can use the "rules" keyword. 

```yaml
job_name: 
  stage: test
  script:
    - echo "Running on every branch"
  rules:
    - if: '$CI_COMMIT_REF_NAME'  # Runs for every branch
```
If you don't use rules, GitLab CI jobs run by default for all branches unless otherwise restricted. Restrictions can be made with the keyword "only", for example: 

```yaml
only:
    - main
    - dev    
```
- If I want a task to run for every merge request I put it into the stage ??

To run a job for every merge request, add it to the "rules" keyword.

```yaml
 rules:
    - if: '$CI_MERGE_REQUEST_ID'
```
- If I want a task to run for every commit to the main branch I put it into the stage ??
```yaml
 rules:
    - if: '$CI_COMMIT_REF_NAME == "main"'
```
# flake8 / flakeheaven

- What is the purpose of flake8?

Flake8 is a comprehensive tool for checking the style and quality of Python code. It combines the functionality of several tools:

PyFlakes: Checks for logical errors and undefined names.
pycodestyle: Checks for PEP 8 compliance (Python's style guide).
McCabe script: Measures the cyclomatic complexity of code.
The purpose of flake8 is to enforce coding standards, detect errors, and improve code readability and maintainability.

- What types of problems does it detect

Flake8 detects a variety of issues, including:

Syntax errors: Invalid Python syntax that would cause a SyntaxError.
Style violations: Non-compliance with PEP 8 guidelines, such as incorrect indentation, line length exceeding 79 characters, or improper naming conventions.
Logical errors: Undefined names, unused imports, or variables.
Code complexity: High cyclomatic complexity indicating that code may be too complex and hard to maintain.
Best practices: Issues like mutable default arguments or bare except clauses.

- Why should you use a tool like flake8 in a serious project?

Using flake8 in a serious project offers several benefits:

Improves Code Quality: By enforcing coding standards, it helps maintain a consistent codebase that's easier to read and understand.
Early Error Detection: It catches errors and potential bugs early in the development process, reducing debugging time.
Facilitates Collaboration: A consistent coding style makes it easier for multiple developers to work on the same codebase.
Enhances Maintainability: Detecting complex code sections allows you to simplify them, making future maintenance easier.
Automates Reviews: It can serve as an automated code review tool, ensuring that basic standards are met before code is merged.

## Run flake8 on your local Computer

  It is very annoying (and takes a lot of time) to wait for the pipeline to check the syntax 
  of your code. To speed it up, you may run it locally like this:

### Configure PyCharm (only once)
- find out the name of your docker container containing flake8. Open the tab *services* in PyCharm and look at the container in the service called *web*. The the name should contain the string *1337_pizza_web_dev*.  
- select _Settings->Tools->External Tools_ 
- select the +-sign (new Tool)
- enter Name: *Dockerflake8*
- enter Program: *docker*
- enter Arguments (replace the first parameter with the name of your container): 
    *exec -i NAMEOFYOURCONTAINER flakeheaven lint /opt/project/app/api/ /opt/project/tests/*
- enter Working Directory: *\$ProjectFileDir\$*

If you like it convenient: Add a button for flake8 to your toolbar!
- right click into the taskbar (e.g. on one of the git icons) and select *Customize ToolBar*
- select the +-sign and Add Action
- select External Tools->Dockerflake8

### Run flake8 on your project
  - Remember! You will always need to run the docker container called *1337_pizza_web_dev* of your project, to do this! 
    So start the docker container(s) locally by running your project
  - Now you may run flake8 
      - by clicking on the new icon in your toolbar or 
      - by selecting from the menu: Tools->External Tools->Dockerflake8 

# GrayLog

# response to the customers
failing command Issue:
The first issue, where the topping "cheeese" was not recognized, was caused by a misspelling of the word "cheese." Please note that this was not a fault on our part.

Diavolo Description Error:
The second issue occurred due to the description for the "Diavolo" topping exceeding the maximum allowable length during a database migration. We have resolved this by increasing the maximum allowable length for descriptions to 50 characters to prevent this problem from recurring in the future.

What is the purpose of GrayLog?

GrayLog is a powerful open-source log management and analysis tool that enables centralized logging. It collects, stores, and analyzes logs from various systems, servers, and applications, providing insights into system activity, troubleshooting errors, and ensuring compliance. Key features include:

    Centralized Log Management: Collect logs from multiple sources into a single location.
    Search and Analysis: Query and analyze logs in real-time using a flexible search engine.
    Alerting: Configure alerts based on specific log patterns or thresholds.
    Visualization: Create dashboards and visual reports for log data.
    Integration: Works with other tools like Elasticsearch and MongoDB for storage and analysis.

What logging levels are available?

The common logging levels in most logging systems (including GrayLog and Python's logging library) are:

    DEBUG: Detailed information for diagnosing problems.
    INFO: General operational messages that highlight the system's progress.
    WARNING: Indication of a potential problem or non-critical issue.
    ERROR: Logs error events that might still allow the system to continue running.
    CRITICAL: Logs severe errors that likely lead to system failure.

What is the default logging level?

The default logging level for many systems, including Python’s logging library, is WARNING. This means only logs at the level of WARNING, ERROR, and CRITICAL will be captured unless the logging configuration is explicitly changed.
Examples of logging commands in Python

Below are some examples of logging commands in Python using the logging module:

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Logging examples
logging.debug("This is a DEBUG message")  # Detailed diagnostic information
logging.info("This is an INFO message")   # General operational information
logging.warning("This is a WARNING message")  # Non-critical issues
logging.error("This is an ERROR message")  # Errors that might affect the operation
logging.critical("This is a CRITICAL message")  # Severe errors, system may crash

# SonarQube

- What is the purpose of SonarQube?

- What is the purpose of the quality rules of SonarQube?

- What is the purpose of the quality gates of SonarQube?


## Run SonarLint on your local Computer

It is very annoying (and takes a lot of time) to wait for the pipeline to run SonarQube. 
To speed it up, you may first run the linting part of SonarQube (SonarLint) locally like this:

### Configure PyCharm for SonarLint (only once)

- Open *Settings->Plugins*
- Choose *MarketPlace*
- Search for *SonarLint* and install the PlugIn

### Run SonarLint

- In the project view (usually to the left) you can run the SonarLint analysis by a right click on a file or a folder. 
  You will find the entry at the very bottom of the menu.
- To run it on all source code of your project select the folder called *app*

# VPN

The servers providing Graylog, SonarQube and your APIs are hidden behind the firewall of Hochschule Darmstadt.
From outside the university it can only be accessed when using a VPN.
https://its.h-da.io/stvpn-docs/de/ 

# SonarQube Bug Resolution Documentation

This document outlines the identified SonarQube issues and their resolutions, adhering to agile documentation practices for quick reference and continuous improvement.

---

## 1. Error When Specifying Only One Parameter

- **Issue**: A method call was causing an error due to a missing parameter when only one argument was provided.
- **Resolution**: Added the missing parameter `db` to the method signature to ensure all required arguments are supplied.

---

## 2. Error with the 'as' Keyword

- **Issue**: Syntax error caused by the use of lowercase `as` in a SQL statement.
- **Resolution**: Changed `as` to uppercase `AS` to correct the SQL syntax, ensuring proper keyword recognition.

---

## 3. Repeated String Literal

- **Issue**: Multiple occurrences of the same string literal were found, violating the DRY (Don't Repeat Yourself) principle.
- **Resolution**: Introduced a constant variable to hold the repeated string value and replaced all instances with this constant to enhance maintainability.

---

## 4. Hardcoded Password in Source Code

- **Issue**: Direct inclusion of username and password in the source code posed a security risk.
- **Resolution**: Replaced hardcoded credentials with randomly generated values and implemented secure credential management using environment variables or a secrets manager.

---

## 5. Error When Removing Cache After Installing Packages

- **Issue**: An error occurred due to residual cache files after package installation, affecting image size and security.
- **Resolution**: Added `rm -rf /var/lib/apt/lists/*` and RUN pip install --user --no-cache-dir poetry
 at the end of the package installation command to remove the cache and reduce the final image size.

---

## 6. Error with Test Coverage

- **Issue**: SonarQube reported an error related to insufficient test coverage.
- **Resolution**: Issue was acknowledged but deprioritized due to current resource constraints and will be addressed in future sprints.

---

## 7. Unresolved Security Hotspot

- **Issue**: SonarQube identified a security hotspot that couldn't be mitigated with the existing codebase.
- **Resolution**: Documented the risk for future review. The issue is currently accepted as a known limitation until a feasible solution is found.

---
##8. Security Issue: automountServiceAccountToken Should Be Set to False
Issue: SonarQube flagged a security issue where automountServiceAccountToken is not set to false in the Kubernetes deployment YAML. By default, Kubernetes mounts a service account token into pods, which may pose a security risk if the application does not require access to the Kubernetes API.
Resolution: Updated the Kubernetes YAML specification to set automountServiceAccountToken to false to prevent unnecessary mounting of service account tokens, enhancing pod security.

##9. Resource Limits: Memory Limit Not Specified
Issue: SonarQube identified that the container lacks specified resource limits, which can lead to uncontrolled resource consumption and affect cluster stability.
Resolution: Added a memory limit to the container specification in the Kubernetes YAML to enforce resource constraints.



