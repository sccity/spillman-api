pipeline {
    agent {
        kubernetes {
            label "${env.JOB_NAME}-${BUILD_NUMBER}"
            containerTemplate {
                name 'jnlp'
                image 'sccity/jenkins-agent-python:0.0.3'
            }
        }
    }

    stages {
        stage('Build') {
            steps {
                container('jnlp') {
                    sh '''
                    python3.10 -m venv venv
                    . venv/bin/activate
                    pip3.10 install -r requirements.txt
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                container('jnlp') {
                    sh '''
                    . venv/bin/activate
                    python3.10 app.py
                    '''
                }
            }
        }
    }

    post {
        failure {
            script {
                def logLines = currentBuild.rawBuild.getLog(100).join("\n")
                emailext(
                    to: 'lhaynie@santaclarautah.gov, rlevsey@santaclarautah.gov',
                    subject: "Build Failed: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                    body: """
                        <strong>Project:</strong> ${env.JOB_NAME}<br>
                        <strong>Build Number:</strong> ${env.BUILD_NUMBER}<br>
                        <strong>Result:</strong> ${currentBuild.currentResult}<br>
                        <strong>URL:</strong> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a><br><br>
                        <strong>Last 100 lines of build log:</strong>
                        <pre>${logLines}</pre>
                        """,
                    mimeType: 'text/html'
                )
            }
        }
    }
}