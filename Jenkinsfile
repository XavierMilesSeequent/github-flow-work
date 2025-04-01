pipeline {
    agent any
    environment {
        GITHUB_TOKEN = credentials('GITHUB_BEARER_TOKEN')
    }
    stages {
        stage('Example stage 1') {
            steps {
                // This will install them to whichever Python is in the PATH on Jenkins
                powershell "python -m pip install -r requirements.txt"
                script {
                    def artifact_download_url = powershell(returnStdout: true, script: "python run_github_action.py").trim()
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
}
