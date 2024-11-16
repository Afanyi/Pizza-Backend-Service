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

- How to change the image used in a task: 
    
- How do you start a task manually:

- The Script part of the config file - what is it good for?

- If I want a task to run for every branch I put it into the stage ??

- If I want a task to run for every merge request I put it into the stage ??

- If I want a task to run for every commit to the main branch I put it into the stage ??

# flake8 / flakeheaven

- What is the purpose of flake8?

- What types of problems does it detect

- Why should you use a tool like flake8 in a serious project?

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

- What is the purpose of GrayLog?

- What logging levels are available?

- What is the default logging level?

- Give 3-4 examples for logging commands in Python:
  ```python

  ```

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

GitLab CI/CD
1. How to delay a job until another job is done:

To delay a job until another job is completed, you can use the needs or dependencies keyword in your .gitlab-ci.yml file.

Using needs:

job1:
  stage: build
  script:
    - echo "Building..."

job2:
  stage: test
  needs: [job1]
  script:
    - echo "Testing..."
The needs keyword specifies that job2 should wait until job1 is finished, regardless of the stage they are in.

Using stages:

Organize your jobs into stages and define the order of stages:

stages:
  - build
  - test

job1:
  stage: build
  script:
    - echo "Building..."

job2:
  stage: test
  script:
    - echo "Testing..."

In this setup, all jobs in the build stage will run before any job in the test stage.

2. How to change the image used in a task:

You can specify a Docker image for a specific job using the image keyword:


job_name:
  image: python:3.9-slim
  script:
    - python --version
This tells GitLab Runner to use the python:3.9-slim Docker image when executing the job.

3. How do you start a task manually:

To make a job start manually, use the when: manual keyword:

deploy_job:
  stage: deploy
  script:
    - echo "Deploying..."
  when: manual
This configuration requires a user to manually trigger the deploy_job from the GitLab UI.

4. The Script part of the config file - what is it good for?

The script section in a job defines the shell commands that the runner will execute. It is the core of your job where you specify the steps required to build, test, or deploy your application.

Example:

test_job:
  stage: test
  script:
    - npm install
    - npm test
5. If I want a task to run for every branch I put it into the stage ??

If you want a job to run for every branch, you can use the only keyword with branches:

job_name:
  stage: test
  script:
    - echo "Running on all branches"
  only:
    - branches
By default, jobs run on all branches unless specified otherwise, so you can also omit the only keyword if you want the job to run on every branch.

6. If I want a task to run for every merge request I put it into the stage ??

To run a job for every merge request, use the only keyword with merge_requests:

job_name:
  stage: test
  script:
    - echo "Running on merge requests"
  only:
    - merge_requests
This ensures the job runs whenever a merge request is created or updated.

7. If I want a task to run for every commit to the main branch I put it into the stage ??

To run a job for every commit to the main branch, specify the branch name in the only keyword:

job_name:
  stage: deploy
  script:
    - echo "Deploying to production"
  only:
    - main
This configuration ensures the job runs only when commits are made to the main branch.

flake8 / flakeheaven
1. What is the purpose of flake8?

Flake8 is a comprehensive tool for checking the style and quality of Python code. It combines the functionality of several tools:

PyFlakes: Checks for logical errors and undefined names.
pycodestyle: Checks for PEP 8 compliance (Python's style guide).
McCabe script: Measures the cyclomatic complexity of code.
The purpose of flake8 is to enforce coding standards, detect errors, and improve code readability and maintainability.

2. What types of problems does it detect?

Flake8 detects a variety of issues, including:

Syntax errors: Invalid Python syntax that would cause a SyntaxError.
Style violations: Non-compliance with PEP 8 guidelines, such as incorrect indentation, line length exceeding 79 characters, or improper naming conventions.
Logical errors: Undefined names, unused imports, or variables.
Code complexity: High cyclomatic complexity indicating that code may be too complex and hard to maintain.
Best practices: Issues like mutable default arguments or bare except clauses.
3. Why should you use a tool like flake8 in a serious project?

Using flake8 in a serious project offers several benefits:

Improves Code Quality: By enforcing coding standards, it helps maintain a consistent codebase that's easier to read and understand.
Early Error Detection: It catches errors and potential bugs early in the development process, reducing debugging time.
Facilitates Collaboration: A consistent coding style makes it easier for multiple developers to work on the same codebase.
Enhances Maintainability: Detecting complex code sections allows you to simplify them, making future maintenance easier.
Automates Reviews: It can serve as an automated code review tool, ensuring that basic standards are met before code is merged.
