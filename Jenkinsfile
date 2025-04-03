pipeline {
    agent any
    environment {
        GITHUB_TOKEN = credentials('GITHUB_BEARER_TOKEN')
    }
    stages {
        stage('Example stage 1') {
            steps {
                sh """
                # Setup Python environment
                python -m venv venv
                . venv/bin/activate
                python -m pip install -r requirements.txt

                # Remove old artifacts
                rm -rf artifact-contents
                """
                echo "Github branch: $BRANCH_NAME"
                script {
                    def artifact_download_url = sh(returnStdout: true, script: """
                    . venv/bin/activate
                    python run_github_action.py
                    """).trim()
                    echo "Artifact download URL: ${artifact_download_url}"
                    sh """
                    curl \
                        ${artifact_download_url} -L \
                        -H "Authorization: Bearer $GITHUB_TOKEN" \
                        -H "Accept: application/vnd.github.v3+json" \
                        -o artifact.zip

                    unzip 'artifact.zip' -d './artifact-contents'
                    """
                }
                publishCtrfResults('artifact-contents/ctrf-report.json')
            }
        }
    }
}
