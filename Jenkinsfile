pipeline {
    agent any
    environment {
        GITHUB_TOKEN = credentials('GITHUB_BEARER_TOKEN')
    }
    stages {
        stage('Example stage 1') {
            steps {
                powershell "python -m pip install -r requirements.txt"
                script {
                    artifact_download_url = powershell(returnStdout: true, script: "python run_github_action.py").trim()
                }
                powershell """
                \$Headers = @{
                    'Authorization: Bearer $GITHUB_TOKEN'
                    'Accept' = 'application/vnd.github.v3+json'
                }
                Invoke-WebRequest -Uri $artifact_download_url -Headers $Headers -OutFile 'artifact.zip'
                """
            }
        }
    }
}
