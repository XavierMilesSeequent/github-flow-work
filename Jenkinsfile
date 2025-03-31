pipeline {
    agent any
    environment {
        GITHUB_TOKEN = credentials('GITHUB_BEARER_TOKEN')
    }
    stages {
        stage('Example stage 1') {
            steps {
                powershell """
                    python -m pip install -r requirements.txt
                    python run_github_action.py
                """
            }
        }
    }
}
