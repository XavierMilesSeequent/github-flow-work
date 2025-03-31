pipeline {
    agent any
    environment {
        GITHUB_BEARER_TOKEN = credentials('GITHUB_BEARER_TOKEN')
        GITHUB_REPOSITORY   = credentials('GITHUB_REPOSITORY')
    }
    stages {
        stage('Example stage 1') {
            steps {
                powershell "python run_github_action.py"
            }
        }
    }
}
