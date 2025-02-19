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
        success {
            script {
                withCredentials([usernamePassword(credentialsId: 'git', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                    sh '''
                    commit_hash=$(git rev-parse HEAD | head -c 7)
                    branch=$(git name-rev --name-only HEAD | cut -d '/' -f 3-)
                    echo "Branch: ${branch} - Commit Hash: $commit_hash"
                    git config --global user.email "jenkins@email.santaclarautah.gov"
                    git config --global user.name "Jenkins"
                    if git rev-parse "$commit_hash" >/dev/null 2>&1; then
                        echo "Tag $commit_hash already exists. Skipping tag creation."
                    else
                        export GIT_ASKPASS=$(mktemp)
                        echo '#!/bin/sh' > \$GIT_ASKPASS
                        echo 'echo "\$GIT_PASSWORD"' >> \$GIT_ASKPASS
                        chmod +x \$GIT_ASKPASS
                        git tag -a "$commit_hash" -m "Automated Build ${commit_hash}"
                        git push origin tag "$commit_hash"
                        rm -f \$GIT_ASKPASS
                    fi
                    '''
                }
            }
        }
        fixed {
            script {
                def logLines = currentBuild.rawBuild.getLog(100).join("\n")
                emailext(
                    to: 'lhaynie@santaclarautah.gov, rlevsey@santaclarautah.gov',
                    subject: "Build Fixed: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
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